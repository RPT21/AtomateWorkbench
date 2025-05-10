# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/userinterface/eventviewer.py
# Compiled at: 2004-11-19 02:45:50
import wx, ui, poi.actions, poi.views, executionengine, executionengine.engine, wx.lib.mixins.listctrl as listmix, wx.lib.buttons as buttons

class AutoSizingListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class EventViewerWindow(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        return

    def createControl(self, parent):
        self.control = wx.Frame(parent, -1, 'Execution Event Viewer', size=(300, 400), style=wx.DEFAULT_FRAME_STYLE | wx.WANTS_CHARS)
        color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        self.control.SetBackgroundColour(color)
        self.list = self.createList()
        self.clearButton = wx.Button(self.control, -1, 'Clear Events')
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self.clearButton, 0)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.GROW | wx.ALL, 0)
        sizer.Add(bsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_CLOSE, self.OnClose)
        self.control.Bind(wx.EVT_CHAR, self.OnChar)
        self.control.Bind(wx.EVT_BUTTON, self.OnClearEvents, self.clearButton)

    def OnChar(self, event):
        event.Skip()
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESC:
            self.hide()

    def getEventString(self, key):
        if not key in executionengine.engine.TYPE2TEXT.keys():
            return "unknown: '%s'" % key
        return executionengine.engine.TYPE2TEXT[key]

    def getMiscInfo(self, event, engine):
        if event.getType() == executionengine.engine.TYPE_DEVICE_RESPONSE:
            buff = ''
            sep = ''
            for reply in event.getData().getReplies():
                buff += sep + str(reply)
                sep = '\t'

            return buff
        return ''

    def addEvent(self, event, engine):
        wx.CallAfter(self.internalAddEvent, event, engine)

    def internalAddEvent(self, event, engine):
        itemCount = self.list.GetItemCount()
        iteminfo = wx.ListItem()
        iteminfo.SetText(str(engine.getCurrentStepIndex()))
        iteminfo.SetId(itemCount)
        if event.getType() in [executionengine.engine.TYPE_HARDWARE_INIT_ERROR, executionengine.engine.TYPE_EXECUTION_ERROR]:
            iteminfo.SetTextColour(wx.RED)
            font = iteminfo.GetFont()
            font.SetWeight(wx.BOLD)
            iteminfo.SetFont(font)
        elif event.getType() in [executionengine.engine.TYPE_STARTING, executionengine.engine.TYPE_ENDING]:
            iteminfo.SetTextColour(wx.BLUE)
            font = iteminfo.GetFont()
            font.SetWeight(wx.BOLD)
            iteminfo.SetFont(font)
        elif event.getType() in [executionengine.engine.TYPE_HOLD, executionengine.engine.TYPE_ADVANCE, executionengine.engine.TYPE_PAUSE, executionengine.engine.TYPE_RESUME, executionengine.engine.TYPE_ABORTING]:
            iteminfo.SetTextColour(wx.BLUE)
            font = iteminfo.GetFont()
            font.SetWeight(wx.BOLD)
            iteminfo.SetFont(font)
        self.list.InsertItem(iteminfo)
        self.list.SetStringItem(itemCount, 1, self.getEventString(event.getType()))
        self.list.SetStringItem(itemCount, 2, str(engine.getCurrentLoopCount()))
        self.list.SetStringItem(itemCount, 3, str(engine.getStepTime()))
        self.list.SetStringItem(itemCount, 4, str(engine.getRecipeTime()))
        self.list.SetStringItem(itemCount, 5, str(engine.getTotalTime()))
        self.list.SetStringItem(itemCount, 6, self.getMiscInfo(event, engine))
        self.list.EnsureVisible(itemCount)

    def createList(self):
        lst = AutoSizingListCtrl(self.control, -1, style=wx.LC_REPORT)
        lst.InsertColumn(0, '')
        lst.InsertColumn(1, 'Event Type', wx.LIST_AUTOSIZE)
        lst.InsertColumn(2, 'L')
        lst.InsertColumn(3, 'Step Time')
        lst.InsertColumn(4, 'Recipe Time')
        lst.InsertColumn(5, 'Total Time')
        lst.InsertColumn(6, 'Info')
        lst.SetColumnWidth(0, 25)
        lst.SetColumnWidth(1, 200)
        lst.SetColumnWidth(2, 25)
        return lst

    def clear(self):
        self.list.DeleteAllItems()

    def OnClearEvents(self, event):
        event.Skip()
        self.clear()

    def OnClose(self, event):
        event.Veto()
        self.hide()

    def show(self):
        self.control.Show()

    def hide(self):
        self.control.Hide()

    def dispose(self):
        self.control.Destroy()

    def isShowing(self):
        return self.control.IsShown()


class ShowEventViewerWindowAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, owner):
        poi.actions.Action.__init__(self, 'Execution Event Viewer')
        self.owner = owner

    def run(self):
        self.owner.toggleView()


class DebugExecutionEventListener(object):
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
        self.view = EventViewerWindow()
        self.view.createControl(ui.getDefault().getMainFrame().getControl())
        executionengine.getDefault().addEngineInitListener(self)

    def engineInit(self, engine):
        self.engine = engine
        engine.addEngineListener(self)

    def engineEvent(self, event):
        self.view.addEvent(event, self.engine)
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)

    def createActions(self):
        action = ShowEventViewerWindowAction(self)
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.addItem(poi.actions.Separator('eventviewer-begin'))
        mng.addItem(poi.actions.ActionContributionItem(action))
        mng.addItem(poi.actions.GroupMarker('eventviewer-end'))
        mng.update()

    def __del__(self):
        self.view.dispose()


def init():
    dbg = DebugExecutionEventListener()
    dbg.create()
