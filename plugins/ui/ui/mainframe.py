# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/mainframe.py
# Compiled at: 2004-10-26 03:15:08
from wx import Frame
import wx.adv
import copy, wx, plugins.ui.ui as ui, plugins.ui.ui.messages as messages
import plugins.poi.poi.actions as actions, logging
import plugins.poi.poi.views as views
logger = logging.getLogger('mainframe')

class Sector(object):
    __module__ = __name__

    def __init__(self):
        self.stage = None
        self.control = None
        self.sid = None
        return

    def hasStage(self):
        return self.stage is not None


    def getId(self):
        return self.sid

    def refresh(self):
        self.stage.refresh()

    def createControl(self, parent, sid, id, defaultSize, style, orientation, alignment, visSash=None):
        self.sid = sid
        if visSash is not None:
            self.control = wx.adv.SashLayoutWindow(parent, id=id, size=defaultSize, style=style)
            self.control.SetAlignment(alignment)
            self.control.SetOrientation(orientation)
            self.control.SetDefaultSize(defaultSize)
            self.control.SetSashVisible(visSash, True)
        else:
            self.control = views.OneChildWindow(parent, -1)

        def resizeStage(event):
            if event is not None:
                event.Skip()
            size = self.control.GetSize()
            self.stage.SetSize(size)
            return

        self.createStage()
        return self.control


    def clearStage(self):
        if self.stage is None:
            return
        for child in self.stage.GetChildren():
            self.stage.RemoveChild(child)
            child.Destroy()
            del child

        return

    def createStage(self):
        self.stage = views.OneChildWindow(self.control, -1)

    def getControl(self):
        return self.control

    def getStage(self):
        return self.stage

    def removeView(self):
        for child in self.stage.GetChildren():
            self.stage.Remove(child)
            child.Destroy()

        self.stage.refresh()


class MainFrame(object):
    __module__ = __name__

    def __init__(self):
        self.control = Frame(None, -1, '')
        self.control.SetThemeEnabled(True)
        self.control.Hide()
        self.views = {}
        self.sectors2Views = {}
        self.perspectives = {}
        self.currentPerspective = None
        self.createSectors()
        self.setTitle(None)
        self.bindChildren()
        self.viewCreationListeners = []
        return

    def getStage(self):
        return self.stage

    def addPerspective(self, id, perspective):
        if id in self.perspectives:
            return
        self.perspectives[id] = perspective

    def getPerspective(self, id):
        if not id in self.perspectives:
            raise Exception('No perspective named %s' % id)
        return self.perspectives[id]

    def showPerspective(self, id):
        if self.currentPerspective is not None:
            self.currentPerspective.Hide()
        self.perspectives[id].Show()
        self.currentPerspective = self.perspectives[id]
        self.stage.refresh()
        return

    def bindChildren(self):
        self.control.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)

    def OnKillFocus(self, event):
        event.Skip()

    def OnChildFocus(self, event):
        event.Skip()
        self.onFocusChild(event.GetEventObject())

    def setTitle(self, title):
        sep = ' - '
        if title is None:
            sep = ''
            title = ''
        self.control.SetTitle(messages.get('frame.title.prefix') + sep + title)
        return

    def addMenuContributions(self):
        viewsManager = ui.getDefault().getMenuManager().findByPath('atm.views')

        class HideAction(actions.Action):
            __module__ = __name__

            def __init__(self):
                actions.Action.__init__(self, 'Debug Hide Sectors', 'Debug Hide Sectors', 'Debug Hide Sectors', style=actions.AS_CHECK_BOX)
                self.setChecked(True)

            def run(innerself):
                self.toggleSectorsView()

        self.hideAction = HideAction()
        viewsManager.addItem(actions.ActionContributionItem(self.hideAction))

    def toggleSectorsView(self):
        self.sectorsView.Show(not self.sectorsView.IsShown())
        self.hideAction.setChecked(self.sectorsView.IsShown())

    def createView(self, sectorID, provider, viewID):
        logger.debug("createView: sectorID='%s' viewID='%s'" % (sectorID, viewID))
        if not sectorID in self.sectors:
            raise Exception("No sector defined as '%s'" % sectorID)
        self.clearSector(sectorID)
        sector = self.sectors[sectorID]
        if not sector.hasStage():
            params = self.stageParts[sectorID]
            logger.debug("Sector params: '%s'" % params)
            sector.createControl(self.sectorsView, sectorID, params['id'], params['size'], params['style'], params['orientation'], params['alignment'], params['sash'])
        view = provider.createView(viewID, sector.getStage())
        self.sectors2Views[sectorID] = view
        self.views[viewID] = sector
        self.fireViewCreated(viewID, view)
        sector.refresh()

    def addViewLifecycleListener(self, listener):
        if not listener in self.viewCreationListeners:
            self.viewCreationListeners.append(listener)

    def removeViewLifecycleListener(self, listener):
        if listener in self.viewCreationListeners:
            self.viewCreationListeners.remove(listener)

    def fireViewCreated(self, viewID, view):
        listeners = copy.copy(self.viewCreationListeners)
        for listener in listeners:
            listener.viewCreated(viewID, view)

    def fireViewRemoved(self, viewID, view):
        listeners = copy.copy(self.viewCreationListeners)
        for listener in listeners:
            listener.viewRemoved(viewID, view)

    def onFocusChild(self, ctrl):
        root = ctrl
        viewctrls = {}
        for view in self.sectors2Views.values():
            viewctrls[view.getControl()] = view

        focusedview = None
        while root != None and root != self.control:
            if root in viewctrls:
                focusedview = viewctrls[root]
                break
            root = root.GetParent()

        if focusedview is None:
            return
        for view in self.sectors2Views.values():
            if not hasattr(view, 'setFocus'):
                continue
            view.setFocus(view == focusedview)

        return

    def removeView(self, viewID):
        if not viewID in self.views:
            return
        sector = self.views[viewID]
        view = self.sectors2Views[self.views[viewID].getId()]
        self.clearSector(sector.getId())
        self.fireViewRemoved(viewID, view)
        sector.refresh()

    def findView(self, viewID):
        """Finds the view defined by view id in the sectors and returns a tuple with the (view, sector) or None if not found"""
        if not viewID in self.views:
            return (
             None, None)
        sectorID = self.views[viewID].getId()
        return (self.sectors2Views[sectorID], sectorID)

    def clearSector(self, sectorID):
        if sectorID in self.sectors2Views:
            sect = self.sectors[sectorID]
            child = self.sectors2Views[sectorID]
            logger.debug("Closing sector '%s'" % str(child))
            logger.debug('\tSelf %s' % child.getControl())
            if hasattr(child, 'dispose'):
                child.dispose()
                del child
            else:
                logger.warning('Child of sector does not have dispose method: %s' % child)
            view = self.sectors2Views[sectorID]
            del self.views[view.getId()]
            del self.sectors2Views[sectorID]
            sect.clearStage()

    def createSectors(self):
        """The main frame is divided into sectors, north, south, east, west, and center.
            Only one view can be active in a sector.  Views can trade sectors if necessary"""
        self.sectors = {}
        self.createSashLayoutSectors()

    def createSashLayoutSectors(self):
        self.stage = views.OneChildWindow(self.control, -1)
        self.stage.insets = [
         5, 5, 5, 5]
        self.sectorsView = wx.Window(self.stage, -1)
        self.addPerspective('edit', self.sectorsView)
        self.showPerspective('edit')
        self.stageParts = {'north': {'id': 1000, 'size': (100, 30), 'style': 0, 'orientation': (wx.adv.LAYOUT_HORIZONTAL), 'alignment': (wx.adv.LAYOUT_TOP), 'sash': (wx.adv.SASH_BOTTOM)}, 'south': {'id': 1001, 'size': (100, 100), 'style': 0, 'orientation': (wx.adv.LAYOUT_HORIZONTAL), 'alignment': (wx.adv.LAYOUT_BOTTOM), 'sash': (wx.adv.SASH_TOP)}, 'west': {'id': 1002, 'size': (100, 30), 'style': 0, 'orientation': (wx.adv.LAYOUT_VERTICAL), 'alignment': (wx.adv.LAYOUT_BOTTOM), 'sash': (wx.adv.SASH_TOP)}, 'east': {'id': 1003, 'size': (100, 30), 'style': 0, 'orientation': (wx.adv.LAYOUT_HORIZONTAL), 'alignment': (wx.adv.LAYOUT_TOP), 'sash': (wx.adv.SASH_TOP)}}
        south = Sector()
        south.createControl(self.sectorsView, 'south', 1001, (100, 100), 0, wx.adv.LAYOUT_HORIZONTAL, wx.adv.LAYOUT_BOTTOM, wx.adv.SASH_TOP)
        west = Sector()
        west.createControl(self.sectorsView, 'west', 1002, (100, 30), 0, wx.adv.LAYOUT_VERTICAL, wx.adv.LAYOUT_LEFT, wx.adv.SASH_RIGHT)
        east = Sector()
        east.createControl(self.sectorsView, 'east', 1003, (100, 100), 0, wx.adv.LAYOUT_VERTICAL, wx.adv.LAYOUT_RIGHT, wx.adv.SASH_LEFT)
        center = Sector()
        center.createControl(self.sectorsView, 'center', 1000, (100, 30), 0, wx.adv.LAYOUT_VERTICAL, wx.adv.LAYOUT_LEFT)
        self.sectors = {'south': south, 'east': east, 'west': west, 'center': center}
        self.ID2Sector = {(south.getControl().GetId()): south, (east.getControl().GetId()): east, (west.getControl().GetId()): west}

        def draggedSash(event):
            window = self.ID2Sector[event.GetId()].getControl()
            rect = event.GetDragRect()
            direction = event.GetEdge()
            ydir = [
             wx.adv.SASH_BOTTOM, wx.adv.SASH_TOP]
            xdir = [wx.adv.SASH_LEFT, wx.adv.SASH_RIGHT]
            currsize = window.GetSize()
            if direction in ydir:
                width = rect[3]
                if width < 20:
                    width = 20
                window.SetDefaultSize((currsize[0], width))
            elif direction in xdir:
                height = rect[2]
                if height < 20:
                    height = 20
                window.SetDefaultSize((height, currsize[1]))
            self.updateSashPositions()

        wx.adv.EVT_SASH_DRAGGED_RANGE(self.sectorsView, 1000, 1003, draggedSash)

        def relayout(event):
            self.updateSashPositions()
            if event is not None:
                event.Skip()
            return

        self.sectorsView.Bind(wx.EVT_SIZE, relayout)

    def updateSashPositions(self):
        la = wx.adv.LayoutAlgorithm()
        la.LayoutWindow(self.sectorsView, self.sectors['center'].getControl())

    def close(self):
        self.control.Close()

    def show(self):
        self.control.Show()

    def hide(self):
        self.control.Hide()

    def dispose(self):
        self.control.Destroy()

    def getControl(self):
        return self.control

    def restoreLayout(self, memento):
        if memento is None:
            self.createDefaultLayout()
            return
        try:
            dims = memento.get('mainframe.layout', 'dimension').split(',')
            self.control.SetPosition(wx.Point(int(dims[0]), int(dims[1])))
            self.control.SetSize(wx.Size(int(dims[2]), int(dims[3])))
            maximized = memento.get('mainframe.layout', 'maximized')
            if maximized.lower() == 'true':
                self.control.Maximize(True)
            for (sectorName, window) in self.sectors.items():
                strsize = memento.get('mainframe.layout', '.'.join(['sector', sectorName]))
                size = list(map(int, strsize.split(',')))
                if size[0] < 20:
                    size[0] = 20
                if size[1] < 20:
                    size[1] = 20
                if sectorName is not 'center':
                    window.getControl().SetDefaultSize(tuple(size))

            self.updateSashPositions()
        except Exception as msg:
            logger.warning("Unable to recreate from memento, defaulting: '%s'" % msg)
            self.createDefaultLayout()

        return

    def createDefaultLayout(self):
        self.control.SetSize(wx.Size(600, 600))
        self.control.SetPosition(wx.Point(10, 10))

    def saveLayout(self, memento):
        if memento is None:
            return
        if not memento.has_section('mainframe.layout'):
            memento.add_section('mainframe.layout')
        maximized = self.control.IsMaximized()
        memento.set('mainframe.layout', 'maximized', maximized)
        size = self.control.GetSize()
        pos = self.control.GetPosition()
        memento.set('mainframe.layout', 'dimension', '%i,%i,%i,%i' % (pos[0], pos[1], size[0], size[1]))
        for (sectorName, window) in self.sectors.items():
            size = window.getControl().GetSize()
            memento.set('mainframe.layout', '.'.join(['sector', sectorName]), '%s,%s' % tuple(map(str, size)))

        return
