# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/goosemonitor/src/goosemonitor/__init__.py
# Compiled at: 2005-06-28 20:47:11
import wx, kernel.plugin, poi.actions, goosemonitor.actions, poi.actions, poi.views, poi.views.viewers, poi.views.contentprovider, hardware.hardwaremanager, goosemonitor.images as images, goosemonitor.messages as messages, goosemonitor.conditional, core, core.conditional, logging
import plugins.goosemonitor.goosemonitor.hw as hw
import plugins.ui.ui as ui
import plugins.goosemonitor.goosemonitor.goosedevicetype as goosedevicetype

ERROR_RETRIEVING = -1
ERROR_PARSING = -2
ERROR_OK = True
instance = None
logger = logging.getLogger('goosemonitor')

def getDefault():
    global instance
    return instance


class GooseMonitorPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.controller = None
        self.provider = None
        self.books = []
        self.status = True
        self.monitorItems = {}
        ui.getDefault().setSplashText('Loading Goose Monitor plugin ...')
        instance = self
        self.ready = False
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        messages.init(contextBundle)
        images.init(contextBundle)
        hardware.hardwaremanager.registerHardwareType(goosedevicetype.GooseDeviceType())
        ui.getDefault().addInitListener(self)
        ui.getDefault().addCloseListener(self)
        self.createMonitorWindow()
        hardware.hardwaremanager.addHardwareManagerListener(self)
        self.defineAllGeese()

    def hardwareRemoved(self, hardware):
        if not hardware in self.monitorItems:
            return
        item = self.monitorItems[hardware]
        del self.monitorItems[hardware]
        self.monitorWindow.removeItem(item)
        core.removeConditionalContribution(hardware)

    def hardwareAdded(self, hardware):
        if not hardware.getHardwareType() == goosemonitor.goosedevicetype.GOOSE_TYPE:
            return
        if hardware in self.monitorItems:
            return
        item = goosemonitor.userinterface.MonitorWindowItem(hardware.getInstance())
        self.monitorWindow.addItem(item)
        self.monitorItems[hardware] = item
        core.addConditionalContribution([conditional.GooseMonitorConditionalContribution(hardware)])

    def hardwareManagerUpdated(self):
        self.defineAllGeese()

    def defineAllGeese(self):
        types = hardware.hardwaremanager.getHardwareByType(goosemonitor.goosedevicetype.GOOSE_TYPE)
        logger.debug('Define all geese: ' + str(types))
        for hw in types:
            if hw in self.monitorItems:
                continue
            if hw.getInstance() is None:
                logger.debug('but the instance is null =(')
                continue
            self.hardwareAdded(hw)

        return

    def getMonitorWindow(self):
        return self.monitorWindow

    def createMonitorWindow(self):
        self.monitorWindow = MonitorWindow()

    def closing(self):
        self.monitorWindow.Destroy()
        self.monitorWindow = None
        return True
        return

    def toggleMonitorWindow(self):
        if self.monitorWindow is None:
            return
        self.monitorWindow.toggleView()
        return

    def addParticipant(self, participant):
        if participant not in self.participants:
            self.participants.append(participant)
        self.update()

    def update(self):
        self.monitorWindow.fireUpdate()

    def getParticipants(self):
        return self.participants

    def removeParticipant(self, participant):
        if participant in self.participants:
            self.participants.remove(participant)
        self.update()

    def fireParticipantUpdate(self, participant):

        def doit():
            valid = True
            for participant in self.participants:
                try:
                    valid = participant.isValid()
                except Exception as msg:
                    logger.exception(msg)

            if valid == self.status:
                return
            self.setStatus(valid)

        wx.CallAfter(doit)

    def readConfiguration(self, contextBundle):
        pass

    def canEnable(self):
        return self.status

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)
        action = ShowGooseMonitorStatusAction(self)
        self.action = action
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.addItem(poi.actions.ActionContributionItem(action))
        mng.update()
        tbm = ui.getDefault().getToolBarManager()
        tbm.addItem(poi.actions.Separator())
        tbm.addItem(poi.actions.ActionContributionItem(action))
        tbm.update(True)
        self.ready = True
        self.setStatus(self.status)

    def setStatus(self, status):
        self.status = status
        if not self.ready:
            return
        self.updateToolbarImage()
        self.update()

    def updateToolbarImage(self):
        if not self.status:
            self.action.setImage(images.getImage(images.SHOW_VIEW_ICON))
        else:
            self.action.setImage(images.getImage(images.SHOW_VIEW_ICON))
        tbm = ui.getDefault().getToolBarManager()
        tbm.update(True)

    def getStatus(self):
        return self.status


MONITOR_BACKGROUND_COLOR = wx.Colour(0, 0, 64)
MONITOR_FOREGROUND_COLOR = wx.Colour(192, 192, 255)

class MonitorWindow(wx.Frame):
    __module__ = __name__

    def __init__(self):
        global MONITOR_BACKGROUND_COLOR
        wx.Frame.__init__(self, None, -1, 'Goose Monitor', size=(400, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.gm = getDefault()
        self.hasFocus = False
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.items = []
        scrolledWindow = wx.ScrolledWindow(self, -1, style=wx.CLIP_CHILDREN)
        scrolledWindow.SetBackgroundColour(wx.BLACK)
        size = self.GetSize()
        inners = wx.BoxSizer(wx.VERTICAL)
        self.scrolledInnerSizer = inners
        scrolledWindow.SetAutoLayout(True)
        scrolledWindow.SetBackgroundColour(MONITOR_BACKGROUND_COLOR)
        scrolledWindow.SetSizer(inners)
        scrolledWindow.Fit()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(scrolledWindow, 1, wx.GROW | wx.ALL, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        scrolledWindow.SetScrollbars(20, 20, 10, 10)
        self.scrolledWindow = scrolledWindow
        return

    def OnSize(self, event):
        event.Skip()

    def updateScrollies(self):
        size = self.scrolledInnerSizer.GetMinSize()
        increment = 20
        self.scrolledWindow.SetScrollbars(increment, increment, size[0] / increment, size[1] / increment)

    def modifiedInternals(self):
        self.updateScrollies()
        self.GetSizer().Layout()

    def addItem(self, item):
        if item in self.items:
            return
        self.items.append(item)
        ctrl = item.createControl(self.scrolledWindow, self)
        self.scrolledInnerSizer.Add(ctrl, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
        self.scrolledInnerSizer.Fit(self.scrolledWindow)
        self.GetSizer().Layout()
        self.updateScrollies()

    def removeItem(self, item):
        if not item in self.items:
            return
        self.items.remove(item)
        ctrl = item.getControl()
        self.scrolledInnerSizer.Remove(ctrl)
        self.scrolledWindow.RemoveChild(ctrl)
        self.scrolledInnerSizer.Remove(ctrl)
        self.scrolledInnerSizer.Fit(self.scrolledWindow)
        self.GetSizer().Layout()
        self.updateScrollies()
        item.dispose()

    def handleParticipantSelectionChanged(self, selection):
        if len(selection) == 0:
            self.messagesList.setInput(None)
            self.messagesList.refresh()
        else:
            self.messagesList.setInput(selection[0])
        return

    def toggleView(self):
        if self.IsShown():
            if self.hasFocus:
                self.Show(False)
            else:
                self.Raise()
        else:
            self.Show(True)
        self.scrolledInnerSizer.Fit(self.scrolledWindow)
        self.GetSizer().Layout()

    def OnSetFocus(self, event):
        self.hasFocus = True

    def OnKillFocus(self, event):
        self.hasFocus = False

    def OnClose(self, event):
        event.Veto()
        self.Show(False)

    def fireUpdate(self):

        def doFire():
            valid = self.interlock.getStatus()
            if not valid:
                self.SetTitle('Safety Interlock Status: Error')
            else:
                self.SetTitle('Safety Interlock Status: All Systems Go!')
            self.participantList.refresh()
            color = wx.RED
            if valid:
                color = self.GetBackgroundColour()
            self.mainStatusPanel.SetBackgroundColour(color)
            msg = messages.get('label.safe')
            font = self.normalFont
            color = self.GetForegroundColour()
            if not valid:
                msg = messages.get('label.unsafe')
                font = self.boldFont
                color = wx.WHITE
            self.statusText.SetLabel(msg)
            self.statusText.SetFont(font)
            self.statusText.SetForegroundColour(color)
            (w, h) = self.statusText.GetTextExtent(msg)
            self.statusText.SetSize((w, h))
            self.mainStatusPanel.GetSizer().Layout()


class ShowGooseMonitorStatusAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, owner):
        poi.actions.Action.__init__(self, 'Goose Monitor')
        self.owner = owner
        self.setImage(images.getImage(images.SHOW_VIEW_ICON))

    def run(self):
        goosemonitor.getDefault().toggleMonitorWindow()
