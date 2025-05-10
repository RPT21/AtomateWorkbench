# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/actions.py
# Compiled at: 2004-11-05 00:50:22
import plugins.ui.ui, wx, plugins.poi.poi.actions, plugins.resources.resources, plugins.resources.resources.version
import plugins.resources.resources.project, plugins.resourcesui.resourcesui.actions, plugins.resourcesui.resourcesui.messages as messages
import plugins.resourcesui.resourcesui.images as images, logging, plugins.resourcesui.resourcesui.recipeexplorer.runlogexportwizard

logger = logging.getLogger('recipeexplorer.actions')
openResourceAction = None
explorer = None

def createAction(explorerPtr):
    global explorer
    explorer = explorerPtr
    openSelectedVersionAction = OpenSelectedVersionAction(explorer)
    deleteRecipeAction = DeleteRecipeAction(explorer)
    deleteVersionAction = DeleteVersionAction(explorer)
    exportRecipeAction = ExportRecipeAction(explorer)
    shareRecipeAction = ShareRecipeAction(explorer)
    unshareRecipeAction = UnshareRecipeAction(explorer)
    createInitialVersionAction = CreateInitialVersionAction(explorer)
    exportRunlogAction = ExportRunlogAction(explorer)
    tbm = explorer.getToolBarManager()
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(shareRecipeAction))
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(unshareRecipeAction))
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(deleteRecipeAction))
    tbm.addItem(plugins.poi.poi.actions.Separator())
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(openSelectedVersionAction))
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(deleteVersionAction))
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(createInitialVersionAction))
    tbm.addItem(plugins.poi.poi.actions.Separator())
    tbm.addItem(plugins.poi.poi.actions.ActionContributionItem(exportRunlogAction))
    tbm.update(True)


def destroyActions():
    pass


def updateActionBars():
    explorer.getToolBarManager().update()


class OpenMostRecentVersionAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.openmostrecentversion.label'), messages.get('actions.openmostrecentversion.help'), messages.get('actions.openmostrecentversion.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.OPEN_RESOURCE))
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            selection = selection[0]
        updateActionBars()

    def run(self):
        print('openmostrecentversion')


class CreateInitialVersionAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.createinitialversion.label'), messages.get('actions.createinitialversion.help'), messages.get('actions.createinitialversion.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.CREATE_NEW_VERSION_ICON))
        self.selection = None
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)
        return

    def hasVersions(self, project):
        workspace = plugins.resources.resources.getDefault().getWorkspace()
        return len(workspace.getRecipeVersions(project)) > 0

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            selection = selection[0]
            self.selection = selection
            self.setEnabled(not self.hasVersions(self.selection))
        updateActionBars()

    def run(self):
        try:
            resourcesui.actions.createInitialVersionAction(self.selection)
        except Exception as msg:
            logger.exception(msg)
            logger.error('Cannot create initial version: %s' % msg)


class OpenSelectedVersionAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.openversion.label'), messages.get('actions.openversion.help'), messages.get('actions.openversion.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.OPEN_VERSION_ICON))
        explorer.getView('versions').getViewer().addSelectionChangedListener(self)
        self.explorer = explorer

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            selection = selection[0]
            self.version = selection
        updateActionBars()

    def run(self):
        plugins.resourcesui.resourcesui.actions.openRecipeVersion(self.version)
        self.explorer.endModal(wx.ID_OK)


class DeleteRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.deleterecipe.label'), messages.get('actions.deleterecipe.help'), messages.get('actions.deleterecipe.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.DELETE_ICON))
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)

    def handleSelectionChanged(self, selection):
        self.selection = None
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            selection = selection[0]
            self.selection = selection
        updateActionBars()
        return

    def run(self):
        plugins.resources.resources.getDefault().getWorkspace().remove(self.selection)


class DeleteVersionAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.deleteversion.label'), messages.get('actions.deleteversion.help'), messages.get('actions.deleteversion.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.DELETE_VERSION_ICON))
        explorer.getView('versions').getViewer().addSelectionChangedListener(self)

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            selection = selection[0]
        updateActionBars()

    def run(self):
        print('deleteversion')


class PromoteVersionAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.promote.label'), messages.get('actions.promote.help'), messages.get('actions.promote.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.OPEN_RESOURCE))
        explorer.getView('versions').getViewer().addSelectionChangedListener(self)

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            selection = selection[0]
            self.version = selection
        updateActionBars()

    def run(self):
        pass


class ExportRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.export.label'), messages.get('actions.export.help'), messages.get('actions.export.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.OPEN_RESOURCE))
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)

    def handleSelectionChanged(self, selection):
        self.setEnabled(False)
        if True:
            return
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            selection = selection[0]
        updateActionBars()

    def run(self):
        pass


class ExportRunlogAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.exportrunlog.label'), messages.get('actions.exportrunlog.help'), messages.get('actions.exportrunlog.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.EXPORT_RUNLOG_ICON))
        self.runlog = None
        explorer.getView('runlogs').getViewer().addSelectionChangedListener(self)
        return

    def handleSelectionChanged(self, selection):
        self.setEnabled(False)
        if len(selection) == 0:
            self.setEnabled(False)
            self.runlog = None
        else:
            self.setEnabled(True)
            selection = selection[0]
            self.runlog = selection
        updateActionBars()
        return

    def run(self):
        dlg = plugins.resourcesui.resourcesui.recipeexplorer.runlogexportwizard.ExportRunlogWizard()
        dlg.createControl(plugins.ui.ui.getDefault().getMainFrame().getControl())
        dlg.setRunlog(self.runlog)
        dlg.showModal()


class ShareRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.shareproject.label'), messages.get('actions.shareproject.help'), messages.get('actions.shareproject.help'))
        self.project = None
        self.setEnabled(False)
        self.setImage(images.getImage(images.SHARE_ACTION_ICON))
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)
        return

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.project = None
            self.setEnabled(False)
        else:
            project = selection[0]
            self.setEnabled(not project.isShared())
            self.project = project
        updateActionBars()
        return

    def run(self):
        wrk = plugins.resources.resources.getDefault().getWorkspace()
        wrk.moveProject(self.project, wrk.getSharedLocation())


class UnshareRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.unshareproject.label'), messages.get('actions.unshareproject.help'), messages.get('actions.unshareproject.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.UNSHARE_ACTION_ICON))
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)

    def handleSelectionChanged(self, selection):
        if len(selection) == 0:
            self.setEnabled(False)
        else:
            self.project = selection[0]
            self.setEnabled(self.project.isShared())
        updateActionBars()

    def run(self):
        wrk = plugins.resources.resources.getDefault().getWorkspace()
        wrk.moveProject(self.project, wrk.getLocalLocation())


# global openResourceAction ## Warning: Unused global
