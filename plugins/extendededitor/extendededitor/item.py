# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/item.py
# Compiled at: 2004-11-19 03:03:13
import wx, logging, plugins.poi.poi.views
import plugins.poi.poi as poi
logger = logging.getLogger('extendededitor.item')

class RoundedGradedHeader(object):
    __module__ = __name__

    def __init__(self):
        self.radius = 4
        self.activecolor = poi.views.getHeaderColor()
        self.inactivecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION)
        self.facecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.control = None
        self.childfocus = False
        self.cachedGradient = None
        self.image = None
        self.text = ''
        self.cachedSize = (10, 10)
        return

    def createCachedGradient(self):
        size = self.control.GetSize()
        self.cachedGradient = wx.EmptyBitmap(size[0], size[1])
        dc = wx.MemoryDC()
        dc.SelectObject(self.cachedGradient)
        dc.SetPen(wx.WHITE_PEN)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.DrawRectangle(0, 0, size[0], size[1])
        dc.SetPen(wx.NullPen)
        color = self.activecolor
        startColour = [
         color.Red(), color.Green(), color.Blue()]
        jump = 2
        inset = self.radius / 2
        for i in range(size[1]):
            dc.SetPen(wx.Pen(wx.Colour(startColour[0], startColour[1], startColour[2])))
            dc.DrawLine(inset, i, size[0] - inset * 2, i)
            if startColour[0] + jump < 255:
                startColour[0] += jump
            if startColour[1] + jump < 255:
                startColour[1] += jump
            if startColour[2] + jump < 255:
                startColour[2] += jump
            if inset - 1 >= 0:
                inset -= 1

    def setImage(self, image):
        self.image = image
        self.update()

    def setTitle(self, text):
        self.text = text
        self.update()

    def getSize(self):
        return self.cachedSize

    def setFocus(self, focused):
        self.childfocus = focused
        self.update()

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1, size=wx.Size(-1, 20))
        self.createCachedGradient()
        self.internalUpdate()
        self.control.Bind(wx.EVT_PAINT, self.OnPaint)
        self.control.Bind(wx.EVT_SIZE, self.OnSize)
        return self.control

    def OnSize(self, event):
        event.Skip()
        size = self.control.GetSize()
        if size != (self.cachedGradient.GetWidth(), self.cachedGradient.GetHeight()):
            self.createCachedGradient()

    def update(self):
        self.internalUpdate()

    def internalUpdate(self):
        if not self.control:
            return
        self.cacheSize()
        self.control.SetSize(self.cachedSize)
        self.control.SetToolTipString(self.text)
        self.control.Refresh()

    def cacheSize(self):
        (width, height) = (
         0, 0)
        offset = 3
        topinset = 4
        width = offset * 2
        height = topinset
        if self.image is not None:
            width += self.image.GetWidth() + width
            height += self.image.GetHeight()
        if self.text is not None:
            dc = wx.MemoryDC()
            bmp = wx.EmptyBitmap(10, 10)
            dc.SelectObject(bmp)
            ext = dc.GetFullTextExtent(self.text)
            width += ext[0]
            if ext[1] > height:
                height = ext[1] + topinset
        currsize = self.control.GetSize()
        if currsize[0] > width:
            width = currsize[0]
        self.cachedSize = (width, height)
        return

    def OnPaint(self, event):
        dc = wx.PaintDC(self.control)
        self.paint(dc)

    def paint(self, dc):
        size = self.control.GetSize()
        if self.childfocus:
            dc.DrawBitmap(self.cachedGradient, 0, 0, False)
        if self.childfocus:
            color = self.activecolor
        else:
            color = self.inactivecolor
        dc.SetPen(wx.Pen(color))
        if self.childfocus:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
        else:
            dc.SetBrush(wx.Brush(self.facecolor))
        dc.DrawRoundedRectangle(0, 0, size[0], size[1] + self.radius, self.radius)
        dc.SetBrush(wx.NullBrush)
        dc.SetPen(wx.NullPen)
        offset = 3
        if self.image is not None:
            top = self.calcCenter(self.image.GetHeight())
            dc.DrawBitmap(self.image, offset, top, True)
            offset += self.image.GetWidth() + offset
        if self.text is not None:
            top = self.calcCenter(dc.GetTextExtent(self.text)[1])
            dc.SetFont(self.font)
            if self.childfocus:
                color = poi.views.getHeaderTextColor()
            else:
                color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            dc.SetTextForeground(color)
            dc.DrawLabel(self.text, (offset, top, size[0] - offset, size[1] - top * 2))
        return

    def getPreferredHeight(self):
        return 30

    def calcCenter(self, height):
        return (self.getPreferredHeight() - height) / 4

    def getControl(self):
        return self.control


class ExtendedEditorItem(object):
    __module__ = __name__

    def __init__(self):
        self.enabled = True
        self.control = None
        self.container = None
        self.body = None
        self.radius = 5
        self.shadowsize = 2
        self.focused = False
        self.model = None
        self.activecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION)
        self.inactivecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION)
        self.header = RoundedGradedHeader()
        self.enablementStateManagedControls = []
        self.enablementState = {}
        return

    def hasConditionalContributions(self):
        return False

    def getConditionalContributions(self):
        return []

    def addStateManagedControl(self, control):
        if not control in self.enablementStateManagedControls:
            self.enablementStateManagedControls.append(control)

    def handleEnablementStateSwitched(self):
        enabled = self.isEnabled()
        for control in self.enablementStateManagedControls:
            wasEnabled = control.IsEnabled()
            if control not in self.enablementState:
                self.enablementState[control] = wasEnabled
            if enabled:
                control.Enable(self.enablementState[control])
            else:
                self.enablementState[control] = wasEnabled
                control.Disable()

    def setRecipeModel(self, model):
        if self.model is not None and self.model != model:
            self.model.removeModifyListener(self)
        self.model = model
        self.model.addModifyListener(self)
        editor = self.container.getEditor()
        editor.addSelectionChangedListener(self)
        self.handleSelectionChanged(editor.getSelection())
        return

    def isEnabled(self):
        return self.enabled

    def recipeModelChanged(self, event):
        pass

    def handleSelectionChanged(self, selection):
        step = None
        if len(selection) > 0:
            step = selection[0]
        self.stepSelectionChanged(step)
        return

    def stepSelectionChanged(self, step):
        pass

    def setTitle(self, text):
        self.title = text
        self.header.setTitle(self.title)

    def setImage(self, image):
        self.image = image
        self.header.setImage(self.image)
        self.update()

    def update(self):
        wx.CallAfter(self.internalUpdate)

    def internalUpdate(self):
        if self.control is None:
            return
        try:
            size = self.control.GetSize()
            bsize = self.body.GetSize()
            inset = self.radius + self.shadowsize
            sizer = self.control.GetSizer()
            if False and (bsize[0] + inset > size[0] or bsize[1] > size[1]):
                sizer = self.control.GetSizer()
                sizer.Layout()
                sizer.Fit(self.control)
                self.control.Refresh()
                self.container.resizeToFit()
        except wx.PyDeadObjectError as msg:
            logger.exception(msg)
            logger.warning('Error while internally updating items:%s for %s' % (msg, self))

        return

    def getControl(self):
        return self.control

    def setSize(self, size):
        self.control.SetSize(size)
        self.control.GetSizer().Layout()

    def getBestSize(self):
        if not self.control.IsShown():
            return (
             0, 0)
        return self.control.GetSizer().CalcMin()

    def createHeader(self):
        self.header.createControl(self.control)
        return self.header

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        self.control.SetBackgroundColour(wx.WHITE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        header = self.createHeader()
        body = self.createBody(self.control)
        sizer.Add(header.getControl(), 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(body, 1, wx.EXPAND | wx.ALL, self.radius + self.shadowsize)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_PAINT, self.OnPaint)
        return self.control

    def isFocused(self):
        return self.focused

    def setFocus(self, focused):
        if not self.enabled:
            return
        if self.focused == focused:
            return
        self.focused = focused
        self.header.setFocus(focused)
        self.control.Refresh()

    def getBody(self):
        return self.body

    def OnPaint(self, event):
        dc = wx.PaintDC(self.control)
        self.paint(dc)

    def paint(self, dc):
        size = self.control.GetSize()
        (i, top) = self.header.getSize()
        if self.focused:
            color = self.activecolor
        else:
            color = self.inactivecolor
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle(0, top, size[0], size[1] - top)
        dc.SetBrush(wx.NullBrush)

    def createBody(self, composite):
        pass

    def setContainerPanel(self, container):
        self.container = container

    def hide(self):
        self.control.Hide()
        self.container.update()

    def show(self):
        self.control.Show()
        self.container.update()

    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        self.setFocus(False)
        self.handleEnablementStateSwitched()
        self.update()

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        self.handleEnablementStateSwitched()
        self.update()

    def dispose(self):
        editor = self.container.getEditor()
        editor.removeSelectionChangedListener(self)
        self.model.removeModifyListener(self)
