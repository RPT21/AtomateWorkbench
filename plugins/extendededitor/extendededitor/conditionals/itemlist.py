# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/conditionals/itemlist.py
# Compiled at: 2004-12-08 05:13:15
import wx, ui, extendededitor.conditionals.editor, extendededitor.messages as messages

class ConditionalListItem(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.step = None
        self.recipe = None
        self.tests = []
        return

    def setRecipe(self, recipe):
        self.recipe = recipe

    def setStep(self, step):
        self.step = step
        if step is not None:
            self.populateList()
        return

    def populateList(self):
        self.clearTests()
        self.tests = self.step.getConditionals()
        idx = 0
        for test in self.tests:
            self.listCtrl.InsertStringItem(idx, test.getName())
            idx += 1

    def clearTests(self):
        self.listCtrl.DeleteAllItems()

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        self.control.SetBackgroundColour(parent.GetBackgroundColour())
        self.listCtrl = self.createList()
        self.editButton = wx.Button(self.control, -1, messages.get('exted.conditional.edit.label'))
        font = self.control.GetFont()
        font.SetWeight(wx.BOLD)
        label = wx.StaticText(self.control, -1, messages.get('exted.conditionals.label'))
        label.SetFont(font)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.GROW | wx.LEFT | wx.BOTTOM, 5)
        sizer.Add(self.listCtrl, 1, wx.GROW | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(self.editButton, 0, wx.ALIGN_RIGHT)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        sizer.Fit(self.control)
        self.editButton.Bind(wx.EVT_BUTTON, self.OnEdit)

    def OnEdit(self, event):
        dlg = extendededitor.conditionals.editor.ConditionalEditor()
        dlg.setStep(self.step)
        dlg.setRecipe(self.recipe)
        dlg.createControl(ui.getDefault().getMainFrame().getControl())
        result = dlg.showModal()
        dlg.dispose()
        self.populateList()

    def createList(self):
        lst = wx.ListCtrl(self.control, -1, size=(-1, 100), style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.SUNKEN_BORDER)
        lst.InsertColumn(0, 'Name')
        return lst

    def getControl(self):
        return self.control
