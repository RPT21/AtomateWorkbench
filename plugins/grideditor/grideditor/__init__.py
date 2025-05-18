# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/__init__.py
# Compiled at: 2004-12-08 01:13:43
import os, plugins.help, lib.kernel as kernel, lib.kernel.plugin, wx, logging
import plugins.ui.ui.preferences, plugins.core.core, plugins.core.core.recipe, plugins.core.core.preferencesstore
import plugins.ui.ui.context, plugins.poi.poi.views, plugins.poi.poi.actions, configparser
import plugins.grideditor.grideditor.images as grideditor_images
import plugins.grideditor.grideditor.recipegridviewer as grideditor_recipegridviewer
import plugins.grideditor.grideditor.executiongridviewer as grideditor_executiongridviewer
import plugins.grideditor.grideditor.preferences as grideditor_preferences
import plugins.grideditor.grideditor.messages as grideditor_messages
import plugins.grapheditor.grapheditor as grapheditor
import plugins.grideditor.grideditor.utils as grideditor_utils
import plugins.panelview.panelview as panelview
import plugins.resources.resources as resources
import plugins.grideditor.grideditor.utils.validation as grideditor_validation
import plugins.grideditor.grideditor.autosaver as autosaver, threading
import plugins.grideditor.grideditor.utils.errorviewer as grideditor_errorviewer
import plugins.grideditor.grideditor.actions as grideditor_actions, plugins.resources.resources.version
import plugins.grideditor.grideditor.recipemodel as grideditor_recipemodel
import plugins.ui.ui as ui
import plugins.poi.poi as poi
import plugins.core.core as core
import plugins.validator.validator as validator
import plugins.extendededitor.extendededitor as extendededitor
from plugins.resourcesui.resourcesui.actions import openRecipeVersion
import plugins.resourcesui.resourcesui.actions

CONFIG_FILENAME = '.config'
PLUGIN_ID = 'grideditor'
VIEW_ID = 'grideditor'
columnContributions = {}
logger = logging.getLogger('grideditor')

def getDefault():
    global instance
    return instance


def getActiveEditor():
    return instance


def addColumnContributionFactory(name, contributionFactory):
    global columnContributions
    if not name in columnContributions:
        columnContributions[name] = contributionFactory


def removeColumnContributionFactory(name):
    if name in columnContributions:
        del columnContributions[name]


def getColumnContributionFactory(name):
    if name in columnContributions:
        return columnContributions[name]


class DebugRemoveEditorAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Debug Hide Editor', '', '')

    def run(self):
        global VIEW_ID
        result = ui.getDefault().getMainFrame().findView(VIEW_ID)
        if result is None:
            ui.getDefault().createView('center', VIEW_ID)
        else:
            ui.getDefault().getMainFrame().clearSector(result[1])
        return


ID_SHOW_RUNPERSPECTIVE = wx.NewId()

def EVT_SHOW_RUN_PERSPECTIVE(win, func):
    win.Connect(-1, -1, ID_SHOW_RUNPERSPECTIVE, func)


class ShowRunPerspectiveEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(ID_SHOW_RUNPERSPECTIVE)


ID_SHOW_GRIDEDITOR = wx.NewId()

def EVT_SHOW_GRID_EDITOR(win, func):
    win.Connect(-1, -1, ID_SHOW_GRIDEDITOR, func)


class ShowGridEditorEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(ID_SHOW_GRIDEDITOR)


class GridEditorPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        instance = self
        self.recipeModel = None
        self.viewer = None
        self.config = configparser.RawConfigParser()
        self.colors = {'invalidcell': (wx.RED), 'highlight': (wx.BLUE)}
        return

    def getInvalidCellColor(self):
        return self.colors['invalidcell']

    def getHighlightStepColor(self):
        return self.colors['highlight']

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        ui.getDefault().addCloseListener(self)
        grideditor_messages.init(contextBundle)
        grideditor_images.init(contextBundle)
        ui.context.addContextChangeListener(self)
        grideditor_utils.validation.init()
        self.setupHelp()
        self.setupPreferencesStore()
        self.autosaver = autosaver.AutoSaver()

    def validationEvent(self, valid, errors):
        pass

    def setupHelp(self):
        pass

    def closing(self):
        """fired by ui when closing"""
        global logger
        validator.getDefault().removeValidationListener(self)
        self.autosaver.stop()
        try:
            self.saveConfiguration()
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to save configuration: '%s'" % self.getConfigurationFilename())

        logger.debug('Saving recipe ...')
        grideditor_utils.saveCurrentRecipe()

    def getDefaultPreferences(self):
        config = configparser.RawConfigParser()
        self.fillDefaultPreferences(config)
        return config

    def fillDefaultPreferences(self, config):
        config.add_section('editor')
        config.set('editor', 'tab-acquires-previous', 'true')
        config.set('editor', 'autosaveinterval', '1')
        config.set('editor', 'colors.invalidcell', '1,1,0')
        config.set('editor', 'colors.highlight', '133,133,218')

    def createDefaultPreferences(self):
        config = self.preferencesStore.getPreferences()
        self.fillDefaultPreferences(config)
        self.preferencesStore.commit()

    def sanityCheck(self):
        """Checks configuration for normal values"""
        prefs = self.preferencesStore.getPreferences()
        if self.preferencesStore.isNew():
            self.createDefaultPreferences()
        try:
            if not prefs.has_section('editor'):
                prefs.add_section('editor')
            ivs = int(prefs.get('editor', 'autosaveinterval'))
            if ivs < 0:
                ivs = 0
            prefs.set('editor', 'autosaveinterval', str(ivs))
        except Exception as msg:
            logger.exception(msg)

        self.preferencesStore.commit()

    def setupPreferencesStore(self):
        global PLUGIN_ID
        preferencesStore = core.preferencesstore.PreferencesStore(PLUGIN_ID)
        self.preferencesStore = preferencesStore
        self.sanityCheck()
        preferencesStore.setDefaultPreferences(self.getDefaultPreferences())
        ui.preferences.getDefault().addPage(grideditor_preferences.PreferencesPage(preferencesStore))
        self.preferencesStore.addPreferencesStoreListener(self)
        self.cacheColorPrefs()

    def cacheColorPrefs(self):
        prefs = self.preferencesStore.getPreferences()
        try:
            self.colors['invalidcell'] = grideditor_utils.parseColorOption(prefs.get('editor', 'colors.invalidcell'))
            self.colors['highlight'] = grideditor_utils.parseColorOption(prefs.get('editor', 'colors.highlight'))
        except Exception as msg:
            logger.warning('No valid colors. Defaulting')

        if self.viewer is not None:
            self.viewer.update()
        return

    def preferencesStoreChanged(self, store):
        self.cacheColorPrefs()
        self.viewer.preferencesChanged()

    def getPreferencesStore(self):
        return self.preferencesStore

    def getRecipeModel(self):
        return self.recipeModel

    def contextChanged(self, event):
        self.internalContextChanged(event)

    def internalContextChanged(self, event):
        key = event.getKey()
        value = event.getNewValue()
        if key == 'recipe':
            if value is not None:
                if event.getOldValue() is not None:
                    if event.getNewValue().getUnderlyingResource().equals(event.getOldValue().getUnderlyingResource()):
                        return
                    oldvalue = event.getOldValue()
                    oldvalue.dispose()
                recipe = event.getNewValue()
                recipeModel = grideditor_recipemodel.RecipeModel()
                recipeModel.setRecipe(recipe)
                self.recipeModel = recipeModel
                logger.debug('Adding stuffs %s' % threading.current_thread())
                (view, where) = ui.getDefault().getMainFrame().findView(VIEW_ID)
                if view is None:
                    ui.getDefault().createView('center', VIEW_ID)
                    ui.getDefault().createView('south', plugins.panelview.panelview.VIEW_ID)
                    ui.getDefault().createView('east', extendededitor.VIEW_ID)
                    ui.getDefault().createView('west', grapheditor.VIEW_ID)
                mainframe = ui.getDefault().getMainFrame()
                (view, where) = mainframe.findView(VIEW_ID)
                editor = view.getViewer()
                editor.setInput(recipeModel)
                (view, where) = mainframe.findView(extendededitor.VIEW_ID)
                view.getViewer().setEditor(editor)
                (view, where) = mainframe.findView(grapheditor.VIEW_ID)
                view.getViewer().setEditor(editor)
                validator.getDefault().setupRecipe(None, recipeModel)
            elif event.getOldValue() is None:
                return
            (view, where) = ui.getDefault().getMainFrame().findView(VIEW_ID)
            ui.getDefault().removeView(VIEW_ID)
            ui.getDefault().removeView(grapheditor.VIEW_ID)
            ui.getDefault().removeView(extendededitor.VIEW_ID)
            ui.getDefault().removeView(plugins.panelview.panelview.VIEW_ID)
            self.recipeModel = None
            validator.getDefault().setupRecipe(None, None)
            grideditor_actions.handleActionContextChange(value, event.getOldValue())
        return

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)
        ui.getDefault().registerViewProvider(VIEW_ID, self)
        grideditor_errorviewer.init()
        frame = ui.getDefault().getMainFrame().getControl()
        accel = poi.actions.acceleratortable.frames[frame]
        accel.addEntry((wx.ACCEL_CTRL | wx.ACCEL_ALT, ord('1'), ID_SHOW_GRIDEDITOR))

        def doOpen(event):
            ui.getDefault().getMainFrame().showPerspective('edit')

        frame.Bind(wx.EVT_MENU, doOpen, id=ID_SHOW_GRIDEDITOR)
        accel.addEntry((wx.ACCEL_CTRL | wx.ACCEL_ALT, ord('2'), ID_SHOW_RUNPERSPECTIVE))

        def doOpen(event):
            ui.getDefault().getMainFrame().showPerspective('run')

        frame.Bind(wx.EVT_MENU, doOpen, id=ID_SHOW_RUNPERSPECTIVE)
        self.restorePreviousRecipe()

    def restorePreviousRecipe(self):
        configpath = self.getLocalConfigurationFilename()
        try:
            f = open(configpath, 'r')
            self.config.read_file(f)
            f.close()
        except Exception as msg:
            logger.warning("Unable to open configuration: '%s'" % configpath)

        projectName = None
        versionNumber = None
        shared = False
        try:
            projectName = self.config.get('main', 'projectname')
            versionNumber = int(self.config.get('main', 'versionnumber'))
            shared = self.config.get('main', 'shared').lower() == 'true'
        except Exception as msg:
            logger.exception(msg)
            logger.debug('No previous recipe specified')
            return

        if projectName is None:
            return
        workspace = plugins.resources.resources.getDefault().getWorkspace()
        project = workspace.getProject(projectName, shared)
        project.load()
        version = workspace.getRecipeVersion(project, plugins.resources.resources.version.getVersionWithNumber(versionNumber))
        version.load()
        openRecipeVersion(version)
        return

    def xclosing(self):
        pass

    def getConfigurationFilename(self):
        global CONFIG_FILENAME
        return os.path.join(lib.kernel.getPluginWorkspacePath(PLUGIN_ID), CONFIG_FILENAME)

    def getLocalConfigurationFilename(self):
        return os.path.join(lib.kernel.getLocalSite(), CONFIG_FILENAME)

    def saveConfiguration(self):
        configpath = self.getLocalConfigurationFilename()
        if not self.config.has_section('main'):
            self.config.add_section('main')
        projectName = ''
        versionNumber = ''
        shared = False
        recipe = ui.context.getProperty('recipe')
        if recipe is not None:
            version = recipe.getUnderlyingResource()
            project = version.getProject()
            projectName = project.getName()
            versionNumber = str(version.getNumber())
            shared = project.isShared()
        self.config.set('main', 'projectname', projectName)
        self.config.set('main', 'versionnumber', versionNumber)
        self.config.set('main', 'shared', shared)
        f = open(configpath, 'w')
        self.config.write(f)
        f.close()
        return

    def getEditor(self):
        return self.viewer

    def createView(self, viewID, parent):
        """Create the view"""

        class SwappableWindow(wx.Window):
            """Only one guy can be visible at a time"""
            __module__ = __name__

            def __init__(self, parent):
                wx.Window.__init__(self, parent, -1)
                self.Bind(wx.EVT_SIZE, self.OnSize)

            def OnSize(self, event):
                event.Skip()
                self.resizeActiveWindow()

            def show(self, child):
                if not child in self.GetChildren():
                    return
                for kid in self.GetChildren():
                    kid.Show(child == kid)

                self.activeWindow = child
                if not wx.IsMainThread():
                    wx.CallAfter(self.resizeActiveWindow)
                else:
                    self.resizeActiveWindow()

            def resizeActiveWindow(self):
                if len(self.GetChildren()) == 0:
                    return
                if self.activeWindow is None:
                    self.activeWindow = self.GetChildren()[0]
                size = self.GetSize()
                self.activeWindow.SetSize(size)
                self.activeWindow.SetPosition((0, 0))
                self.activeWindow.Refresh()
                return

            def x__del__(self):
                lib.kernel.debugDumpStack()
                logger.debug('****** DEL *******')

        class SomeView(poi.views.SectorView):
            __module__ = __name__

            def createControl(self, parent):
                self.control = SwappableWindow(parent)

                def closelistener(event):
                    event.Skip()
                    logger.debug('CLOSE LISTENER')
                    lib.kernel.debugDumpStack()

                wx.EVT_CLOSE(self.control, closelistener)
                viewer = grideditor_recipegridviewer.RecipeGridViewer()
                viewer.createControl(self.control)
                self.control.show(viewer.getControl())
                self.viewer = viewer
                return self.control

            def showGridEditorView(self, show):
                if show:
                    self.control.show(self.viewer.getControl())
                    self.viewer.show(True)
                grideditor_actions.updateActions()

            def setFocus(self, focus):
                self.viewer.setFocus(focus)

            def getId(self):
                return viewID

            def getViewer(self):
                return self.viewer

            def dispose(self):
                logger.debug('DISPOSE CALLED')
                self.viewer.dispose()

        view = SomeView()
        self.view = view
        view.createControl(parent)
        self.viewer = view.viewer
        return view

    def getView(self):
        return self.view
