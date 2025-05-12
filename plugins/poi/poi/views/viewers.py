# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/views/viewers.py
# Compiled at: 2005-06-10 18:51:25
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

class SelectionProvider(object):
    __module__ = __name__

    def __init__(self):
        self.selectionChangedListeners = []
        self.selection = []

    def fireSelectionChanged(self, event):
        for listener in self.selectionChangedListeners:
            listener.handleSelectionChanged(event)

    def setSelection(self, selection):
        self.selection = selection
        self.fireSelectionChanged(self.selection)

    def addSelectionChangedListener(self, listener):
        if listener not in self.selectionChangedListeners:
            self.selectionChangedListeners.append(listener)

    def removeSelectionChangedListener(self, listener):
        if listener in self.selectionChangedListeners:
            self.selectionChangedListeners.remove(listener)

    def getSelection(self):
        return self.selection


class StructuredViewer(SelectionProvider):
    __module__ = __name__

    def __init__(self):
        SelectionProvider.__init__(self)
        self.tinput = None
        self.contentProvider = None
        self.labelProvider = None
        self.doubleClickListeners = []
        return

    def addDoubleClickListener(self, listener):
        if not listener in self.doubleClickListeners:
            self.doubleClickListeners.append(listener)

    def removeDoubleClickListener(self, listener):
        if listener in self.doubleClickListeners:
            self.doubleClickListeners.remove(listener)

    def fireDoubleClickEvent(self, selection):
        for listener in self.doubleClickListeners:
            listener.doubleClick(selection)

    def setInput(self, tinput):
        oldInput = self.tinput
        self.tinput = tinput
        if self.contentProvider != None:
            self.contentProvider.inputChanged(self, oldInput, self.tinput)
        return

    def getInput(self):
        return self.tinput

    def setContentProvider(self, contentProvider):
        self.contentProvider = contentProvider

    def setLabelProvider(self, labelProvider):
        self.labelProvider = labelProvider

    def refresh(self):
        pass

    def setSelection(self, selection, reveal=False):
        SelectionProvider.setSelection(self, selection)
        if reveal:
            self.revealSelection(selection)

    def revealSelection(self, selection):
        pass

    def clear(self):
        pass


class ListViewer(StructuredViewer):
    __module__ = __name__

    def __init__(self, parent):
        StructuredViewer.__init__(self)
        self.createControl(parent)

    def createControl(self, parent):
        self.control = None
        return

    def getList(self):
        return self.control

    def getControl(self):
        return self.control

    def refresh(self):
        pass


class MixedInListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, id, style):
        wx.ListCtrl.__init__(self, parent, id, style=style)
        ListCtrlAutoWidthMixin.__init__(self)


class TableViewer(StructuredViewer):
    __module__ = __name__

    def __init__(self, parent):
        StructuredViewer.__init__(self)
        self.id2objects = {}
        self.objects2id = {}
        self.createControl(parent)
        self.tipWindow = None
        self.lastItemHover = None
        self.imageList = {}
        return

    def createControl(self, parent):
        self.control = MixedInListCtrl(parent, -1, style=self.getStyle())
        lst = wx.ImageList(16, 16)
        self.control.AssignImageList(lst, wx.IMAGE_LIST_SMALL)
        wid = self.control.GetId()
        self.control.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, id=wid)
        self.control.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, id=wid)
        self.control.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, id=wid)
        self.control.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnItemFocused, id=wid)
        self.control.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnItemRightClick, id=wid)
        self.control.Bind(wx.EVT_LIST_KEY_DOWN, self.OnKeyDown, id=wid)
        self.control.Bind(wx.EVT_MOTION, self.OnMouseMotion, self.control)

    def OnMouseMotion(self, event):
        event.Skip()
        (idx, flags) = self.control.HitTest(event.GetPosition())
        if self.lastItemHover == idx:
            return
        self.lastItemHover = idx
        if idx == -1:
            return
        if True:
            return
        if self.labelProvider is not None:
            item = self.control.GetItem(idx)
            element = self.id2objects[item.GetData()]
            toolTipText = self.labelProvider.getToolTipText(element)
            if toolTipText is None:
                return
            if len(toolTipText.strip()) == 0:
                return
            rect = self.control.GetItemRect(item.GetId())
            pos = self.control.ClientToScreen((rect[0], rect[1]))
            rect = (pos[0], pos[1], rect[2], rect[3])
            self.tipWindow = wx.TipWindow(self.control, toolTipText)
            self.tipWindow.SetBoundingRect(rect)
        return

    def OnItemSelected(self, event):
        itemIndex = -1
        selectedItems = []
        selection = []
        while True:
            itemIndex = self.control.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            item = self.control.GetItem(itemIndex)
            selection.append(self.id2objects[item.GetData()])

        self.setSelection(selection)

    def OnItemDeselected(self, event):
        self.setSelection([])

    def OnItemActivated(self, event):
        event.Skip()
        self.fireDoubleClickEvent(self.getSelection())

    def OnItemFocused(self, event):
        pass

    def OnItemRightClick(self, event):
        pass

    def OnKeyDown(self, event):
        pass

    def deselectAll(self):
        itemIndex = -1
        while True:
            itemIndex = self.control.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            item = self.control.GetItem(itemIndex)
            item.SetState(item.GetState() & ~wx.LIST_STATE_SELECTED)

    def selectAndReveal(self, obj):
        if not obj in self.objects2id:
            return
        index = self.objects2id[obj]
        self.control.EnsureVisible(index)
        self.deselectAll()
        item = self.control.GetItem(index)
        item.SetState(item.GetState() | wx.LIST_STATE_SELECTED)

    def revealSelection(self, selection):
        self.control.Refresh()

    def getStyle(self):
        return wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER

    def getTable(self):
        return self.control

    def getControl(self):
        return self.control

    def refresh(self):
        wx.CallAfter(self.internalRefresh)

    def internalRefresh(self):
        if self.contentProvider != None:
            oldSelection = self.getSelection()
            self.control.DeleteAllItems()
            elems = self.contentProvider.getElements(self.getInput())
            i = 0
            self.id2objects.clear()
            for elem in elems:
                image = None
                text = elem
                if self.labelProvider is not None:
                    text = self.labelProvider.getText(elem)
                    image = self.labelProvider.getImage(elem)
                newItem = wx.ListItem()
                newItem.SetData(i)
                self.id2objects[i] = elem
                if image is not None:
                    if image not in self.imageList:
                        if image.GetWidth() == 16 and image.GetHeight() == 16:
                            self.imageList[image] = self.control.GetImageList(wx.IMAGE_LIST_SMALL).Add(image)
                    if image in self.imageList:
                        newItem.SetImage(self.imageList[image])
                newItem.SetText(text)
                newItem.SetId(i)
                newItem.SetColumn(0)
                newItem.SetMask(wx.LIST_MASK_TEXT | wx.LIST_MASK_DATA | wx.LIST_MASK_IMAGE)
                self.control.InsertItem(newItem)
                self.objects2id[elem] = i
                i += 1

        return
