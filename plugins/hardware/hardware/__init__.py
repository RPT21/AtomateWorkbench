# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/__init__.py
# Compiled at: 2005-06-10 18:51:18
import traceback, lib.kernel.plugin, plugins.hardware.hardware.actions as hardware_actions
import wx, plugins.hardware.hardware.hardwaremanager as hardwaremanager, plugins.ui.ui as ui
import threading, time, plugins.poi.poi.operation as operation
import logging, plugins.hardware.hardware.images as images
import plugins.poi.poi as poi
import plugins.poi.poi.actions
logger = logging.getLogger('hardware')
PLUGIN_ID = 'hardware'
EVT_START_EXITING_ID = wx.NewId()

def EVT_START_EXITING(win, func):
    win.Connect(-1, -1, EVT_START_EXITING_ID, func)


class StartExitingEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_START_EXITING_ID)


EVT_KILL_IT_ID = wx.NewId()

def EVT_KILL_IT(win, func):
    win.Connect(-1, -1, EVT_KILL_IT_ID, func)


class KillItEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_KILL_IT_ID)


class ResponseTimeoutException(Exception):
    __module__ = __name__

    def __init__(self, msg):
        Exception.__init__(self, msg)


ID_SHOW_HARDWAREEDITOR = wx.NewId()

def EVT_SHOW_HARDWARE_EDITOR(win, func):
    win.Connect(-1, -1, ID_SHOW_HARDWAREEDITOR, func)


class ShowHardwareEditorEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(ID_SHOW_HARDWAREEDITOR)


class HardwarePlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        lib.kernel.plugin.Plugin.__init__(self)
        self.initializeThreads = []
        self.initializeThreadDlg = None
        self.shutdownThreads = []
        self.shutdownThreadDlg = None
        self.initializeLock = threading.Condition()
        ui.getDefault().setSplashText('Loading Hardware plugin ...')
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        ui.getDefault().addCloseListener(self)
        hardwaremanager.init()
        images.init(contextBundle)

    def closing(self):
        self.internalClose()
        return False

    def internalClose(self):
        self.cancelableShutdownHardware()

    def getHardwareToInitialize(self):
        hardwares = []
        for description in hardwaremanager.getHardware():
            hwinst = description.getInstance()
            try:
                initialize = description.getConfiguration().get('main', 'startupinit').lower() == 'true'
                if initialize:
                    hardwares.append(description.getInstance())
            except Exception as msg:
                pass

        return hardwares

    def handlePartInit(self, part):
        if not isinstance(part, ui.UIPlugin):
            return
        ui.getDefault().removeInitListener(self)
        toolsManager = ui.getDefault().getMenuManager().findByPath('atm.tools')
        toolsManager.appendToGroup('tools-additions-begin', poi.actions.ActionContributionItem(hardware_actions.OpenHardwareManagerAction()))
        self.createHardwareInstances()
        hardwares = self.getHardwareToInitialize()
        frame = ui.getDefault().getMainFrame().getControl()
        accel = poi.actions.acceleratortable.frames[frame]
        accel.addEntry((wx.ACCEL_CTRL | wx.ACCEL_ALT, ord('h'), ID_SHOW_HARDWAREEDITOR))

        def doOpen(event):
            hardware_actions.openHardwareEditor()

        frame.Bind(wx.EVT_MENU, doOpen, id=ID_SHOW_HARDWAREEDITOR)

        if len(hardwares) > 0:
            self.cancelableInitializeHardware(hardwares)

    def createHardwareInstances(self):
        """Initialize all hardware configured for startup"""
        logger.debug('Initializing startup hardware')
        for description in hardwaremanager.getHardware():
            hwTypeID = description.getHardwareType()
            hwType = hardwaremanager.getHardwareType(hwTypeID)
            instance = hwType.getInstance()
            instance.setDescription(description)
            initialize = False
            try:
                initialize = description.getConfiguration().get('main', 'startupinit').lower() == 'true'  # description.getConfiguration()['main']._options() per veure les opcions
            except Exception as msg:
                logger.exception(msg)
                logger.warning('No startupinit tag in description')

            hardwaremanager.fireHardwareManagerUpdated()
            if not initialize:
                continue

    def xcancelableShutdownHardware(self):
        t = threading.Thread()
        t.run = self.caca
        t.start()

    def cancelableShutdownHardware(self):

        class ShutdownWithProgressRunner(operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                logger.debug('Starting ...')
                failed = False
                for description in hardwaremanager.getHardware():
                    hwinst = description.getInstance()
                    if hwinst.getStatus() == hardwaremanager.STATUS_RUNNING:
                        try:
                            hwinst.shutdown()
                        except Exception as msg:
                            logger.exception(msg)
                            failed = True

                try:
                    logger.debug('Calling hardware manager shutdown')
                    hardwaremanager.shutdown()
                    logger.debug('Finalizing')
                except Exception as msg:
                    logger.exception(msg)

        f = ui.invisibleFrame
        dlg = plugins.poi.poi.dialogs.progress.ProgressDialog(f)
        runner = ShutdownWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as msg:
            traceback.print_exc()

        ui.invisibleFrame.Close()

    def cancelableInitializeHardware(self, hardwares):

        class InitializeWithProgressRunner(operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                logger.debug('Starting ...')
                monitor.beginTask('Initializing all hardware', len(hardwares))
                done = False
                hwinst = None
                monitor.endTask()

                class CancelListener(threading.Thread):
                    __module__ = __name__

                    def run(innerself):
                        while not done:
                            if monitor.isCanceled() and hwinst is not None:
                                logger.debug('Cancel detected')
                                hwinst.interruptOperation()
                            logger.debug('Iteration')
                            time.sleep(0.25)

                        return

                cancellistener = None
                failed = False
                for hwinst in hardwares:
                    logger.debug("Going to initialize '%s'" % hwinst)
                    if cancellistener is None:
                        logger.debug('Creating cancel listener')
                        cancellistener = CancelListener()
                        cancellistener.start()
                    try:
                        monitor.subTask("Initializing '%s'" % hwinst.getDescription().getName())
                        if hwinst.getStatus() == hardwaremanager.STATUS_RUNNING:
                            monitor.worked(1)
                        hwinst.initialize()
                        logger.debug('Done initializing %s' % str(hwinst))
                        monitor.worked(1)
                    except Exception as msg:
                        logger.exception(msg)
                        failed = True

                done = True
                if failed:
                    logger.debug('Failed to initialize')
                return

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)
        runner = InitializeWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as msg:
            traceback.print_exc()

        logger.debug('Done')
