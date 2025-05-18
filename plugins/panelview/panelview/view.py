# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/panelview/src/panelview/view.py
# Compiled at: 2004-11-23 19:48:35
import wx, copy, plugins.poi.poi.views, logging, threading, plugins.panelview.panelview.devicemediator
import plugins.panelview.panelview.item, wx.lib.scrolledpanel
import plugins.panelview.panelview.devicemediator as panelview_devicemediator

logger = logging.getLogger('panelview.viewer')

class ViewerView(object):
    __module__ = __name__

    def __init__(self, horizontal=True):
        self.control = None
        self.statusPanel = None
        self.horizontal = horizontal
        plugins.panelview.panelview.devicemediator.setView(self)
        return

    def createControl(self, parent):
        self.control = wx.lib.scrolledpanel.ScrolledPanel(parent, -1)
        self.control.SetBackgroundColour(wx.WHITE)
        self.control.SetupScrolling()

        class SizeHandler(wx.EvtHandler):
            __module__ = __name__

            def __init__(self, win, view):
                wx.EvtHandler.__init__(self)
                self.Bind(wx.EVT_SIZE, self.OnSize)
                self.win = win
                self.view = view

            def OnSize(self, event):
                event.Skip()
                sizer = self.win.GetSizer()
                for item in self.view.panelitems:
                    panel = item.getControl()

                sizer.Layout()

        self.panelitems = []
        self.control.PushEventHandler(SizeHandler(self.control, self))
        l = wx.VERTICAL
        if self.horizontal:
            l = wx.HORIZONTAL
        sizer = wx.BoxSizer(l)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_SIZE, self.updateMe)
        return self.control

    def addItem(self, item, refresh=True):
        logger.debug('Add Item: %s creating control in %s' % (item, threading.current_thread()))
        if not item in self.panelitems:
            self.panelitems.append(item)
            sizer = self.control.GetSizer()
            item.createControl(self.control, self.horizontal)
            control = item.getControl()
            logger.debug('control size: %s' % control.GetSize())
            sizer.Add(control, 0, wx.EXPAND | wx.RIGHT, 3)
            if refresh:
                wx.CallAfter(self.updateMe)

    def updateMe(self, event=None):
        if event is not None:
            event.Skip()
        width = 80
        if len(self.panelitems) > 0:
            width = self.control.GetClientSize()[0] / len(self.panelitems)
        minwidth = 80
        maxwidth = 200
        if width > maxwidth:
            width = maxwidth
        if width < minwidth:
            width = minwidth
        for item in self.panelitems:
            control = item.getControl()
            control.SetSize((width, -1))

        self.control.SetupScrolling()
        return

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
        for item in items:
            self.removeItem(item, refresh=False)

        if not wx.IsMainThread():
            wx.CallAfter(self.updateMe)
        else:
            self.updateMe()

    def dispose(self):
        items = copy.copy(self.panelitems)
        logger.debug("Disposing panel items: '%s'" % self.panelitems)
        for item in items:
            self.removeItem(item, refresh=False)

        logger.debug("\tLeft over: '%s'" % self.panelitems)
        plugins.panelview.panelview.devicemediator.removeView(self)

    def setFocus(self, focused):
        self.view.setFocus(focused)

    def getControl(self):
        return self.control

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
        if newInput != oldInput and oldInput != None:
            self.removeAllItems()
        if newInput is None:
            return
        model = newInput
        wx.CallAfter(self.internalPrepareNewPanels, model)
        return

    def internalPrepareNewPanels(self, model):
        panelview_devicemediator.setRecipeModel(model)
        self.updateMe()
