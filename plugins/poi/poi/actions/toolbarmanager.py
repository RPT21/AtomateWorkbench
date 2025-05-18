# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/actions/toolbarmanager.py
# Compiled at: 2005-06-10 18:51:25
import wx, logging, plugins.poi.poi as poi

logger = logging.getLogger('poi.toolbarmanager')

class ToolBarManager(poi.actions.ContributionManager, poi.actions.ContributionItem):
    __module__ = __name__

    def __init__(self, title, sid):
        poi.actions.ContributionItem.__init__(self, sid)
        poi.actions.ContributionManager.__init__(self)
        self.widget = None
        self.title = title
        return

    def createControl(self, parent, text_style=0):
        mb = wx.ToolBar(parent, -1, style=wx.TB_FLAT | text_style)
        if isinstance(parent, wx.Frame):
            parent.SetToolBar(mb)
        mb.shell = parent
        self.widget = mb
        self.update(True)
        self.widget.Bind(wx.EVT_TOOL_ENTER, self.OnToolEnter, self.widget)
        return self.widget

    def OnToolEnter(self, event):
        frames = poi.actions.statusBarFrames
        if isinstance(self.widget.shell, wx.Frame):
            return
        if self.widget.shell not in frames:
            return
        sbm = frames[self.widget.shell]
        realitem = None
        for item in self.items:
            if not hasattr(item, 'widget'):
                continue
            if item.widget.GetId() == event.GetSelection():
                realitem = item
                break

        text = ''
        if realitem is not None:
            text = realitem.action.getDescription()
        sbm.setText(text)
        wx.CallAfter(sbm.update)
        return

    def remove(self, item):
        poi.actions.ContributionManager.remove(self, item)
        if hasattr(item, 'widget'):
            self.widget.DeleteTool(item.widget.GetId())

    def removeAllItems(self):
        if wx.Platform not in ['__WXGTK__']:
            self.widget.ClearTools()
        for item in self.items:
            try:
                if hasattr(item, 'widget'):
                    if not isinstance(item.widget, wx.Control):
                        worked = self.widget.DeleteTool(item.widget.GetId())
                    else:
                        self.widget.RemoveChild(item.widget)
                        item.widget.Destroy()
            except Exception as msg:
                logger.exception(msg)

    def update(self, force=False):
        if force:
            self.removeAllItems()
        for item in self.items:
            if item.isSeparator():
                idx = self.items.index(item)
                if idx == 0:
                    continue
                if self.items[idx - 1].isSeparator():
                    continue
            if not force:
                if not hasattr(item, 'widget'):
                    continue
                widget = item.widget
                if isinstance(item, poi.actions.ActionContributionItem):
                    self.widget.EnableTool(widget.GetId(), item.isEnabled())
            else:
                item.fillToolBar(self.widget)

        if force:
            try:
                self.widget.Realize()
            except Exception as msg:
                print(("* ERROR: Unable to realize toolbar:'%s'" % msg))
