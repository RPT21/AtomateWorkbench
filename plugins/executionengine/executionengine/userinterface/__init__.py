# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/userinterface/__init__.py
# Compiled at: 2004-08-18 03:36:54
import wx, plugins.poi.poi.dialogs, threading, plugins.ui.ui, logging
import plugins.ui.ui as ui
import plugins.poi.poi as poi

EVT_RUNNING_TASK_END_ID = wx.NewId()
EVT_RUNNING_TASK_START_ID = wx.NewId()

def EVT_RUNNING_TASK_END(win, func):
    win.Connect(-1, -1, EVT_RUNNING_TASK_END_ID, func)


class ResultEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self, id):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RUNNING_TASK_END_ID)
        self.id = id


def EVT_RUNNING_TASK_START(win, func):
    win.Connect(-1, -1, EVT_RUNNING_TASK_START_ID, func)


class StartTaskEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RUNNING_TASK_START_ID)


class InitializeDialogJob(object):
    __module__ = __name__

    def __init__(self):
        self.dialog = None
        return

    def cancel(self):
        pass

    def setDialog(self, dialog):
        self.dialog = dialog

    def setMessage(self, message):
        if self.dialog is None:
            return
        self.dialog.setMessage(message)
        return

    def run(self, dialog):
        pass


USE_DIALOG = True

class RecipeInitializationDialog(plugins.poi.poi.dialogs.Dialog):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.dialogs.Dialog.__init__(self)
        self.showing = False
        self.lock = threading.Condition()
        self.showThread = None
        self.done = False
        self.results = None
        self.logger = logging.getLogger('executionengine')
        self.control = None
        self.retid = wx.ID_OK
        self.canceled = False
        return

    def createControl(self, parent):
        if self.control is not None:
            raise Exception('Control is already created')
        self.control = wx.Dialog(parent, -1, 'Recipe Initialization')
        self.currentTaskLabel = wx.StaticText(self.control, -1, '')
        self.cancelButton = wx.Button(self.control, -1, 'Cancel')
        self.okButton = wx.Button(self.control, -1, 'OK')
        self.okButton.Hide()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.currentTaskLabel, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        sizer.Add(self.okButton, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.SetSize(wx.Size(400, 500))
        self.control.CentreOnScreen()
        EVT_RUNNING_TASK_END(self.control, self.OnResults)
        poi.dialogs.Dialog.createControl(self, parent)
        self.control.Bind(wx.EVT_BUTTON, self.OnOKButton, self.okButton)
        self.control.Bind(wx.EVT_BUTTON, self.OnCancelPressed, self.cancelButton)
        return

    def OnOKButton(self, event):
        self.bringDown(wx.ID_CANCEL)

    def OnCancelPressed(self, event):
        event.Skip()
        self.canceled = True
        self.cancelButton.Disable()
        self.runner.cancel()

    def OnResults(self, event):
        event.Skip()
        if self.canceled:
            self.bringDown(event.id)
            return
        if event.id == wx.ID_OK:
            self.bringDown(wx.ID_OK)
            return
        self.okButton.Show()
        self.cancelButton.Hide()
        sizer = self.control.GetSizer()
        sizer.Layout()
        self.setMessage('Errors while initializing hardware')

    def setMessage(self, message):
        self.lock.acquire()
        if not self.showing:
            self.lock.release()
            return
        self.currentTaskLabel.SetLabel(message)
        sizer = self.control.GetSizer()
        sizer.SetItemMinSize(self.currentTaskLabel, self.currentTaskLabel.GetSize())
        sizer.Layout()
        self.lock.release()

    def bringDown(self, id):
        self.results = id == wx.ID_OK
        self.retid = id == wx.ID_OK
        self.endModal(id)
        self.lock.acquire()
        self.lock.notify()
        self.lock.release()

    def OnStartTask(self, event):
        self.createControl(ui.getDefault().getMainFrame().getControl())
        event.Skip()
        self.showing = True
        self.showModal()
        self.control.Destroy()
        del self.control
        self.control = None
        self.lock.acquire()
        self.lock.notify()
        self.lock.release()
        return

    def execute(self, job):
        job.setDialog(self)
        EVT_RUNNING_TASK_START(ui.getDefault().getMainFrame().getControl(), self.OnStartTask)
        runner = RunnerThread(self, job)
        runner.start()
        self.runner = runner
        self.lock.acquire()
        self.lock.wait()
        self.lock.release()
        mainframe = ui.getDefault().getMainFrame().getControl()
        mainframe.Disconnect(-1, -1, EVT_RUNNING_TASK_START_ID)
        return self.retid


class RunnerThread(threading.Thread):
    __module__ = __name__

    def __init__(self, dialog, job):
        threading.Thread.__init__(self)
        self.dialog = dialog
        self.job = job

    def cancel(self):
        self.job.cancel()

    def run(self):
        wx.PostEvent(ui.getDefault().getMainFrame().getControl(), StartTaskEvent())
        try:
            self.job.run(self.dialog)
        except Exception as msg:
            self.dialog.logger.exception(msg)
            self.dialog.logger.error("Exception while executing job: '%s'" % msg)
            wx.PostEvent(self.dialog.control, ResultEvent(wx.ID_CANCEL))
            return

        wx.PostEvent(self.dialog.control, ResultEvent(wx.ID_OK))
