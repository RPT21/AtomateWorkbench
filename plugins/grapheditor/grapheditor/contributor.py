# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grapheditor/src/grapheditor/contributor.py
# Compiled at: 2004-10-29 20:53:40
import wx, logging
logger = logging.getLogger('grapheditor.contributor')
DEBUG = False

class GraphContributor(object):
    __module__ = __name__

    def __init__(self):
        self.title = ''
        self.titlefont = self.getTitleFont()
        self.cachedTitleSize = (-1, -1)
        self.cachedTitleBitmap = None
        self.owner = None
        self.device = None
        self.isMouseIn = False
        self.recipeModel = None
        return

    def setDevice(self, device):
        self.device = device

    def onMouseMotion(self, pos):
        if not self.isMouseIn:
            return

    def onMouseEnter(self, pos):
        self.isMouseIn = True

    def onMouseLeave(self):
        self.isMouseIn = False

    def prepareItem(self, owner, recipeModel):
        self.owner = owner
        self.recipeModel = recipeModel
        self.cacheTitleSize()

    def cacheTitleBitmap(self, dc, columnWidth):
        self.cacheTitleSize()
        self.cachedTitleBitmap = wx.EmptyBitmap(columnWidth, self.getHeight())
        dc = wx.MemoryDC()
        dc.SelectObject(self.cachedTitleBitmap)
        self.drawTitle(dc, (0, 0), columnWidth)

    def refresh(self, force=False):
        if force:
            self.cachedTitleBitmap = None
        self.owner.updateItem(self)
        return

    def drawTitle(self, dc, pos, columnWidth):
        if DEBUG:
            dc.SetPen(wx.RED_PEN)
            dc.DrawRectangle(pos[0], pos[1], columnWidth, self.getHeight())
            dc.SetPen(wx.NullPen)
        dc.Clear()
        dc.SetTextForeground(wx.RED)
        dc.SetFont(self.titlefont)
        centre = self.calcCenter(self.cachedTitleSize[0], self.getHeight())
        (tw, th) = dc.GetTextExtent(self.title)
        if self.title == None:
            self.title = ''
        if tw <= 0 or th <= 0:
            (tw, th) = (
             1, 1)
        mdc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(tw, th)
        mdc.SelectObject(bmp)
        mdc.SetBackground(dc.GetBackground())
        mdc.Clear()
        mdc.SetFont(dc.GetFont())
        mdc.DrawText(self.title, 1, 1)
        img = wx.ImageFromBitmap(bmp)
        img = img.Rotate90()
        dc.DrawBitmap(img.ConvertToBitmap(), 0, 0)
        return

    def cacheTitleSize(self):
        dc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(50, 50)
        dc.SelectObject(bmp)
        self.cachedTitleSize = dc.GetFullTextExtent(self.title)

    def getTitleFont(self):
        font = wx.SWISS_FONT
        font.SetPointSize(10)
        return font

    def update(self, dc, pos, interval, pixelInterval, cachedIntervalEvents, editor):
        pass

    def setTitle(self, text):
        self.title = text

    def updateTitle(self, dc, pos, interval, columnWidth):
        if self.cachedTitleBitmap is None:
            self.cacheTitleBitmap(dc, columnWidth)
        dc.DrawBitmap(self.cachedTitleBitmap, pos[0], pos[1])
        return

    def calcCenter(self, itemHeight, totalHeight):
        return (itemHeight - totalHeight) / 2

    def getHeight(self):
        raise Exception('Not implemented')
