# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/actions.py
# Compiled at: 2004-11-05 00:50:22
import wx, plugins.poi.poi.actions
import plugins.resourcesui.resourcesui.messages as messages
import plugins.resourcesui.resourcesui.images as images, logging
import plugins.resourcesui.resourcesui.recipeexplorer.runlogexportwizard
import plugins.resourcesui.resourcesui.recipeexplorer as resourcesui_recipeexplorer
import plugins.poi.poi as poi
import plugins.ui.ui as ui
import plugins.resources.resources as resources
import plugins.resourcesui.resourcesui.actions as resourcesui_actions


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
    tbm.addItem(poi.actions.ActionContributionItem(shareRecipeAction))
    tbm.addItem(poi.actions.ActionContributionItem(unshareRecipeAction))
    tbm.addItem(poi.actions.ActionContributionItem(deleteRecipeAction))
    tbm.addItem(poi.actions.Separator())
    tbm.addItem(poi.actions.ActionContributionItem(openSelectedVersionAction))
    tbm.addItem(poi.actions.ActionContributionItem(deleteVersionAction))
    tbm.addItem(poi.actions.ActionContributionItem(createInitialVersionAction))
    tbm.addItem(poi.actions.Separator())
    tbm.addItem(poi.actions.ActionContributionItem(exportRunlogAction))
    tbm.update(True)


def destroyActions():
    pass


def updateActionBars():
    explorer.getToolBarManager().update()


class OpenMostRecentVersionAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.openmostrecentversion.label'), messages.get('actions.openmostrecentversion.help'), messages.get('actions.openmostrecentversion.help'))
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


class CreateInitialVersionAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.createinitialversion.label'), messages.get('actions.createinitialversion.help'), messages.get('actions.createinitialversion.help'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.CREATE_NEW_VERSION_ICON))
        self.selection = None
        explorer.getView('recipes').getViewer().addSelectionChangedListener(self)
        return

    def hasVersions(self, project):
        workspace = resources.getDefault().getWorkspace()
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
            resourcesui_actions.createInitialVersionAction(self.selection)
        except Exception as msg:
            logger.exception(msg)
            logger.error('Cannot create initial version: %s' % msg)


class OpenSelectedVersionAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.openversion.label'), messages.get('actions.openversion.help'), messages.get('actions.openversion.help'))
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
        resourcesui_actions.openRecipeVersion(self.version)
        self.explorer.endModal(wx.ID_OK)


class DeleteRecipeAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.deleterecipe.label'), messages.get('actions.deleterecipe.help'), messages.get('actions.deleterecipe.help'))
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
        resources.getDefault().getWorkspace().remove(self.selection)


class DeleteVersionAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.deleteversion.label'), messages.get('actions.deleteversion.help'), messages.get('actions.deleteversion.help'))
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


class PromoteVersionAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.promote.label'), messages.get('actions.promote.help'), messages.get('actions.promote.help'))
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


class ExportRecipeAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.export.label'), messages.get('actions.export.help'), messages.get('actions.export.help'))
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


class ExportRunlogAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.exportrunlog.label'), messages.get('actions.exportrunlog.help'), messages.get('actions.exportrunlog.help'))
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
        dlg = resourcesui_recipeexplorer.runlogexportwizard.ExportRunlogWizard()
        dlg.createControl(ui.getDefault().getMainFrame().getControl())
        dlg.setRunlog(self.runlog)
        dlg.showModal()


class ShareRecipeAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.shareproject.label'), messages.get('actions.shareproject.help'), messages.get('actions.shareproject.help'))
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
        wrk = resources.getDefault().getWorkspace()
        wrk.moveProject(self.project, wrk.getSharedLocation())


class UnshareRecipeAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, explorer):
        poi.actions.Action.__init__(self, messages.get('actions.unshareproject.label'), messages.get('actions.unshareproject.help'), messages.get('actions.unshareproject.help'))
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
        wrk = resources.getDefault().getWorkspace()
        wrk.moveProject(self.project, wrk.getLocalLocation())


# global openResourceAction ## Warning: Unused global
