# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/perspective.py
# Compiled at: 2004-12-14 22:00:17
import math, time, wx, threading, logging, plugins.executionengine.executionengine.messages as messages
import plugins.executionengine.executionengine.images as images
import plugins.executionengine.executionengine, plugins.ui.ui, plugins.ui.ui.context, plugins.poi.poi.utils
import plugins.poi.poi.utils.scrolledpanel, plugins.poi.poi.utils.listctrl
import plugins.executionengine.executionengine.engine as engine_lib
import wx.adv
import plugins.executionengine.executionengine as executionengine
import plugins.poi.poi.utils
import plugins.poi.poi as poi
import plugins.ui.ui as ui
import plugins.panelview.panelview as panelview

class Perspective(wx.Window):
    __module__ = __name__

    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1)
        self.Hide()
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.createSectors()
        self.engine = None
        plugins.executionengine.executionengine.getDefault().addEngineInitListener(self)
        return

    def getEngine(self):
        return self.engine

    def engineInit(self, engine):
        plugins.ui.ui.getDefault().getMainFrame().showPerspective('run')
        self.engine = engine
        self.engine.addEngineListener(self)

    def engineEvent(self, event):
        t = event.getType()
        if t == plugins.executionengine.executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)
        self.detailedView.engineEvent(event)

    def OnSize(self, event):
        event.Skip()
        self.updateSashPositions()

    def createSectors(self):
        self.sectors = {}
        self.layout = wx.adv.LayoutAlgorithm()
        self.top = self.createSector((wx.adv.LAYOUT_TOP, wx.adv.LAYOUT_HORIZONTAL, 30, wx.adv.SASH_BOTTOM, 150))
        self.detailedView = DetailedExecutionView(self.top, self)
        self.left = self.createSector((wx.adv.LAYOUT_LEFT, wx.adv.LAYOUT_VERTICAL, 30, wx.adv.SASH_RIGHT, 100))
        self.graphView = GraphView(self.left, self)
        self.main = self.createSector((wx.adv.LAYOUT_RIGHT, wx.adv.LAYOUT_VERTICAL, 30, None, 100))
        self.ledView = LEDView(self.main, self)
        self.updateSashPositions()
        return

    def dispose(self):
        self.detailedView.dispose()

    def getGraphPanel(self):
        return self.graphView

    def updateSashPositions(self):
        self.layout.LayoutWindow(self)

    def createSector(self, values):
        sector = wx.adv.SashLayoutWindow(self, -1, style=wx.CLIP_CHILDREN | wx.adv.SW_3D)
        sector.SetAlignment(values[0])
        sector.SetDefaultSize(wx.Size(300, values[4]))
        sector.SetOrientation(values[1])
        sector.SetMinimumSizeY(values[2])
        sector.SetMinimumSizeX(values[2])
        if values[3]:
            sector.SetSashVisible(values[3], True)
        sector.Bind(wx.adv.EVT_SASH_DRAGGED, self.OnSashDragged)
        return sector

    def OnSashDragged(self, event):
        obj = event.GetEventObject()
        event.Skip()
        (x, y, w, h) = event.GetDragRect()
        obj.SetDefaultSize((w, h))
        self.updateSashPositions()


class BoldLabel(wx.StaticText):
    __module__ = __name__

    def __init__(self, parent, id, text):
        wx.StaticText.__init__(self, parent, id, text)
        font = parent.GetFont()
        font.SetWeight(wx.BOLD)
        self.SetFont(font)


logger = logging.getLogger('perspective.run')

def str2time(val):
    if val is None:
        return '00:00:00'
    if type(val) == str:
        return '00:00:00'
    s = time.strftime('%H:%M:%S', time.gmtime(math.floor(val)))
    logger.debug('str2time: %s' % s)
    return s


TYPE2STATUS = {(engine_lib.TYPE_STARTING): 'Starting',
               (engine_lib.TYPE_ENDING): 'End', (engine_lib.TYPE_HOLD): 'Hold',
               (engine_lib.TYPE_ADVANCE): 'Advance', (engine_lib.TYPE_PAUSE): 'Pause',
               (engine_lib.TYPE_RESUME): 'Resume', (engine_lib.TYPE_ABORTING): 'Aborting',
               (engine_lib.TYPE_HARDWARE_INIT_ERROR): 'Error Initializing Hardware',
               (engine_lib.TYPE_HARDWARE_INIT_START): 'Initializing Hardware',
               (engine_lib.TYPE_HARDWARE_INIT_END): 'Finished Initializing'}

class GraphView(plugins.poi.poi.utils.scrolledpanel.ScrolledPanel):
    __module__ = __name__

    def __init__(self, parent, perspective):
        plugins.poi.poi.utils.scrolledpanel.ScrolledPanel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.sizer = sizer
        self.SetupScrolling()

    def OnPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        (w, h) = self.GetSize()
        dc.DrawRectangle(0, 0, w - 1, h - 1)

    def refresh(self):
        wx.CallAfter(self.__refresh)

    def __refresh(self):
        """
                # !!! arg
        class SizeHandler(wx.EvtHandler):
            def __init__(self2):
                wx.EvtHandler.__init__(self2)
                self.Bind(wx.EVT_SIZE, self2.OnSize, self)
            
            def OnSize(self2, event):
                event.Skip()
                sizer = self.control.GetSizer()
                for child in self.control.GetChildren():
                    sizer.SetItemMinSize(child, child.GetBestSize())
                
                sizer.Layout()
        """
        sizer = self.GetSizer()
        for child in self.GetChildren():
            sizer.SetItemMinSize(child, child.GetBestSize())

        sizer.Layout()
        self.Layout()

    def addGraphPanel(self, panel):
        self.sizer.Add(panel, 0, wx.EXPAND | wx.ALL, 5)
        self.refresh()

    def removeGraphPanel(self, panel):
        self.sizer.Remove(panel)
        self.RemoveChild(panel)
        panel.Destroy()
        self.refresh()


class LEDView(wx.Panel):
    __module__ = __name__

    def __init__(self, parent, perspective):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panelview = panelview.PanelView()
        self.panelview.createControl(self, False)
        sizer.Add(self.panelview.getControl(), 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.hookToRecipe()

    def hookToRecipe(self):
        self.model = None
        ui.context.addContextChangeListener(self)
        self.model = ui.context.getProperty('recipe')
        if self.model is not None:
            self.prepareInput()
        return

    def contextChanged(self, event):
        key = event.getKey()
        value = event.getNewValue()
        old = self.model
        if key == 'recipe':
            if value is None:
                if self.model is None:
                    return
                self.model.removeModifyListener(self)
                self.model = None
                self.panelview.getViewer().inputChanged(old, self.model)
            else:
                import plugins.grideditor.grideditor as grideditor
                self.model = grideditor.getDefault().getEditor().getInput()
                self.prepareInput()
                self.panelview.getViewer().inputChanged(old, self.model)
        return

    def prepareInput(self):
        pass

    def refresh(self):
        wx.CallAfter(self.Refresh)


class HistoryList(plugins.poi.poi.utils.listctrl.ListCtrl):
    __module__ = __name__

    def __init__(self, parent):
        plugins.poi.poi.utils.listctrl.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_HRULES)
        self.InsertColumn(0, 'Run History')
        self.SetColumnWidth(0, 300)

    def clear(self):

        def doit():
            self.DeleteAllItems()
            self.Refresh()

        wx.CallAfter(doit)

    def appendItem(self, label, color=None, bold=False, icon=None):
        wx.CallAfter(self._internalAppendItem, label, color, bold, icon)

    def _internalAppendItem(self, label, color=None, bold=False, icon=None):
        i = self.GetItemCount()
        item = wx.ListItem()
        item.SetId(i)
        item.SetText(label)
        if color is not None:
            item.SetTextColour(color)
        if bold:
            font = self.GetFont()
            font.SetWeight(wx.BOLD)
            item.SetFont(font)
        self.InsertItem(item)
        self.EnsureVisible(i)
        self.Refresh()
        return


class TimerThread(threading.Thread):
    __module__ = __name__

    def __init__(self, func):
        threading.Thread.__init__(self)
        self.daemon = True
        self.paused = True
        self.done = False
        self.func = func

    def shutdown(self):
        logger.debug('Shutting down detailed view timer thread')
        self.done = True
        self.join(2.0)
        logger.debug('Joined timer thread')

    def run(self):
        then = time.time()
        while not self.done:
            time.sleep(0.1)
            if self.done:
                break
            now = time.time()
            if now - then >= 1.0:
                self.func()
                then = time.time()

        logger.debug('Exiting detailed view timer thread')


STATE_STOPPED = 2
STATE_RUNNING = 4
STATE_LOOPING = 8
STATE_HOLDING = 16

class DetailedExecutionView(plugins.poi.poi.utils.scrolledpanel.ScrolledPanel):
    __module__ = __name__

    def __init__(self, parent, perspective):
        plugins.poi.poi.utils.scrolledpanel.ScrolledPanel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.executedConditionals = []
        self.SetBackgroundColour(wx.WHITE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self, 1, wx.EXPAND)
        parent.SetSizer(sizer)
        parent.SetAutoLayout(True)
        self.perspective = perspective
        self.createControls()
        self.lastSize = (0, 0)
        self.timer = TimerThread(self.OnTick)
        self.timer.start()
        self.SetupScrolling()
        self.reset()

    def reset(self):
        self.enterStepTime = 0
        self.recipeStartTime = 0
        self.recipeTime = 0
        self.stepTime = 0
        self.state = STATE_STOPPED
        self.lastTime = 0

    def dispose(self):
        self.timer.shutdown()

    def OnTick(self):

        def doTick():
            if self.state & STATE_STOPPED != 0:
                return
            now = time.time()
            delta = now - self.lastTime
            self.lastTime = now
            if self.state & STATE_RUNNING != 0:
                if self.state & STATE_HOLDING == 0:
                    self.recipeTime += delta
                    self.stepTime += delta
            totalTime = now - self.recipeStartTime
            self.ctrlRecipeTime.SetLabel(str2time(self.recipeTime))
            self.ctrlTotalTime.SetLabel(str2time(totalTime))
            self.ctrlStepTime.SetLabel(str2time(self.stepTime))
            if self.state & STATE_RUNNING != 0:
                pass
            if self.state & STATE_LOOPING != 0:
                pass

        wx.CallAfter(doTick)

    def getStatusText(self, eventType):
        global TYPE2STATUS
        if eventType not in TYPE2STATUS:
            return 'Running'
        return TYPE2STATUS[eventType]

    def clearExecutedConditionals(self):
        self.executedConditionals = []

    def addExecutedConditional(self, conditional):
        self.executedConditionals.append(conditional)

    def hasExecutedConditional(self, conditional):
        return conditional in self.executedConditionals

    def engineEvent(self, event):
        engine = self.perspective.getEngine()
        t = event.getType()
        if t == executionengine.engine.TYPE_STARTING:
            self.closeButton.Enable(False)
            self.historyList.clear()
            self.historyList.appendItem('Starting ...')
        elif t == executionengine.engine.TYPE_ENDING:
            self.state = STATE_STOPPED
            self.historyList.appendItem('Finished')
            self.closeButton.Enable(True)
            self.reset()
        elif t == executionengine.engine.TYPE_ENTERING_STEP:
            self.historyList.appendItem('Entering step %d' % (engine.getCurrentStepIndex() + 1))
            self.clearExecutedConditionals()
            self.stepTime = 0
            self.lastTime = time.time()
        elif t == executionengine.engine.TYPE_CONDITIONAL_EXECUTING:
            (suite, action) = event.getData()
            if not self.hasExecutedConditional(suite):
                self.historyList.appendItem('Executing action %s to conditional suite %s' % (action, suite.getName()), color=wx.GREEN)
                self.addExecutedConditional(suite)
        elif t == executionengine.engine.TYPE_EXECUTION_ERROR:
            self.historyList.appendItem(event.getData(), color=wx.RED, bold=True)
        elif t == executionengine.engine.TYPE_HARDWARE_INIT_START:
            self.historyList.appendItem('Initializing devices ...')
        elif t == executionengine.engine.TYPE_HARDWARE_INIT_ERROR:
            self.historyList.appendItem('Error while initializing device: %s' % event.getData())
        elif t == executionengine.engine.TYPE_HARDWARE_INIT_END:
            self.historyList.appendItem('Finished initializing devices ...')
            self.state = STATE_RUNNING
            self.recipeStartTime = time.time()
            self.lastTime = time.time()
        if t == executionengine.engine.TYPE_PAUSE:
            self.state |= STATE_HOLDING
        if t == executionengine.engine.TYPE_HOLD:
            self.state |= STATE_HOLDING
        if t == executionengine.engine.TYPE_RESUME:
            self.state &= ~STATE_HOLDING
        if t == executionengine.engine.TYPE_ADVANCE:
            self.state &= ~STATE_HOLDING
        statusText = self.getStatusText(t)
        self.ctrlStatus.SetLabel(statusText)
        self.ctrlStepNumber.SetLabel(str(engine.getCurrentStepIndex() + 1))
        if engine.isLooping():
            self.ctrlLoopCount.SetLabel(str(engine.getLoopCount()))
            if self.state & STATE_RUNNING != 0:
                self.state |= STATE_LOOPING
        else:
            self.ctrlLoopCount.SetLabel('No Loop')
            if self.state & STATE_RUNNING != 0:
                self.state &= ~STATE_LOOPING
        sizer = self.numsPanel.GetSizer()
        (w, h) = self.ctrlRecipeTime.GetSize()
        ctrls = [
         self.ctrlStatus, self.ctrlStepNumber, self.ctrlLoopCount, self.ctrlStepTime, self.ctrlRecipeTime, self.ctrlTotalTime]
        (w, h) = self.lastSize
        for ctrl in ctrls:
            s2 = ctrl.GetSize()
            if s2[0] > w:
                w = s2[0]
            sizer.SetItemMinSize(ctrl, w, s2[1])

        if w != self.lastSize[0]:
            self.lastSize = (
             w, h)
            sizer.RecalcSizes()
            self.GetSizer().Layout()

    def createHistory(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.WHITE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, -1, messages.get('perspective.run.label.history')), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND)
        lst = HistoryList(panel)
        sizer.Add(lst, 1, wx.EXPAND | wx.ALL)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        self.historyList = lst
        return panel

    def createControls(self):
        self.numsPanel = wx.Panel(self, -1)
        sizer = wx.FlexGridSizer(6, 2, gap=wx.Size(0,0))
        sizer.AddGrowableCol(1)
        self.labelStatus = BoldLabel(self.numsPanel, -1, messages.get('perspective.label.status'))
        self.labelStepNumber = BoldLabel(self.numsPanel, -1, messages.get('perspective.label.stepnumber'))
        self.labelLoopCount = BoldLabel(self.numsPanel, -1, messages.get('perspective.label.loopcount'))
        self.labelStepTime = BoldLabel(self.numsPanel, -1, messages.get('perspective.label.steptime'))
        self.labelRecipeTime = BoldLabel(self.numsPanel, -1, messages.get('perspective.label.recipetime'))
        self.labelTotalTime = BoldLabel(self.numsPanel, -1, messages.get('perspective.label.totaltime'))
        self.ctrlStatus = wx.StaticText(self.numsPanel, -1, '')
        self.ctrlStepNumber = wx.StaticText(self.numsPanel, -1, '')
        self.ctrlLoopCount = wx.StaticText(self.numsPanel, -1, '')
        self.ctrlStepTime = wx.StaticText(self.numsPanel, -1, '')
        self.ctrlRecipeTime = wx.StaticText(self.numsPanel, -1, '')
        self.ctrlTotalTime = wx.StaticText(self.numsPanel, -1, '')
        sizer.Add(self.labelStatus)
        sizer.Add(self.ctrlStatus, 1)
        sizer.Add(self.labelStepNumber)
        sizer.Add(self.ctrlStepNumber, 1)
        sizer.Add(self.labelLoopCount)
        sizer.Add(self.ctrlLoopCount, 1)
        sizer.Add(self.labelStepTime)
        sizer.Add(self.ctrlStepTime, 1)
        sizer.Add(self.labelRecipeTime)
        sizer.Add(self.ctrlRecipeTime, 1)
        sizer.Add(self.labelTotalTime)
        sizer.Add(self.ctrlTotalTime, 1)
        self.numsPanel.SetSizer(sizer)
        self.numsPanel.SetAutoLayout(True)
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        historyPanel = self.createHistory()
        self.closeButton = poi.utils.ImageButton(self, -1, images.getImage(images.RUN_ENABLED), messages.get('perspective.label.close'))
        self.Bind(wx.EVT_BUTTON, self.OnCloseButton, self.closeButton)
        self.closeButton.Enable(False)
        mainsizer.Add(self.numsPanel, 0, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL), 0, wx.EXPAND)
        mainsizer.Add(historyPanel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)
        mainsizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL), 0, wx.EXPAND)
        mainsizer.Add(self.closeButton, 0, wx.ALIGN_TOP | wx.ALL, 5)
        self.SetSizer(mainsizer)
        self.SetAutoLayout(True)

    def OnCloseButton(self, event):
        ui.getDefault().getMainFrame().showPerspective('edit')
