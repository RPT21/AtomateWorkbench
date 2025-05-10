# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/__init__.py
# Compiled at: 2005-06-10 18:51:18
import traceback, kernel.plugin, kernel.pluginmanager as PluginManager, hardware.actions, poi.actions, wx, hardware.hardwaremanager, ui, threading, time, poi.operation, poi.dialogs.progress, poi.actions.acceleratortable, logging, hardware.images as images
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


class HardwarePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
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
        hardware.hardwaremanager.init()
        images.init(contextBundle)

    def closing(self):
        self.internalClose()
        return False

    def internalClose(self):
        self.cancelableShutdownHardware()

    def getHardwareToInitialize(self):
        hardwares = []
        for description in hardware.hardwaremanager.getHardware():
            hwinst = description.getInstance()
            try:
                initialize = description.getConfiguration().get('main', 'startupinit').lower() == 'true'
                if initialize:
                    hardwares.append(description.getInstance())
            except Exception, msg:
                pass

        return hardwares

    def handlePartInit(self, part):
        if not isinstance(part, ui.UIPlugin):
            return
        ui.getDefault().removeInitListener(self)
        toolsManager = ui.getDefault().getMenuManager().findByPath('atm.tools')
        toolsManager.appendToGroup('tools-additions-begin', poi.actions.ActionContributionItem(hardware.actions.OpenHardwareManagerAction()))
        self.createHardwareInstances()
        hardwares = self.getHardwareToInitialize()
        frame = ui.getDefault().getMainFrame().getControl()
        accel = poi.actions.acceleratortable.frames[frame]
        accel.addEntry((wx.ACCEL_CTRL | wx.ACCEL_ALT, ord('h'), ID_SHOW_HARDWAREEDITOR))

        def doOpen(event):
            hardware.actions.openHardwareEditor()

        wx.EVT_MENU(frame, ID_SHOW_HARDWAREEDITOR, doOpen)
        if len(hardwares) > 0:
            self.cancelableInitializeHardware(hardwares)

    def createHardwareInstances(self):
        """Initialize all hardware configured for startup"""
        logger.debug('Initializing startup hardware')
        for description in hardware.hardwaremanager.getHardware():
            hwTypeID = description.getHardwareType()
            hwType = hardware.hardwaremanager.getHardwareType(hwTypeID)
            instance = hwType.getInstance()
            instance.setDescription(description)
            initialize = False
            try:
                initialize = description.getConfiguration().get('main', 'startupinit').lower() == 'true'
            except Exception, msg:
                logger.exception(msg)
                logger.warn('No startupinit tag in description')

            hardware.hardwaremanager.fireHardwareManagerUpdated()
            if not initialize:
                continue

    def xcancelableShutdownHardware(self):
        t = threading.Thread()
        t.run = self.caca
        t.start()

    def cancelableShutdownHardware(self):

        class ShutdownWithProgressRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                logger.debug('Starting ...')
                failed = False
                for description in hardware.hardwaremanager.getHardware():
                    hwinst = description.getInstance()
                    if hwinst.getStatus() == hardware.hardwaremanager.STATUS_RUNNING:
                        try:
                            hwinst.shutdown()
                        except Exception, msg:
                            logger.exception(msg)
                            failed = True

                try:
                    logger.debug('Calling hardware manager shutdown')
                    hardware.hardwaremanager.shutdown()
                    logger.debug('Finalizing')
                except Exception, msg:
                    logger.exception(msg)

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        runner = ShutdownWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception, msg:
            traceback.print_exc()

        ui.invisibleFrame.Close()

    def cancelableInitializeHardware(self, hardwares):

        class InitializeWithProgressRunner(poi.operation.RunnableWithProgress):
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
                        if hwinst.getStatus() == hardware.hardwaremanager.STATUS_RUNNING:
                            monitor.worked(1)
                        hwinst.initialize()
                        logger.debug('Done initializing %s' % str(hwinst))
                        monitor.worked(1)
                    except Exception, msg:
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
        except Exception, msg:
            traceback.print_exc()

        logger.debug('Done')
