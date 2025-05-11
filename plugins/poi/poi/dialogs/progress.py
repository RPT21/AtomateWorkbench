# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/dialogs/progress.py
# Compiled at: 2005-06-10 18:51:25
"""
A progress dialog to show the progress of a long running task.
There are two ways to call it:
    
    fork:  Forking will run the process in a separate thread, taking care to create the dialog in the main thread
    no-fork: Will run the process in the current thread.   If the current thread is the main thread
            then handle event dispatching so as not to starve the thread

"""
import gc, sys, wx, traceback, threading, plugins.poi.poi.dialogs, plugins.poi.poi.operation, time, logging
from plugins.poi.poi.dialogs import Dialog
import plugins.poi.poi as poi
logger = logging.getLogger('progress')
EVT_TASK_END_ID = wx.NewId()
EVT_TASK_START_ID = wx.NewId()
EVT_TASK_WORKED_ID = wx.NewId()

def EVT_TASK_WORKED(win, func):
    win.Connect(-1, -1, EVT_TASK_WORKED_ID, func)


class WorkedTaskEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self, work):
        """Fired by the runner thread to notify of startup"""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_TASK_WORKED_ID)
        self.work = work


def EVT_TASK_START(win, func, id):
    win.Connect(-1, -1, id, func)


class StartTaskEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self, id):
        """Fired by the runner thread to notify of startup"""
        wx.PyEvent.__init__(self)
        self.SetEventType(id)


def EVT_TASK_END(win, func, id):
    win.Connect(-1, -1, id, func)


class EndTaskEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self, id):
        """Fired inside the thread to notify of end"""
        wx.PyEvent.__init__(self)
        self.SetEventType(id)


class ProgressDialog(Dialog, plugins.poi.poi.operation.ProgressMonitor, wx.EvtHandler):
    __module__ = __name__

    def __init__(self, parent):
        wx.EvtHandler.__init__(self)
        Dialog.__init__(self)
        plugins.poi.poi.operation.ProgressMonitor.__init__(self)
        self.created = False
        self.parent = parent
        self.canceled = False
        self.lock = threading.Condition()
        self.runnerlock = threading.Condition()
        self.activatecount = 0
        self.ready = False
        self.done = False
        self.cancelButton = None
        self.cancelable = False
        self.taskLabel = False
        self.control = None
        self.mainTaskName = ''
        self.work = 0
        self.currentWork = 0
        self.closeId = wx.NewId()
        self.openId = wx.NewId()
        logger.debug('Creating progress dialog %d/%d/%s' % (self.closeId, self.openId, self))
        return

    def setCancelable(self, cancelable):
        self.cancelable = cancelable

    def beginTask(self, name, totalWork):
        self.mainTaskName = name
        self.work = totalWork

    def subTask(self, name):
        if name is None:
            self.setTaskText(self.mainTaskName)
        else:
            self.setTaskText(name)
        return

    def worked(self, amt):
        self.currentWork += amt
        wx.CallAfter(self.internalWorked)

    def internalWorked(self, event=None):
        logger.debug("internal worked: '%s' - %s" % (self.progressBar, self))
        self.lock.acquire()
        if not self.done:
            p = self.currentWork / float(self.work) * 100
            self.progressBar.SetValue(int(p))
        self.lock.release()

    def setTaskText(self, text):
        wx.CallAfter(self.internalSetTaskText, text)

    def internalSetTaskText(self, text):
        logger.debug('Internal Set Text')
        self.taskLabel.SetLabel(text)

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, 'Progress Dialog')
        self.progressBar = wx.Gauge(self.control, -1, 100)
        self.taskLabel = wx.StaticText(self.control, -1, '')
        self.cancelButton = wx.Button(self.control, -1, 'Cancel')
        if not self.cancelable:
            self.cancelButton.Disable()
        self.control.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelButton)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.taskLabel, 0, wx.ALIGN_LEFT | wx.GROW | wx.ALL, 5)
        sizer.Add(self.progressBar, 0, wx.GROW | wx.ALL, 5)
        sizer.Add(self.cancelButton, 0, wx.ALIGN_RIGHT | wx.ALL | 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.SetSize(wx.Size(300, 300))
        self.control.CentreOnScreen()
        self.control.PushEventHandler(self)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate, self.control)
        return self.control

    def setOperationCancelButtonEnabled(self, enabled):
        self.cancelButton.Enable(enabled)

    def OnCancel(self, event):
        self.cancelButton.Disable()
        self.setCanceled(True)

    def OnActivate(self, event):
        """We won't start the job until the dialog is shown, so we keep
        a count of the activation (seems to be 2 in win32) and then
        notify the runner thread when ready.
        """
        logger.debug('activate')
        requiredactivate = 1
        event.Skip()
        if self.activatecount > requiredactivate:
            return
        self.runnerlock.acquire()
        self.activatecount += 1
        if self.activatecount == requiredactivate:
            self.control.Disconnect(-1, -1, wx.wxEVT_ACTIVATE_APP)
            if not self.ready:
                self.ready = True
                self.runnerlock.notify()
        self.runnerlock.release()

    def create(self):
        wx.CallAfter(self.internalCreate)

    def internalCreate(self):
        self.createControl(self.parent)
        self.configureParent(self.parent)

    def doOpen(self):
        self.control.ShowModal()
        self.lock.acquire()
        self.done = True
        self.lock.notify()
        self.lock.release()
        self.done = True
        self.control.Destroy()
        self.control = None
        return

    def aboutToRun(self):
        pass

    def clearCursors(self):
        pass

    def close(self):
        logger.debug('closing dialog %d/%d/%s' % (self.openId, self.closeId, threading.currentThread()))
        self.control.EndModal(wx.ID_OK)
        logger.debug('Past End Modal')

    def deconfigureParent(self):
        pass

    def configureParent(self, parent):
        """configures the parent to listen for start task and end task events
        to properly open the window and close it
        """
        self.parent = parent
        EVT_TASK_START(self, self.OnTaskStart, self.openId)
        EVT_TASK_END(self, self.OnTaskEnd, self.closeId)
        EVT_TASK_WORKED(self, self.internalWorked)

    def OnTaskStart(self, event):
        event.Skip()
        self.open()

    def OnTaskEnd(self, event):
        self.close()

    def open(self):
        self.doOpen()

    def run(self, runnable, fork=False, cancelable=False):
        self.runnable = runnable
        self.exception = None
        self.create()

        class Runner(threading.Thread):
            __module__ = __name__

            def run(innerself):
                wx.PostEvent(self, StartTaskEvent(self.openId))
                self.runnerlock.acquire()
                if not self.ready:
                    self.runnerlock.wait()
                self.ready = True
                self.runnerlock.release()
                self.aboutToRun()
                try:
                    logger.debug('Running runnable')
                    runnable.run(self)
                except Exception as msg:
                    self.exception = sys.exc_info()

                self.done = True
                wx.PostEvent(self, EndTaskEvent(self.closeId))

        def doit():
            runner = Runner()
            runner.start()
            while runner.is_alive():
                if wx.IsMainThread(self):
                    wx.Yield()
                time.sleep(0.01)

            if self.exception is not None:
                raise poi.operation.InvocationTargetException(self.exception)
            return

        if fork:
            logger.debug('Forking for runner')

            class ForkerThread(threading.Thread):
                __module__ = __name__

                def run(self):
                    doit()

            forker = ForkerThread()
            forker.start()
        else:
            logger.debug("Did not fork.  Executing in thread '%s'" % threading.currentThread())
            doit()
        return
