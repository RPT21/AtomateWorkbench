# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/utils/listctrl.py
# Compiled at: 2005-06-10 18:51:25
import wx, wx.lib.mixins.listctrl as listmix

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def getSelectedIndexes(self):
        itemIndex = -1
        selected = []
        while True:
            itemIndex = self.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            selected.append(itemIndex)

        return selected
