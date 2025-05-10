# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/utils/errorviewer.py
# Compiled at: 2004-12-08 05:16:11
import wx, ui, poi, poi.actions, validator, grideditor.messages as messages, wx.lib.mixins.listctrl as listmix, wx.lib.buttons as buttons, grideditor, grideditor.images as images

class AutoSizingListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style | wx.SUNKEN_BORDER)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class ErrorViewer(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.showing = False
        self.createControl()
        validator.getDefault().addValidationListener(self)
        self.stepIndices = []
        return

    def validationEvent(self, valid, errors):
        wx.CallAfter(self.internalValidationEvent, valid, errors)

    def internalValidationEvent(self, valid, errors):
        self.resetAll()
        for error in errors:
            self.addError(error)

    def getStepIndex(self, step):
        recipe = ui.context.getProperty('recipe')
        return recipe.getStepIndex(step)

    def addError(self, error):
        if 'step' in error.getKeys():
            stepidx = self.getStepIndex(error.getStep())
        else:
            stepidx = None
        itemCount = self.list.GetItemCount()
        iteminfo = wx.ListItem()
        if stepidx is not None:
            iteminfo.SetText('%i' % (stepidx + 1))
        else:
            iteminfo.SetText('N/A')
        iteminfo.SetId(itemCount)
        self.list.InsertItem(iteminfo)
        self.list.SetStringItem(itemCount, 1, error.getDescription())
        self.list.EnsureVisible(itemCount)
        self.stepIndices.append(stepidx)
        return

    def resetAll(self):
        self.clear()

    def createControl(self, parent=None):
        parent = ui.getDefault().getMainFrame().getControl()
        self.control = wx.Frame(parent, -1, messages.get('dialog.errorviewer.title'), size=(300, 300), pos=(100, 100))
        self.list = self.createList()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.GROW | wx.ALL, 0)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_CLOSE, self.OnClose)

    def createList(self):
        lst = AutoSizingListCtrl(self.control, -1, style=wx.LC_REPORT)
        lst.InsertColumn(0, messages.get('dialog.errorviewer.column.step'))
        lst.InsertColumn(1, messages.get('dialog.errorviewer.column.description'), wx.LIST_AUTOSIZE)
        lst.SetColumnWidth(0, 80)
        lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, lst)
        return lst

    def OnItemActivated(self, event):
        event.Skip()
        stepIdx = self.getItemSelected()
        if stepIdx == -1 or stepIdx == None:
            return
        grideditor.getDefault().getEditor().setStepSelected(stepIdx)
        return

    def getItemSelected(self):
        itemIndex = -1
        while True:
            itemIndex = self.list.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            return self.stepIndices[itemIndex]

        return -1

    def clear(self):
        self.list.DeleteAllItems()
        del self.stepIndices[0:]

    def OnClose(self, event):
        self.showing = False
        self.control.Hide()

    def dispose(self):
        self.control.Hide()
        self.control.Destroy()

    def show(self):
        self.showing = False
        self.control.Show()
        self.control.Raise()

    def hide(self):
        self.showing = False
        self.control.Hide()

    def isShowing(self):
        return self.showing


class ShowErrorViewerAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, owner):
        poi.actions.Action.__init__(self, 'Error Viewer')
        self.owner = owner
        self.setImage(images.getImage(images.ERROR_VIEWER_OK))
        self.setDisabledImage(images.getImage(images.ERROR_VIEWER_FAILURE))

    def run(self):
        self.owner.toggleView()


class ValidationListener(object):
    __module__ = __name__

    def __init__(self):
        self.view = None
        validator.getDefault().addValidationListener(self)
        return

    def toggleView(self):
        if self.view is None:
            return
        if self.view.isShowing():
            self.view.hide()
        else:
            self.view.show()
        return

    def validationEvent(self, valid, errors):
        wx.CallAfter(self.internalValidationEvent, valid, errors)

    def internalValidationEvent(self, valid, errors):
        if not valid:
            self.action.setImage(images.getImage(images.ERROR_VIEWER_FAILURE))
        else:
            self.action.setImage(images.getImage(images.ERROR_VIEWER_OK))
        tbm = ui.getDefault().getToolBarManager()
        tbm.update(True)

    def create(self):
        self.createActions()
        self.view = ErrorViewer()
        self.view.createControl(ui.getDefault().getMainFrame().getControl())

    def createActions(self):
        action = ShowErrorViewerAction(self)
        self.action = action
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.addItem(poi.actions.ActionContributionItem(action))
        mng.update()
        tbm = ui.getDefault().getToolBarManager()
        tbm.addItem(poi.actions.Separator())
        tbm.addItem(poi.actions.ActionContributionItem(action))
        tbm.update(True)

    def __del__(self):
        self.view.dispose()


def init():
    dbg = ValidationListener()
    dbg.create()
