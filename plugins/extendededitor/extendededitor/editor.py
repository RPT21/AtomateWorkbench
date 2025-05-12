# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/editor.py
# Compiled at: 2004-11-19 03:02:18
import wx, traceback, wx.lib.scrolledpanel, poi.views, logging, extendededitor.mediator, extendededitor.mainitem, threading, extendededitor.messages as messages, extendededitor.images as images, copy, poi.utils.scrolledpanel, ui.context, executionengine, executionengine.engine
logger = logging.getLogger('extendededitor')

class EditorViewer(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.editorPanels = []
        self.model = None
        self.mediator = extendededitor.mediator.Mediator(self)
        ui.context.addContextChangeListener(self)
        executionengine.getDefault().addEngineInitListener(self)
        self.engine = None
        self.lastFocusedItem = None
        return

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)
            self.engine = None
        elif event.getType() == executionengine.engine.TYPE_ENTERING_STEP:
            stepindex = self.engine.currentStepIndex
            self.selectStepByIndex(stepindex)
        return

    def selectStepByIndex(self, index):
        step = self.model.getStepAt(index)
        for item in self.editorPanels:
            item.stepSelectionChanged(step)

    def contextChanged(self, event):
        key = event.getKey()
        if key != 'can-edit':
            return
        canedit = event.getNewValue()
        wx.CallAfter(self.updateItemsEnable, canedit)

    def updateItemsEnable(self, enable):
        for item in self.editorPanels:
            if enable:
                item.enable()
            else:
                item.disable()

    def createControl(self, parent):
        self.view = poi.views.StackedView()
        self.view.createControl(parent)
        self.control = poi.utils.scrolledpanel.ScrolledPanel(self.view.getContent(), -1)
        self.control.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.control.SetSizer(self.sizer)
        self.control.SetAutoLayout(True)
        self.control.SetupScrolling()
        self.control.Bind(wx.EVT_CHILD_FOCUS, self.OnFocusChild)
        self.control.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus, self.control)
        self.control.Bind(wx.EVT_SIZE, self.OnSize)
        self.viewcontrol = self.view.getControl()
        self.view.setTitle(messages.get('view.title'))
        self.view.setTitleImage(images.getImage(images.VIEW_ICON))
        return self.viewcontrol

    def OnSize(self, event):
        event.Skip()

    def focusItem(self, item):
        for i in self.editorPanels:
            if i == item:
                i.setFocus(True)
                self.lastFocusedItem = i
            else:
                i.setFocus(False)

    def setFocus(self, focused):
        wasFocused = self.view.isFocused()
        self.view.setFocus(focused)
        if not focused:
            self.focusItem(None)
        else:
            self.focusItem(self.lastFocusedItem)
        return

    def OnSetFocus(self, event):
        event.Skip()

    def OnKillFocus(self, event):
        event.Skip()

    def findItemOfControl(self, ctrl):
        root = ctrl
        itemctrllist = {}
        for i in self.editorPanels:
            itemctrllist[i.getControl()] = i

        i = 0
        while root != self.control and root != None:
            if root in list(itemctrllist.keys()):
                return itemctrllist[root]
            root = root.GetParent()

        return None
        return

    def OnFocusChild(self, event):
        event.Skip()
        item = self.findItemOfControl(event.GetEventObject())
        if item is None:
            return
        self.focusItem(item)
        return

    def setEditor(self, editor):
        self.editor = editor
        editor.addInputChangedListener(self)
        self.inputChanged(None, self.editor.getInput())
        return

    def getEditor(self):
        return self.editor

    def inputChanged(self, oldInput, newInput):
        if oldInput == newInput:
            return
        if newInput is None:
            return
        if oldInput != newInput:
            self.removeAllItems()
        model = newInput
        self.mediator.setRecipeModel(model)
        item = extendededitor.mainitem.MainEditorItem()
        self.insertEditorItem(0, item)
        item.setContainerPanel(self)
        item.setRecipeModel(model)
        self.model = model
        self.update()
        return

    def resizeAllItems(self):
        thissize = self.control.GetClientSize()
        lgs = 0
        for item in self.editorPanels:
            (iw, ih) = item.getBestSize()
            if iw > lgs:
                lgs = iw

        if lgs > thissize[0]:
            finalsize = lgs
        else:
            finalsize = thissize[0]
        for item in self.editorPanels:
            bs = item.getBestSize()
            item.setSize((finalsize, bs[1]))

    def insertEditorItem(self, index, item):
        if item in self.editorPanels:
            return
        self.editorPanels.insert(index, item)
        try:
            self.createItem(item)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to create control for extended editor item '%s':'%s'" % (item, msg))
            return

        self.sizer.Insert(index, item.getControl(), 0, wx.EXPAND | wx.ALL, 5)
        self.update()

    def createItem(self, item):
        item.setContainerPanel(self)
        item.createControl(self.control)
        bs = item.getBestSize()
        item.setSize(bs)

    def addEditorItem(self, item):
        if item in self.editorPanels:
            return
        self.editorPanels.append(item)
        try:
            self.createItem(item)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to create control for extended editor item '%s':'%s'" % (item, msg))
            return

        self.sizer.Add(item.getControl(), 0, wx.EXPAND | wx.ALL, 5)
        self.update()

    def resizeToFit(self):
        self.internalUpdate()

    def update(self):
        self.control.SetupScrolling()

    def internalUpdate(self):
        self.control.SetupScrolling()

    def removeAllItems(self):
        logger.debug('Removing all items')
        items = copy.copy(self.editorPanels)
        for item in items:
            self.removeEditorItem(item, False)

        logger.debug("Leftover: '%s'" % self.editorPanels)
        del items

    def removeEditorItem(self, item, update=True):
        if not item in self.editorPanels:
            return
        ic = item.getControl()
        if ic is None:
            logger.error("No control exists for item '%s'" % item)
            return
        self.control.RemoveChild(ic)
        self.sizer.Remove(ic)
        ic.Destroy()
        self.editorPanels.remove(item)
        item.dispose()
        if update:
            self.update()
        return

    def getControl(self):
        return self.viewcontrol

    def dispose(self):
        ui.context.removeContextChangeListener(self)
        executionengine.getDefault().removeEngineInitListener(self)
        for item in self.editorPanels:
            item.dispose()
