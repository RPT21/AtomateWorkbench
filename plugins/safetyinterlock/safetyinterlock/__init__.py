# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/safetyinterlock/src/safetyinterlock/__init__.py
# Compiled at: 2004-11-19 02:36:57
import wx, os, plugins.safetyinterlock.safetyinterlock.hw
import plugins.ui.ui.images as uiimages
import lib.kernel.plugin, lib.kernel as kernel, plugins.safetyinterlock.safetyinterlock.actions
import plugins.poi.poi.actions
import plugins.poi.poi.views.viewers, plugins.poi.poi.views.contentprovider
import plugins.hardware.hardware.hardwaremanager
import plugins.safetyinterlock.safetyinterlock.images as images
import plugins.safetyinterlock.safetyinterlock.messages as messages, logging
import plugins.ui.ui as ui
import plugins.poi.poi as poi
import plugins.executionengine.executionengine as executionengine

logger = logging.getLogger('safetyinterlock')

def getDefault():
    global instance
    return instance


class SafetyInterlockPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.controller = None
        self.provider = None
        self.books = []
        self.participants = []
        self.status = True
        ui.getDefault().setSplashText('Loading Safety Interlock plugin ...')
        instance = self
        self.ready = False
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        messages.init(contextBundle)
        images.init(contextBundle)
        ui.getDefault().addInitListener(self)
        ui.getDefault().addCloseListener(self)
        executionengine.getDefault().addEnablementStateParticipant(self)
        self.createStatusDialog()

    def hardwareManagerUpdated(self):
        pass

    def createStatusDialog(self):
        self.statusDialog = StatusDialog()

    def closing(self):
        self.statusDialog.Destroy()
        self.statusDialog = None
        return True

    def toggleStatusDialog(self):
        if self.statusDialog is None:
            return
        self.statusDialog.Show(not self.statusDialog.IsShown())
        return

    def addParticipant(self, participant):
        if participant not in self.participants:
            self.participants.append(participant)
        self.update()

    def update(self):
        self.statusDialog.fireUpdate()

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
        action = ShowSafetyLockStatusAction(self)
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
        plugins.executionengine.executionengine.getDefault().updateEnablementState()
        self.updateToolbarImage()
        self.update()

    def updateToolbarImage(self):
        if not self.status:
            self.action.setImage(images.getImage(images.STATUS_VIEW_FAILURE_ICON))
        else:
            self.action.setImage(images.getImage(images.STATUS_VIEW_NORMAL_ICON))
        tbm = ui.getDefault().getToolBarManager()
        tbm.update(True)

    def getStatus(self):
        return self.status


class InterlockParticipant(object):
    __module__ = __name__

    def __init__(self):
        getDefault().addParticipant(self)

    def isValid(self):
        return False

    def fireUpdate(self):
        getDefault().fireParticipantUpdate(self)

    def getStatusMessages(self):
        return []

    def getName(self):
        return '[no name]'


class ParticipantLabelProvider(poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        if not element.isValid():
            return uiimages.getImage(uiimages.ERROR_ICON_16)
        else:
            return uiimages.getImage(uiimages.TRANSPARENT_16)

    def getText(self, element):
        return element.getName()

    def getToolTipText(self, element):
        return ''


class ParticipantContentProvider(poi.views.contentprovider.ContentProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.ContentProvider.__init__(self)
        self.tinput = None
        return

    def inputChanged(self, viewer, oldInput, newInput):
        if self.tinput != newInput and newInput != None:
            self.tinput = newInput
        if viewer != None:
            viewer.refresh()
        return

    def getElements(self, inputElement):
        return self.tinput.getParticipants()


class ParticipantErrorsContentProvider(poi.views.contentprovider.ContentProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.ContentProvider.__init__(self)
        self.tinput = None
        return

    def inputChanged(self, viewer, oldInput, newInput):
        if self.tinput != newInput:
            self.tinput = newInput
        if viewer != None:
            viewer.refresh()
        return

    def getElements(self, inputElement):
        if self.tinput is None:
            return []
        return self.tinput.getStatusMessages()


class StatusDialog(wx.Dialog):
    __module__ = __name__

    def __init__(self):
        wx.Dialog.__init__(self, None, -1, 'Safety Interlock Status', size=wx.Size(400, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.interlock = getDefault()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.participantList = poi.views.viewers.TableViewer(self)
        self.participantList.setContentProvider(ParticipantContentProvider())
        self.participantList.setLabelProvider(ParticipantLabelProvider())
        self.participantList.setInput(getDefault())
        control = self.participantList.getControl()
        control.InsertColumn(0, 'Safety Component')

        class ParticipantViewerEventHandler(object):
            __module__ = __name__

            def handleSelectionChanged(innerself, selection):
                self.handleParticipantSelectionChanged(selection)

        eventHandler = ParticipantViewerEventHandler()
        self.participantList.addSelectionChangedListener(eventHandler)
        self.mainStatusPanel = wx.Panel(self, -1, size=wx.Size(-1, 40), style=wx.SUNKEN_BORDER)
        self.statusText = wx.StaticText(self.mainStatusPanel, -1, '', style=wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE | wx.SIMPLE_BORDER)
        self.statusText.SetBackgroundColour(wx.GREEN)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.statusText, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL, 3)
        self.mainStatusPanel.SetSizer(s)
        self.mainStatusPanel.SetAutoLayout(True)
        self.boldFont = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.normalFont = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        sizer.Add(self.mainStatusPanel, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(control, 1, wx.EXPAND | wx.ALL, 5)
        self.messagesList = poi.views.viewers.TableViewer(self)
        self.messagesList.setContentProvider(ParticipantErrorsContentProvider())
        control = self.messagesList.getControl()
        control.InsertColumn(0, 'Detailed Messages')
        sizer.Add(control, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)
        closeButton = wx.Button(self, wx.ID_CANCEL, '&Close')
        sizer.Add(closeButton, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALL, 5)

        def doclose(event):
            event.Skip()
            self.Hide()

        self.Bind(wx.EVT_BUTTON, doclose, closeButton)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        return

    def handleParticipantSelectionChanged(self, selection):
        if len(selection) == 0:
            self.messagesList.setInput(None)
            self.messagesList.refresh()
        else:
            self.messagesList.setInput(selection[0])
        return

    def OnClose(self, event):
        event.Veto()
        event.Skip()

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
            self.statusText.SetSize(wx.Size(w, h))
            self.mainStatusPanel.GetSizer().Layout()

        wx.CallAfter(doFire)


class ShowSafetyLockStatusAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, owner):
        poi.actions.Action.__init__(self, 'Safety Lock Status')
        self.owner = owner
        self.setImage(images.getImage(images.STATUS_VIEW_NORMAL_ICON))

    def run(self):
        getDefault().toggleStatusDialog()
