# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/__init__.py
# Compiled at: 2004-11-30 03:01:31
import lib.kernel, logging, lib.kernel.plugin, lib.kernel.boot, lib.kernel.splash, threading, wx, copy, os, sys
import plugins.ui.ui.messages as messages, plugins.ui.ui.images as images
import plugins.ui.ui.context as context
import plugins.ui.ui.preferences as preferences
import plugins.ui.ui.splash as splash
import plugins.ui.ui.undomanager as undomanager
import plugins.ui.ui.mainframe as mainframe
import plugins.poi.poi as poi
from plugins.ui.ui.actions import ExitAction
import plugins.poi.poi.actions.statusbarmanager as statusbarmanager
import plugins.poi.poi.actions.toolbarmanager as toolbarmanager
import plugins.poi.poi.actions.menumanager as menumanager
import configparser

MB_FILE = 'atm.file'
MB_EDIT = 'atm.edit'
MB_HELP = 'atm.help'
MB_TOOLS = 'atm.tools'
VIEW_CHANGE_TYPE_ADDED = 1
VIEW_CHANGE_TYPE_REMOVED = 2
PLUGIN_ID = 'ui'
MEMENTO_FILENAME = '.memento'
logger = logging.getLogger('ui')
invisibleFrame = None

def dumpThreads():
    global logger
    logger.debug('Dumping threads')
    logger.debug('----------------------------')
    logger.debug('TOTAL THREADS: %d' % threading.active_count())
    for thread in threading.enumerate():
        logger.debug('\tTHREAD: %s - %s' % (str(thread), thread.name))


class UIApp(wx.App):
    __module__ = __name__

    def OnInit(self):
        return True


def getDefault():
    global default
    return default


class UIPlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global default
        lib.kernel.plugin.Plugin.__init__(self)
        self.mainFrame = None
        self.app = None
        self.ctx = None
        self.initListeners = []
        self.viewProviders = {}
        self.viewListeners = []
        self.closeListeners = []
        self.closeVetoListeners = []
        self.toolbarManager = None
        self.statusBarManager = None
        default = self
        return

    def addViewListener(self, listener):
        if not listener in self.viewListeners:
            self.viewListeners.append(listener)

    def removeViewListener(self, listener):
        if listener in self.viewListeners:
            self.viewListeners.remove(listener)

    def fireViewChange(self, changeType, viewID):
        list(map((lambda p: p.viewChanged(changeType, viewID)), self.viewListeners))

    def addCloseVetoListener(self, listener):
        if not listener in self.closeVetoListeners:
            self.closeVetoListeners.append(listener)

    def removeCloseVetoListener(self, listener):
        if listener in self.closeVetoListeners:
            self.closeVetoListeners.remove(listener)

    def fireCloseVetoRequest(self):
        """Returns True if it should veto it, false otherwise"""
        for listener in self.closeVetoListeners:
            if listener.closeVeto():
                return True

        return False

    def addCloseListener(self, listener):
        if not listener in self.closeListeners:
            self.closeListeners.append(listener)

    def removeCloseListener(self, listener):
        if listener in self.closeListeners:
            self.closeListeners.remove(listener)

    def fireCloseEvent(self):
        listeners = copy.copy(self.closeListeners)
        proceed = True
        for listener in listeners:
            if not listener.closing():
                proceed = False

        return proceed

    def registerViewProvider(self, viewID, provider):
        if not viewID in self.viewProviders:
            self.viewProviders[viewID] = provider

    def createView(self, sectorID, viewID):
        global VIEW_CHANGE_TYPE_ADDED
        logger.debug('CREATE VIEW: %s %s IN THREAD %s' % (sectorID, viewID, threading.current_thread()))
        if not viewID in self.viewProviders:
            raise Exception("No view provider registered for '%s'" % viewID)
        self.getMainFrame().createView(sectorID, self.viewProviders[viewID], viewID)
        self.fireViewChange(VIEW_CHANGE_TYPE_ADDED, viewID)

    def removeView(self, viewID):
        global VIEW_CHANGE_TYPE_REMOVED
        self.getMainFrame().removeView(viewID)
        self.fireViewChange(VIEW_CHANGE_TYPE_REMOVED, viewID)

    def addInitListener(self, listener):
        if not listener in self.initListeners:
            self.initListeners.append(listener)

    def removeInitListener(self, listener):
        if listener in self.initListeners:
            self.initListeners.remove(listener)

    def firePartInit(self):
        listeners = copy.copy(self.initListeners)
        for listener in listeners:
            try:
                listener.handlePartInit(self)
            except Exception as msg:
                logger.error("Handle part init exception: '%s'" % msg)
                logger.exception(msg)

    def startup(self, contextBundle):
        self.ctx = contextBundle
        lib.kernel.splash.increment('Loading User Interface ...')
        lib.kernel.boot.addBootSequenceListener(self)
        self.createApp()
        messages.init(contextBundle)
        images.init(contextBundle)
        self.bringUpSplash()
        preferences.init()
        undomanager.init()

    def bringUpSplash(self):
        self.splash = splash.SplashPage(None)
        self.splash.show()
        self.setSplashText('Loading UI plugin ...')
        return

    def bringDownSplash(self):
        self.splash.startTimeout()
        self.splash = None
        return

    def setSplashText(self, text):
        if self.splash is None:
            return
        self.splash.setStatus(text)
        return

    def getContextBundle(self):
        return self.ctx

    def bootSequenceComplete(self):
        lib.kernel.boot.removeBootSequenceListener(self)
        self.createUI()
        self.restoreLayout()
        self.mainFrame.show()
        self.firePartInit()
        self.setSplashText('')
        self.bringDownSplash()
        self.startApp()

    def createApp(self):
        global invisibleFrame
        logger.debug('Create App')
        invisibleFrame = wx.Frame(None, -1, '')
        context.init()
        return

    def startApp(self):
        lib.kernel.splash.bringdown()

    def getToolBarManager(self):
        return self.toolbarManager

    def getMenuManager(self):
        return self.menuManager

    def getStatusBarManager(self):
        return self.statusBarManager

    def createUI(self):
        self.statusBarManager = statusbarmanager.StatusBarManager('#STATUSBAR')
        self.toolbarManager = toolbarmanager.ToolBarManager(None, '#TOOLBAR')
        mm = menumanager.MenuManager(None, '#MENUBAR')
        fileManager = self.createFileMenuManager()
        editManager = self.createEditMenuManager()
        toolsManager = self.createToolsMenuManager()
        viewManager = self.createViewMenuManager()
        helpManager = self.createHelpMenuManager()
        mm.addItem(fileManager)
        mm.addItem(editManager)
        mm.addItem(poi.actions.GroupMarker('mb-additions-begin'))
        mm.addItem(poi.actions.GroupMarker('mb-additions-end'))
        mm.addItem(toolsManager)
        mm.addItem(viewManager)
        mm.addItem(helpManager)
        tbm = self.toolbarManager
        tbm.addItem(poi.actions.Separator('edit-actions-begin'))
        tbm.addItem(poi.actions.Separator('edit-actions-end'))
        tbm.addItem(poi.actions.Separator('tb-additions-begin'))
        tbm.addItem(poi.actions.Separator('tb-additions-end'))
        self.menuManager = mm
        self.mainFrame = mainframe.MainFrame()
        self.registerFrameEvents()
        mm.createMenuBar(self.mainFrame.getControl())
        self.toolbarManager.createControl(self.mainFrame.getControl())
        self.statusBarManager.createControl(self.mainFrame.getControl())
        return

    def registerFrameEvents(self):
        control = self.mainFrame.getControl()
        control.Bind(wx.EVT_CLOSE, self.OnClose)

    def internalOnExit(self):
        dumpThreads()
        self.saveLayout()
        self.fireCloseEvent()
        self.mainFrame.dispose()
        dumpThreads()
        logger.debug('Exiting')
        sys.exit(0)

    def exit(self):
        self.mainFrame.close()

    def OnClose(self, event):
        if not event.CanVeto():
            self.internalOnExit()
            event.Skip()
            return
        if self.fireCloseVetoRequest():
            event.Veto()
            return
        event.Skip()
        self.internalOnExit()

    def createFileMenuManager(self):
        global MB_FILE
        fileManager = menumanager.MenuManager(messages.get('mainmenu.file'), MB_FILE)
        fileManager.addItem(poi.actions.GroupMarker('file-additions-begin'))
        fileManager.addItem(poi.actions.Separator('file-additions-end'))
        exitAction = ExitAction()
        fileManager.addItem(poi.actions.ActionContributionItem(exitAction))
        return fileManager

    def createEditMenuManager(self):
        mng = poi.actions.menumanager.MenuManager(messages.get('mainmenu.edit'), 'atm.edit')
        mng.addItem(poi.actions.ActionContributionItem(undomanager.UNDO_ACTION))
        mng.addItem(poi.actions.ActionContributionItem(undomanager.REDO_ACTION))
        mng.addItem(poi.actions.Separator())
        mng.addItem(poi.actions.GlobalActionContributionItem('global.edit.cut', messages.get('editmenu.cut'), enabledImage=images.getImage(images.ENABLED_EDIT_CUT), disabledImage=images.getImage(images.DISABLED_EDIT_CUT)))
        mng.addItem(poi.actions.GlobalActionContributionItem('global.edit.copy', messages.get('editmenu.copy'), enabledImage=images.getImage(images.ENABLED_EDIT_COPY), disabledImage=images.getImage(images.DISABLED_EDIT_COPY)))
        mng.addItem(poi.actions.GlobalActionContributionItem('global.edit.paste', messages.get('editmenu.paste'), enabledImage=images.getImage(images.ENABLED_EDIT_PASTE), disabledImage=images.getImage(images.DISABLED_EDIT_PASTE)))
        mng.addItem(poi.actions.GroupMarker('edit-additions-begin'))
        mng.addItem(poi.actions.GroupMarker('edit-additions-end'))
        return mng

    def createViewMenuManager(self):
        mng = poi.actions.menumanager.MenuManager(messages.get('mainmenu.views'), 'atm.views')
        mng.addItem(poi.actions.GroupMarker('views-additions-end'))
        return mng

    def createToolsMenuManager(self):
        mng = poi.actions.menumanager.MenuManager(messages.get('mainmenu.tools'), 'atm.tools')
        mng.addItem(poi.actions.ActionContributionItem(actions.PreferencesAction()))
        mng.addItem(poi.actions.Separator('tools-additions-begin'))
        mng.addItem(poi.actions.GroupMarker('tools-additions-end'))
        return mng

    def createHelpMenuManager(self):
        mng = poi.actions.menumanager.MenuManager(messages.get('mainmenu.help'), 'atm.help')
        mng.addItem(poi.actions.ActionContributionItem(actions.AboutAction()))
        mng.addItem(poi.actions.GroupMarker('help-additions-begin'))
        mng.addItem(poi.actions.GroupMarker('help-additions-end'))
        return mng

    def getMemento(self):
        global MEMENTO_FILENAME
        global PLUGIN_ID
        wp = lib.kernel.getPluginWorkspacePath(PLUGIN_ID)
        try:
            config = configparser.RawConfigParser()
            config.read([os.path.join(wp, MEMENTO_FILENAME)])
        except Exception as msg:
            logger.exception(msg)
            logger.error('* ERROR: Cannot create memento file:')
            return None

        return config

    def restoreLayout(self):
        memento = None
        try:
            memento = self.getMemento()
        except Exception as msg:
            logger.error("Memento exception: '%s'" % msg)
            logger.exception(msg)

        self.mainFrame.restoreLayout(memento)
        return

    def saveLayout(self):
        wp = lib.kernel.getPluginWorkspacePath(PLUGIN_ID)
        config = configparser.RawConfigParser()
        self.mainFrame.saveLayout(config)
        try:
            f = open(os.path.join(wp, MEMENTO_FILENAME), 'w')
            config.write(f)
            f.close()
        except Exception as msg:
            logger.error("Could not save memento: '%s'" % msg)
            logger.exception(msg)

    def getMainFrame(self):
        """Return the applciation top frame"""
        return self.mainFrame


# global MB_EDIT ## Warning: Unused global
