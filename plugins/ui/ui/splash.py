# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/splash.py
# Compiled at: 2004-11-23 19:52:36
import wx, lib.kernel, threading, plugins.ui.ui.images as images
import wx.adv

class SplashPage(wx.adv.SplashScreen):
    __module__ = __name__

    def __init__(self, parent, timeout=True):
        self.img = images.getImage(images.SPLASH_BITMAP)
        (w, h) = (self.img.GetWidth(), self.img.GetHeight())
        wx.adv.SplashScreen.__init__(self, self.img, wx.adv.SPLASH_NO_TIMEOUT | wx.adv.SPLASH_CENTRE_ON_SCREEN, 0, None, -1)
        self.finished = not timeout
        self.internal = False
        self.statustext = ''
        self.timer = None

        def ignored(e):
            pass

        self.Bind(wx.EVT_ERASE_BACKGROUND, self._BkgPaint)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        return

    def OnCloseWindow(self, event):
        if self.internal:
            event.Skip()
            return

    def OnMouse(self, event):
        if not (event.LeftDown() or event.RightDown()):
            return
        if not self.finished:
            return
        event.Skip()
        if self.timer is not None:
            self.timer.cancel()
        self.done()
        return

    def _BkgPaint(self, event):
        dc = event.GetDC()
        self.draw(dc)

    def _OnPaint(self, event):
        dc = wx.ClientDC(self)
        self.draw(dc)

    def forceDraw(self):
        dc = wx.ClientDC(self)
        self.draw(dc)

    def draw(self, dc):
        dc.SetTextForeground(wx.WHITE)
        (w, h) = self.GetSize()
        s = 'Version %d.%d  Build: %d' % (lib.kernel.VERSION_MAJOR, lib.kernel.VERSION_MINOR, lib.kernel.BUILD_INFO[0])
        te = dc.GetTextExtent(s)
        dc.DrawBitmap(self.img, 0, 0)
        dc.DrawText(s, w - (te[0] + 5), 3)
        s = self.statustext
        te = dc.GetTextExtent(s)
        dc.DrawText(s, int((w - (te[0] + 5)) / 2), int(h - (te[1] + 2)))

    def OnActivate(self, event):
        event.Skip()
        if not event.GetActive():
            self.Raise()

    def startTimeout(self):
        self.finished = True
        self.timer = threading.Timer(10.0, self.done)
        self.timer.start()

    def done(self):
        self.internal = True
        wx.CallAfter(self.__internalDone)

    def __internalDone(self):
        self.hide()
        self.Close(True)

    def hide(self):
        self.Hide()

    def show(self):
        self.Show()
        self.Refresh()

    def setStatus(self, text):
        self.statustext = text
        wx.CallAfter(self.Refresh)

    def setVersion(self, version):
        pass

    def setBuild(self, build):
        pass
