# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/utils/staticwraptext.py
# Compiled at: 2005-06-10 18:51:25
import wx

class StaticWrapText(wx.StaticText):
    __module__ = __name__

    def __init__(self, *args, **kwargs):
        wx.StaticText.__init__(self, *args, **kwargs)
        self.__label = super(StaticWrapText, self).GetLabel()
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.__wrap()

    def SetLabel(self, label):
        self.__label = label
        self.__wrap()

    def GetLabel(self):
        return self.__label

    def __wrap(self):
        words = self.__label.split()
        lines = []
        max_width = self.GetParent().GetVirtualSizeTuple()[0]
        index = 0
        current = []
        for word in words:
            current.append(word)
            if self.GetTextExtent((' ').join(current))[0] > max_width:
                del current[-1]
                lines.append((' ').join(current))
                current = [word]

        lines.append((' ').join(current))
        super(StaticWrapText, self).SetLabel(('\n').join(lines))
        self.Refresh()

    def OnSize(self, event):
        self.__wrap()
