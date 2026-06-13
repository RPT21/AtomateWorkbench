# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/panelview/src/panelview/view.py
# Compiled at: 2004-11-23 19:48:35
import wx, copy, plugins.poi.poi.views, logging, threading, plugins.panelview.panelview.devicemediator
import plugins.panelview.panelview.item, wx.lib.scrolledpanel
import plugins.panelview.panelview.devicemediator as panelview_devicemediator

logger = logging.getLogger('panelview.viewer')


def _isDestroyed(window):
    if window is None:
        return True
    if hasattr(wx, 'IsDestroyed'):
        try:
            return wx.IsDestroyed(window)
        except Exception:
            return True
    return False


def _safeCallAfter(func, *args, **kwargs):
    """Safely call wx.CallAfter with exception handling for destroyed windows"""
    def wrapper():
        try:
            return func(*args, **kwargs)
        except RuntimeError:
            # Widget was destroyed, silently ignore
            pass
        except Exception as msg:
            # Log but don't block, especially during shutdown
            try:
                logger.debug(f"Callback exception: {msg}")
            except:
                pass
    
    return wx.CallAfter(wrapper)

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
                if _isDestroyed(self.win):
                    return
                try:
                    sizer = self.win.GetSizer()
                    if sizer is None:
                        return
                    for item in self.view.panelitems:
                        panel = item.getControl()

                    sizer.Layout()
                except RuntimeError:
                    return
                except Exception:
                    return

        self.panelitems = []
        self._sizeHandler = SizeHandler(self.control, self)
        self.control.PushEventHandler(self._sizeHandler)
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
        if _isDestroyed(self.control):
            return
        if not item in self.panelitems:
            self.panelitems.append(item)
            sizer = self.control.GetSizer()
            item.createControl(self.control, self.horizontal)
            control = item.getControl()
            if _isDestroyed(control):
                return
            logger.debug('control size: %s' % control.GetSize())
            sizer.Add(control, 0, wx.EXPAND | wx.RIGHT, 3)
            if refresh:
                _safeCallAfter(self.updateMe)

    def updateMe(self, event=None):
        if event is not None:
            event.Skip()
        if _isDestroyed(self.control):
            return
        try:
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
                if not _isDestroyed(control):
                    control.SetSize((width, -1))

            self.control.SetupScrolling()
        except RuntimeError:
            return
        return

    def removeItem(self, item, refresh=True):
        logger.debug('Remove item: %s' % item)
        if item in self.panelitems:
            self.panelitems.remove(item)
            if not _isDestroyed(self.control):
                try:
                    sizer = self.control.GetSizer()
                    control = item.getControl()
                    self.control.RemoveChild(control)
                    sizer.Remove(control)
                    sizer.Layout()
                except Exception as msg:
                    logger.exception(msg)
            item.dispose()
            if refresh and not _isDestroyed(self.control):
                _safeCallAfter(self.updateMe)

    def removeAllItems(self):
        items = copy.copy(self.panelitems)
        for item in items:
            self.removeItem(item, refresh=False)

        if not wx.IsMainThread():
            _safeCallAfter(self.updateMe)
        else:
            self.updateMe()

    def dispose(self):
        items = copy.copy(self.panelitems)
        logger.debug("Disposing panel items: '%s'" % self.panelitems)
        for item in items:
            self.removeItem(item, refresh=False)

        if self.control is not None and hasattr(self, '_sizeHandler') and self._sizeHandler is not None:
            try:
                if not _isDestroyed(self.control):
                    self.control.PopEventHandler(False)
            except Exception:
                pass
            self._sizeHandler = None

        # Destroy the control
        if self.control is not None:
            try:
                if not _isDestroyed(self.control):
                    self.control.Destroy()
            except Exception:
                pass
            self.control = None

        logger.debug("\tLeft over: '%s'" % self.panelitems)
        plugins.panelview.panelview.devicemediator.removeView(self)

    def setFocus(self, focused):
        if not focused or _isDestroyed(self.control):
            return
        try:
            self.control.SetFocus()
        except RuntimeError:
            return

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
        _safeCallAfter(self.internalPrepareNewPanels, model)
        return

    def internalPrepareNewPanels(self, model):
        if _isDestroyed(self.control):
            return
        try:
            panelview_devicemediator.setRecipeModel(model)
            self.updateMe()
        except RuntimeError:
            return
        except Exception as msg:
            logger.exception(msg)
