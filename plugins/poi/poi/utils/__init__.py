# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/utils/__init__.py
# Compiled at: 2005-06-10 18:51:25
import wx

class ImageButton(wx.BitmapButton):
    __module__ = __name__

    def __init__(self, parent, id, bitmap, label):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(2, 2))
        self.bmp = self.__createLabel(bitmap, label)
        self.SetBitmapLabel(self.bmp)

    def __createLabel(self, bitmap, label):
        (w, h) = self.__calcDimensions(bitmap, label)
        bmp = wx.Bitmap(w, h)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        mid = int((h - bitmap.GetHeight()) / 2)
        dc.DrawBitmap(bitmap, 0, mid, True)
        x = bitmap.GetWidth() + 2
        dc.SetFont(self.GetFont())
        mid = (h - dc.GetTextExtent(label)[1]) / 2
        dc.DrawText(label, int(x), int(mid))
        return bmp

    def __calcDimensions(self, bitmap, label):
        (w, h) = (0, 0)
        if bitmap is not None:
            (w, h) = (bitmap.GetWidth(), bitmap.GetHeight())
        (tw, th, des, lead) = self.GetParent().GetFullTextExtent(label)
        textheight = th + des
        if h < textheight:
            h = textheight
        w += tw + 2
        return (w, h)

