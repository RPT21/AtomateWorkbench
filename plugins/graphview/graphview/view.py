# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/graphview/src/graphview/view.py
# Compiled at: 2004-10-29 21:43:58
import wx, wx.lib.scrolledpanel, copy, plugins.poi.poi.views, logging, threading
import plugins.panelview.panelview.devicemediator
import plugins.panelview.panelview.images as images, plugins.panelview.panelview.messages as messages
import plugins.panelview.panelview.item
import plugins.labbooks.labbooks as labbooks
import plugins.panelview.panelview as panelview
import plugins.poi.poi as poi

logger = logging.getLogger('panelview.viewer')

class ViewerView(labbooks.RunLogParticipant):
    __module__ = __name__

    def __init__(self):
        labbooks.RunLogParticipant.__init__(self)
        self.control = None
        self.statusPanel = None
        panelview.devicemediator.setView(self)
        labbooks.getDefault().registerDeviceParticipant(self)
        return

    def createRunLogHeaders(self, devices):
        pass

    def handleEngineEvent(self, event, runlogFile):
        pass

    def createControl(self, parent):
        self.view = poi.views.StackedView()
        self.view.createControl(parent)
        self.control = wx.lib.scrolledpanel.ScrolledPanel(self.view.getContent(), -1)
        self.control.SetBackgroundColour(wx.WHITE)
        self.control.SetupScrolling()
        self.viewcontrol = self.view.getControl()
        self.view.setTitle(messages.get('view.title'))
        self.view.setTitleImage(images.getImage(images.VIEW_ICON))
        self.panelitems = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        return self.viewcontrol

    def addItem(self, item, refresh=True):
        logger.debug('Add Item: %s creating control in %s' % (item, threading.current_thread()))
        if not item in self.panelitems:
            self.panelitems.append(item)
            sizer = self.control.GetSizer()
            item.createControl(self.control)
            control = item.getControl()
            logger.debug('control size: %s' % control.GetSize())
            sizer.Add(control, 0, wx.EXPAND)
            sizer.RecalcSizes()
            sizer.Layout()
            if refresh:
                wx.CallAfter(self.updateMe)
            logger.debug('past stuffs of refresh')

    def updateMe(self):
        self.control.SetupScrolling()

    def removeItem(self, item, refresh=True):
        logger.debug('Remove item: %s' % item)
        if item in self.panelitems:
            self.panelitems.remove(item)
            try:
                sizer = self.control.GetSizer()
                control = item.getControl()
                self.control.RemoveChild(control)
                sizer.Remove(control)
                sizer.Layout()
            except Exception as msg:
                logger.exception(msg)
            else:
                item.dispose()
                if refresh:
                    wx.CallAfter(self.updateMe)

    def removeAllItems(self):
        items = copy.copy(self.panelitems)
        list(map((lambda p: self.removeItem(p, refresh=False)), self.panelitems))
        wx.CallAfter(self.updateMe)

    def dispose(self):
        items = copy.copy(self.panelitems)
        logger.debug("Disposing panel items: '%s'" % self.panelitems)
        for item in items:
            self.removeItem(item, refresh=False)

        logger.debug("\tLeft over: '%s'" % self.panelitems)

    def setFocus(self, focused):
        self.view.setFocus(focused)

    def getControl(self):
        return self.viewcontrol

    def setEditor(self, editor):
        self.editor = editor

    def getEditor(self):
        return self.editor

    def inputChanged(self, oldInput, newInput):
        if oldInput == newInput:
            return
        if newInput is None:
            return
        if newInput != oldInput and oldInput != None:
            self.removeAllItems()
        model = newInput
        wx.CallAfter(self.internalPrepareNewPanels, model)
        return

    def internalPrepareNewPanels(self, model):
        self.statusPanel = panelview.item.ExecutionStatusPanelItem()
        self.addItem(self.statusPanel, refresh=False)
        panelview.devicemediator.setRecipeModel(model)
        self.updateMe()
