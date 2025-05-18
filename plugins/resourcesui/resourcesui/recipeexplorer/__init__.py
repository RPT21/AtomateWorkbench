# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/__init__.py
# Compiled at: 2004-11-20 00:28:57
import wx, logging, wx.adv
import plugins.resourcesui.resourcesui.actions as resourcesui_actions
import plugins.resourcesui.resourcesui.recipeexplorer.snapshotview as recipeexplorer_snapshotview
import plugins.resourcesui.resourcesui.recipeexplorer.recipesview as recipeexplorer_recipesview
import plugins.resourcesui.resourcesui.recipeexplorer.actions as recipeexplorer_actions
import plugins.resourcesui.resourcesui.recipeexplorer.versionsview as recipeexplorer_versionsview
import plugins.resourcesui.resourcesui.recipeexplorer.runlogsview as recipeexplorer_runlogsview
import plugins.resourcesui.resourcesui.recipeexplorer.snapshotview, plugins.resources.resources as resources
import plugins.poi.poi.actions.toolbarmanager, plugins.poi.poi.actions.statusbarmanager
import plugins.poi.poi.dialogs, plugins.poi.poi.views, plugins.resourcesui.resourcesui.messages as messages
import plugins.resources.resources.version, plugins.resources.resources.project
import plugins.poi.poi as poi

logger = logging.getLogger('resources.ui')
DIALOG_PREFS_FILE = 'recipeexplorer.prefs'


class RecipeExplorer(poi.dialogs.Dialog):
    __module__ = __name__

    def __init__(self):
        poi.dialogs.Dialog.__init__(self)
        self.control = None
        self.setSaveLayout(True)
        self.counts = 0
        self.setStyle(wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        resources.getDefault().getWorkspace().addWorkspaceChangeListener(self)
        return

    def handleClosing(self, id):
        resources.getDefault().getWorkspace().removeWorkspaceChangeListener(self)

    def workspaceChanged(self, event):
        resource = event.getRoot()
        selection = self.getView('recipes').getViewer().getSelection()
        if len(selection) == 0:
            return
        selection = selection[0]
        if isinstance(resource, resources.version.RecipeVersion):
            project = resource.getProject()
            if not selection.equals(project):
                return
            self.updateVersions(project)
        elif isinstance(resource, resources.project.Project):
            self.updateRecipes()
        elif isinstance(resource, resources.project.RunLog):
            pass

    def updateRunlogs(self, selection):
        self.views['runlogs'].showRunLogs(selection)

    def updateRecipes(self):
        self.getView('recipes').getViewer().setInput(resources.getDefault().getWorkspace())

    def performLayout(self):
        la = wx.adv.LayoutAlgorithm()
        la.LayoutWindow(self.stage, self.sectors['center'])
        self.stage.Refresh()

    def createContent(self, parent):
        b = poi.views.OneChildWindow(self.control, -1)
        return b

    def createStatusBar(self):
        self.statusbarManager = poi.actions.statusbarmanager.StatusBarManager('#STATUSBAR')
        self.statusbar = self.statusbarManager.createControl(self.control)
        return self.statusbar

    def createToolBar(self):
        self.toolbarManager = poi.actions.toolbarmanager.ToolBarManager(None, '#TOOLBAR')
        self.toolbar = self.toolbarManager.createControl(self.control, wx.TB_HORZ_TEXT)
        return self.toolbar

    def getToolBarManager(self):
        return self.toolbarManager

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, messages.get('frame.title'), style=self.getStyle())
        self.control.Bind(wx.EVT_CLOSE, self.OnClose)
        toolbar = self.createToolBar()
        statusbar = self.createStatusBar()
        self.content = self.createContent(self.control)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(self.content, 1, wx.EXPAND)
        sizer.Add(statusbar, 0, wx.EXPAND | wx.ALL, 0)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.createBody(self.content)
        poi.dialogs.Dialog.createControl(self, parent)

    def OnClose(self, event):
        recipeexplorer_actions.destroyActions()
        event.Skip()

    def createBody(self, parent):
        win = wx.Window(parent, -1)
        self.stage = win

        def ignore(event):
            event.Skip()

        self.stage.Bind(wx.EVT_PAINT, ignore)
        self.createSectors()
        self.createViews()
        self.restoreLayout()
        self.performLayout()
        recipeexplorer_actions.createAction(self)

    def createViews(self):
        self.views = {}
        recipes = recipeexplorer_recipesview.RecipesView()
        recipes.createControl(self.sectors['west'])
        versions = recipeexplorer_versionsview.VersionsView()
        versions.createControl(self.sectors['center'])
        runlogs = recipeexplorer_runlogsview.RunLogsView()
        runlogs.createControl(self.sectors['east'])
        snapshot = recipeexplorer_snapshotview.SnapshotView()
        snapshot.createControl(self.sectors['snapshot'])

        class RecipeViewerEventHandler(object):
            __module__ = __name__

            def handleSelectionChanged(innerself, selection):
                self.handleProjectSelectionChanged(selection)

            def doubleClick(innerself, selection):
                self.handleProjectDoubleClick(selection)

        eventHandler = RecipeViewerEventHandler()
        recipes.getViewer().addSelectionChangedListener(eventHandler)
        recipes.getViewer().addDoubleClickListener(eventHandler)

        class VersionsViewerEventHandler(object):
            __module__ = __name__

            def handleSelectionChanged(innerself, selection):
                self.handleVersionSelectionChanged(selection)

            def doubleClick(innerself, selection):
                self.handleVersionDoubleClick(selection)

        eventHandler = VersionsViewerEventHandler()
        versions.getViewer().addSelectionChangedListener(eventHandler)
        versions.getViewer().addDoubleClickListener(eventHandler)

        class RunlogViewerEventHandler(object):
            __module__ = __name__

            def handleSelectionChanged(innerself, selection):
                self.handleRunlogSelectionChanged(selection)

        eventHandler = RunlogViewerEventHandler()
        runlogs.getViewer().addSelectionChangedListener(eventHandler)
        self.views['recipes'] = recipes
        self.views['versions'] = versions
        self.views['runlogs'] = runlogs
        self.views['snapshot'] = snapshot
        self.updateRecipes()

    def getView(self, key):
        if not key in self.views:
            return None
        return self.views[key]

    def handleRunlogSelectionChanged(self, selection):
        if len(selection) == 0:
            self.views['snapshot'].clearRunlog()
            return
        self.views['snapshot'].setRunlog(selection[0])

    def handleVersionSelectionChanged(self, selection):
        if len(selection) == 0:
            self.views['versions'].clear()
            self.views['snapshot'].clearVersion()
            return
        self.views['snapshot'].setVersion(selection[0])
        self.updateRunlogs(selection[0])

    def handleVersionDoubleClick(self, selection):
        try:
            resourcesui_actions.openRecipeVersion(selection[0])
            self.endModal(wx.ID_OK)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Cannot open recipe: '%s'" % msg)

    def handleProjectDoubleClick(self, selection):
        print(('double click', selection))

    def handleProjectSelectionChanged(self, selection):
        if len(selection) == 0:
            self.views['runlogs'].getViewer().clear()
            self.views['versions'].getViewer().clear()
            self.views['snapshot'].clear()
            return
        self.updateVersions(selection[0])
        self.views['snapshot'].setProject(selection[0])

    def updateVersions(self, project):
        self.views['versions'].showVersions(project)

    def createSectors(self):

        def relayout(event):
            event.Skip()
            self.performLayout()

        self.stage.Bind(wx.EVT_SIZE, relayout)
        west = wx.adv.SashLayoutWindow(self.stage, 1000, size=wx.Size(150, 30))
        west.SetAlignment(wx.adv.LAYOUT_LEFT)
        west.SetOrientation(wx.adv.LAYOUT_VERTICAL)
        west.SetDefaultSize(wx.Size(150, 30))
        west.SetSashVisible(wx.adv.SASH_RIGHT, True)
        runsnap = wx.adv.SashLayoutWindow(self.stage, 1002, size=wx.Size(600, 30))
        runsnap.SetBackgroundColour(wx.GREEN)
        runsnap.SetAlignment(wx.adv.LAYOUT_RIGHT)
        runsnap.SetOrientation(wx.adv.LAYOUT_VERTICAL)
        runsnap.SetDefaultSize(wx.Size(600, 30))
        runsnap.SetSashVisible(wx.adv.SASH_LEFT, True)
        center = poi.views.OneChildWindow(self.stage, -1)
        east = wx.adv.SashLayoutWindow(runsnap, 1001, size=wx.Size(200, 30))
        east.SetAlignment(wx.adv.LAYOUT_LEFT)
        east.SetOrientation(wx.adv.LAYOUT_VERTICAL)
        east.SetDefaultSize(wx.Size(200, 30))
        east.SetSashVisible(wx.adv.SASH_RIGHT, True)
        snapshot = wx.adv.SashLayoutWindow(runsnap, 1003, size=wx.Size(400, 30))
        snapshot.SetAlignment(wx.adv.LAYOUT_RIGHT)
        snapshot.SetOrientation(wx.adv.LAYOUT_VERTICAL)
        snapshot.SetDefaultSize(wx.Size(400, 30))
        self.sectors = {'west': west, 'center': center, 'east': east, 'snapshot': snapshot}

        def draggedSash(event):
            window = {1000: west, 1001: east, 1002: runsnap, 1003: snapshot}[event.GetId()]
            rect = event.GetDragRect()
            currsize = window.GetSize()
            width = rect[2]
            if width < 20:
                width = 20
            window.SetDefaultSize(wx.Size(width, currsize[1]))
            self.performLayout()

        wx.adv.EVT_SASH_DRAGGED_RANGE(self.stage, 1000, 1003, draggedSash)

    def getMementoID(self):
        return 'recipeexplorer.prefs'

    def fillLayoutMemento(self, memento):
        size = self.control.GetSize()
        memento.set('layout', 'size', '%s,%s' % (size[0], size[1]))
        for (key, view) in list(self.sectors.items()):
            if key is 'versions':
                continue
            width = view.GetSize()[0]
            memento.set('layout', '.'.join(['sector', key]), '%i' % width)

    def createDefaultLayout(self):
        self.control.SetSize((800, 600))
        self.control.CentreOnScreen()

    def restoreLayoutFromMemento(self, memento):
        size = list(map(int, tuple(memento.get('layout', 'size').split(','))))
        for (key, view) in list(self.sectors.items()):
            if not isinstance(view, wx.adv.SashLayoutWindow):
                continue
            width = int(memento.get('layout', '.'.join(['sector', key])))
            if width < 20:
                width = 20
            view.SetDefaultSize(wx.Size(width, -1))

        self.control.SetSize(size)
        self.control.CentreOnScreen()
