# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/views/__init__.py
# Compiled at: 2005-06-10 18:51:25
import wx, wx.adv

def getHeaderColor():
    if '__WXGTK__' in wx.PlatformInfo:
        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
    else:
        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION)


def getHeaderTextColor():
    if '__WXGTK__' in wx.PlatformInfo:
        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
    else:
        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_CAPTIONTEXT)


class OneChildWindow(wx.Window):
    """A window with one child that will grow that child and not have to use a layout manager"""
    __module__ = __name__

    def __init__(self, parent, id, style=0):
        wx.Window.__init__(self, parent, id, style=style)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.insets = [0, 0, 0, 0]

    def OnSize(self, event):
        if event is not None:
            event.Skip()
        self.refresh()
        return

    def refresh(self):
        children = self.GetChildren()
        if len(children) == 0:
            return
        for child in children:
            if not child.IsShown():
                continue
            firstChild = child
            size = self.GetClientSize()
            firstChild.SetPosition((self.insets[0], self.insets[1]))
            firstChild.SetSize((size[0] - (self.insets[0] + self.insets[2]), size[1] - (self.insets[1] + self.insets[3])))
            break

        self.Refresh()


class StackedContent(OneChildWindow):
    __module__ = __name__

    def __init__(self, parent, id):
        OneChildWindow.__init__(self, parent, id)
        self.insets = [2, 2, 2, 2]
        self.radius = 8
        self.focused = False
        self.outlinecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNSHADOW)
        self.facecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.activecolor = getHeaderColor()
        self.inactivecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVEBORDER)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def setFocus(self, focused):
        self.focused = focused

    def OnPaint(self, event):
        event.Skip()
        self.draw(wx.PaintDC(self))

    def update(self):
        self.Refresh()

    def OnSize(self, event):
        OneChildWindow.OnSize(self, event)
        self.draw(wx.ClientDC(self))

    def getGradedColour(self, color):
        startColour = [
         color.Red(), color.Green(), color.Blue()]
        size = TITLE_HEIGHT
        start = color.Red()
        jump = 2
        height = TITLE_HEIGHT
        inset = 1
        for i in range(self.radius, height):
            if startColour[0] + jump < 255:
                startColour[0] += jump
            if startColour[1] + jump < 255:
                startColour[1] += jump
            if startColour[2] + jump < 255:
                startColour[2] += jump

        return startColour

    def draw(self, dc):
        size = self.GetClientSize()
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(self.outlinecolor))
        dc.DrawRectangle(0, 0, size[0], size[1])
        if self.focused:
            color = self.getGradedColour(self.activecolor)
        else:
            color = self.facecolor
        dc.SetPen(wx.Pen(color))
        dc.DrawRectangle(1, 1, size[0] - 2, size[1] - 2)
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)


TITLE_HEIGHT = 22

class StackedViewHeader(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.titleText = '[text]'
        self.titleImage = None
        self.cachedBackground = None
        self.focused = False
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.outlinecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNSHADOW)
        self.facecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.inactivetextcolor = wx.BLACK
        self.activetextcolor = getHeaderTextColor()
        self.activecolor = getHeaderColor()
        self.inactivecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVEBORDER)
        self.radius = 8
        return

    def setFocus(self, focused):
        self.focused = focused

    def createControl(self, parent):
        self.control = wx.Window(parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)
        self.control.Bind(wx.EVT_PAINT, self.OnPaint)
        self.control.Bind(wx.EVT_SIZE, self.OnSize)

    def update(self):
        self.cachedBackground = None
        self.control.Refresh()
        return

    def OnSize(self, event):
        event.Skip()
        self.cachedBackground = None
        return

    def createCachedBackground(self):
        (w, h) = self.control.GetSize()
        self.cachedBackground = wx.EmptyBitmap(w, h)
        dc = wx.MemoryDC()
        dc.SelectObject(self.cachedBackground)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.facecolor))
        dc.DrawRectangle(0, 0, w, h)
        dc.SetBrush(wx.NullBrush)
        if self.focused:
            color = self.activecolor
        else:
            color = self.facecolor
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.NullPen)
        dc.SetPen(wx.Pen(self.outlinecolor))
        dc.DrawRoundedRectangle(0, 0, w, h + self.radius, self.radius)
        height = self.getHeight()
        if self.focused:
            yoff = self.radius
            inset = 1
            startColour = [
             color.Red(), color.Green(), color.Blue()]
            start = color.Red()
            jump = 2
            inset = 1
            for i in range(self.radius, height):
                dc.SetPen(wx.Pen(wx.Colour(startColour[0], startColour[1], startColour[2])))
                dc.DrawLine(inset, i, w - inset * 2, i)
                if startColour[0] + jump < 255:
                    startColour[0] += jump
                if startColour[1] + jump < 255:
                    startColour[1] += jump
                if startColour[2] + jump < 255:
                    startColour[2] += jump

        xoffset = self.radius
        if self.titleImage is not None:
            top = self.calcCenter(self.titleImage.GetHeight(), height)
            dc.DrawBitmap(self.titleImage, xoffset, top, True)
            xoffset += self.titleImage.GetWidth() + 3
        if self.focused:
            color = self.activetextcolor
        else:
            color = self.inactivetextcolor
        dc.SetTextForeground(color)
        dc.SetFont(self.font)
        (tew, twh) = dc.GetTextExtent(self.titleText)
        top = self.calcCenter(twh, height)
        dc.DrawLabel(self.titleText, wx.Rect(xoffset, int(top), w - xoffset, h))
        return

    def calcCenter(self, itemHeight, totalHeight):
        return (totalHeight - itemHeight) / 2

    def OnPaint(self, event):
        dc = wx.PaintDC(self.control)
        if self.cachedBackground is None:
            self.createCachedBackground()
        dc.DrawBitmap(self.cachedBackground, 0, 0, False)
        return

    def setTitle(self, title):
        self.titleText = title
        self.update()

    def setTitleImage(self, image):
        self.titleImage = image
        self.update()

    def getHeight(self):
        return TITLE_HEIGHT

    def getControl(self):
        return self.control


class StackedView(object):
    __module__ = __name__

    def __init__(self):
        self.titleText = ''
        self.image = None
        self.focused = False
        self.title = None
        return

    def isFocused(self):
        return self.focused

    def setFocus(self, focused=True):
        if self.focused == focused:
            return
        self.title.setFocus(focused)
        self.content.setFocus(focused)
        self.focused = focused
        self.update()

    def createControl(self, parent):
        self.control = wx.Window(parent, -1)
        self.createTitle()
        self.createContent()
        self.control.Bind(wx.EVT_SIZE, self.OnSizeControl)
        self.OnSizeControl(None)
        return

    def update(self):
        wx.CallAfter(self.internalUpdate)

    def internalUpdate(self):
        self.title.update()
        self.content.update()

    def OnSizeControl(self, event):
        if event is not None:
            event.Skip()
        controlSize = self.control.GetClientSize()
        self.title.getControl().SetPosition((0, 0))
        titleHeight = self.title.getHeight()
        self.content.SetPosition(wx.Point(0, titleHeight))
        self.title.getControl().SetSize((controlSize[0], titleHeight))
        self.content.SetSize(wx.Size(controlSize[0], controlSize[1] - titleHeight))
        return

    def createTitle(self):
        self.title = StackedViewHeader()
        self.title.createControl(self.control)
        return self.title.getControl()

    def createContent(self):
        self.content = StackedContent(self.control, -1)
        self.createBody(self.content)

    def createBody(self, parent):
        pass

    def setTitleImage(self, image):
        self.title.setTitleImage(image)
        self.update()

    def setTitle(self, title):
        self.title.setTitle(title)
        self.update()

    def getControl(self):
        return self.control

    def getTitle(self):
        return self.title

    def getContent(self):
        return self.content


class SectorView(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        return

    def setFocus(self, focused):
        pass

    def getViewID(self):
        return None

    def createControl(self, parent):
        pass

    def getControl(self):
        return self.control

    def dispose(self):
        pass
