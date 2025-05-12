# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/panelview/src/panelview/item.py
# Compiled at: 2004-11-19 22:27:06
import wx, plugins.panelview.panelview.messages as messages, logging
logger = logging.getLogger('panelview.mainitem')

class PanelViewItem(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.height = 100
        self.device = None
        return

    def createControl(self, parent, horizontal=False):
        raise NotImplementedException()

    def getControl(self):
        return self.control

    def xgetBestSize(self):
        return (
         100, -1)

    def getHeight(self):
        return self.height

    def dispose(self):
        try:
            self.control.Destroy()
        except Exception as msg:
            pass


def str2time(val):
    if val is None:
        return '00:00:00'
    if type(val) == str:
        return '00:00:00'
    return wx.TimeSpan.Seconds(val).Format()


if False:

    class ExecutionStatusPanelItem(PanelViewItem):
        __module__ = __name__

        def __init__(self):
            PanelViewItem.__init__(self)
            self.engine = None
            plugins.executionengine.executionengine.getDefault().addEngineInitListener(self)
            executionengine.purgemanager.addListener(self)
            self.lasttext = 'Stopped'
            return

        def dispose(self):
            """Must remove as listener"""
            PanelViewItem.dispose(self)
            executionengine.getDefault().removeEngineInitListener(self)
            executionengine.purgemanager.removeListener(self)

        def purgeStart(self, worker):
            self.updateFields('Purging')

        def purgePause(self, worker):
            pass

        def purgeEnd(self, worker):
            purging = len(executionengine.purgemanager.getPurgeWorkers()) > 0
            self.updateFields('Done')

        def workerRemoved(self, worker):
            pass

        def workerAdded(self, worker):
            pass

        def engineInit(self, engine):
            if self.engine is not None:
                self.engine.removeEngineListener(self)
            self.engine = engine
            if engine is not None:
                self.engine.addEngineListener(self)
            return

        def engineEvent(self, event):
            t = event.getType()
            if t == executionengine.engine.TYPE_HOLD:
                self.lasttext = 'Holding'
            else:
                self.lasttext = 'Playing'
            txt = self.lasttext
            if t == executionengine.engine.TYPE_STARTING:
                self.updateFields('Starting ...')
            elif t == executionengine.engine.TYPE_ENDING:
                self.updateFields('Stopped')
                self.engine.removeEngineListener(self)
            else:
                self.updateFields(txt, str2time(self.engine.getStepTime()), str2time(self.engine.getRecipeTime()), str2time(self.engine.getTotalTime()), self.engine.getCurrentStepIndex() + 1)

        def updateFields(self, status, stepTime='', recipeTime='', totalTime='', stepIndex=''):
            wx.CallAfter(self.internalUpdateFields, status, stepTime, recipeTime, totalTime, stepIndex)

        def internalUpdateFields(self, status, stepTime='', recipeTime='', totalTime='', stepIndex=''):
            try:
                self.statusText.SetLabel(status)
                self.stepIndexText.SetLabel(str(stepIndex))
                self.stepTimeText.SetLabel(str(stepTime))
                self.recipeTimeText.SetLabel(str(recipeTime))
                self.totalTimeText.SetLabel(str(totalTime))
            except Exception as msg:
                logger.exception(msg)

        def createControl(self, parent):
            self.control = wx.Panel(parent, -1)
            self.control.SetBackgroundColour(wx.WHITE)
            font = self.control.GetFont()
            font.SetWeight(wx.BOLD)
            fsizer = wx.FlexGridSizer(0, 2, 3, 3)
            fsizer.AddGrowableCol(1)
            label = wx.StaticText(self.control, -1, messages.get('panelview.status.label'))
            label.SetFont(font)
            self.statusText = wx.StaticText(self.control, -1, '')
            fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            fsizer.Add(self.statusText, 1, wx.ALIGN_CENTRE_VERTICAL)
            label = wx.StaticText(self.control, -1, messages.get('panelview.stepindex.label'))
            label.SetFont(font)
            self.stepIndexText = wx.StaticText(self.control, -1, '')
            fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            fsizer.Add(self.stepIndexText, 1, wx.ALIGN_CENTRE_VERTICAL)
            label = wx.StaticText(self.control, -1, messages.get('panelview.steptime.label'))
            label.SetFont(font)
            self.stepTimeText = wx.StaticText(self.control, -1, '')
            fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            fsizer.Add(self.stepTimeText, 1, wx.ALIGN_CENTRE_VERTICAL)
            label = wx.StaticText(self.control, -1, messages.get('panelview.recipetime.label'))
            label.SetFont(font)
            self.recipeTimeText = wx.StaticText(self.control, -1, '')
            fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            fsizer.Add(self.recipeTimeText, 1, wx.ALIGN_CENTRE_VERTICAL)
            label = wx.StaticText(self.control, -1, messages.get('panelview.totaltime.label'))
            label.SetFont(font)
            self.totalTimeText = wx.StaticText(self.control, -1, '')
            fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            fsizer.Add(self.totalTimeText, 1, wx.ALIGN_CENTRE_VERTICAL)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(fsizer, 1, wx.EXPAND | wx.BOTTOM, 5)
            self.control.SetSizer(sizer)
            self.control.SetAutoLayout(True)
            sizer.Fit(self.control)
            return self.control
