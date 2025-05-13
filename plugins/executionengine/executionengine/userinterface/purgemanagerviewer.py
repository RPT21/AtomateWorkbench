# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/userinterface/purgemanagerviewer.py
# Compiled at: 2004-12-08 05:15:20
import wx, plugins.ui.ui, plugins.executionengine.executionengine.purgemanager
import plugins.poi.poi.actions, wx.lib.mixins.listctrl as listmix
import plugins.executionengine.executionengine as executionengine
import plugins.ui.ui as ui
import plugins.poi.poi as poi

class AutoSizingListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style | wx.SUNKEN_BORDER)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class PurgeManagerViewer(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.showing = False
        self.createControl()
        plugins.executionengine.executionengine.purgemanager.addListener(self)
        self.populateList()
        return

    def populateList(self):
        workers = plugins.executionengine.executionengine.purgemanager.getPurgeWorkers()
        for worker in workers:
            self.addWorker(worker)

    def addWorker(self, worker):
        itemCount = self.list.GetItemCount()
        iteminfo = wx.ListItem()
        iteminfo.SetText(worker.getDescription())
        iteminfo.SetId(itemCount)
        self.list.InsertItem(iteminfo)
        self.list.SetStringItem(itemCount, 1, worker.getStatusText())
        self.list.EnsureVisible(itemCount)

    def resetAll(self):
        self.clear()
        self.populateList()

    def purgeStart(self, worker):
        wx.CallAfter(self.resetAll)

    def purgePause(self, worker):
        wx.CallAfter(self.resetAll)

    def purgeEnd(self, worker):
        wx.CallAfter(self.resetAll)

    def purgeStop(self, worker):
        wx.CallAfter(self.resetAll)

    def workerAdded(self, worker):
        wx.CallAfter(self.resetAll)

    def workerRemoved(self, worker):
        wx.CallAfter(self.resetAll)

    def createControl(self, parent=None):
        parent = ui.getDefault().getMainFrame().getControl()
        self.control = wx.Frame(parent, -1, 'Purge Manager', size=wx.Size(300, 300), pos=wx.Point(100, 100))
        self.list = self.createList()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 0)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_CLOSE, self.OnClose)

    def createList(self):
        lst = AutoSizingListCtrl(self.control, -1, style=wx.LC_REPORT)
        lst.InsertColumn(0, 'Worker')
        lst.InsertColumn(1, 'Status', wx.LIST_AUTOSIZE)
        lst.SetColumnWidth(0, 100)
        return lst

    def clear(self):
        self.list.DeleteAllItems()

    def OnClose(self, event):
        self.showing = False
        self.control.Hide()

    def dispose(self):
        executionengine.purgemanager.removeListener(self)
        self.control.Hide()
        self.control.Destroy()

    def show(self):
        self.showing = False
        self.control.Show()

    def hide(self):
        self.showing = False
        self.control.Hide()

    def isShowing(self):
        return self.showing


class ShowPurgeManagerViewerWindowAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self, owner):
        plugins.poi.poi.actions.Action.__init__(self, 'Purge Manager')
        self.owner = owner

    def run(self):
        self.owner.toggleView()


class PurgeManagerListener(object):
    __module__ = __name__

    def __init__(self):
        self.view = None
        return

    def toggleView(self):
        if self.view is None:
            return
        if self.view.isShowing():
            self.view.hide()
        else:
            self.view.show()
        return

    def create(self):
        self.createActions()
        self.view = PurgeManagerViewer()
        self.view.createControl(ui.getDefault().getMainFrame().getControl())
        executionengine.getDefault().addEngineInitListener(self)

    def engineInit(self, engine):
        self.engine = engine

    def engineEvent(self, event):
        pass

    def createActions(self):
        action = ShowPurgeManagerViewerWindowAction(self)
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.addItem(poi.actions.Separator('purgemanager-begin'))
        mng.addItem(poi.actions.ActionContributionItem(action))
        mng.addItem(poi.actions.GroupMarker('purgemanager-end'))
        mng.update()

    def __del__(self):
        self.view.dispose()


def init():
    dbg = PurgeManagerListener()
    dbg.create()
