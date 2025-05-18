# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/utils/scrolledpanel.py
# Compiled at: 2005-06-10 18:51:25
import wx

class ScrolledPanel(wx.ScrolledWindow):
    """ScrolledPanel fills a "hole" in the implementation of wx.ScrolledWindow,
providing automatic scrollbar and scrolling behavior and the tab traversal
management that wxScrolledWindow lacks.  This code was based on the original
demo code showing how to do this, but is now available for general use
as a proper class (and the demo is now converted to just use it.)
"""
    __module__ = __name__

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL, name='scrolledpanel'):
        wx.ScrolledWindow.__init__(self, parent, -1, pos=pos, size=size, style=style, name=name)
        self.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)

    def SetupScrolling(self, scroll_x=True, scroll_y=True, rate_x=20, rate_y=20):
        """
        This function sets up the event handling necessary to handle
        scrolling properly. It should be called within the __init__
        function of any class that is derived from ScrolledPanel,
        once the controls on the panel have been constructed and
        thus the size of the scrolling area can be determined.

        """
        if not scroll_x:
            rate_x = 0
        if not scroll_y:
            rate_y = 0
        sizer = self.GetSizer()
        if sizer:
            (w, h) = sizer.GetMinSize()
            if rate_x:
                w += rate_x - w % rate_x
            if rate_y:
                h += rate_y - h % rate_y
            self.SetVirtualSize(wx.Size(w, h))
            self.SetSizeHints(w, h)
        self.SetScrollRate(rate_x, rate_y)
        wx.CallAfter(self.Scroll, wx.Point(0, 0))

    def OnChildFocus(self, evt):
        evt.Skip()
        child = evt.GetWindow()
        child = child.FindFocus()
        (sppu_x, sppu_y) = self.GetScrollPixelsPerUnit()
        (vs_x, vs_y) = self.GetViewStart()
        cpos = child.GetPosition()
        csz = child.GetSize()
        cpos = self.ScreenToClient(child.ClientToScreen(cpos))
        (new_vs_x, new_vs_y) = (
         -1, -1)
