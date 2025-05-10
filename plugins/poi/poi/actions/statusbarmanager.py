# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/actions/statusbarmanager.py
# Compiled at: 2005-06-10 18:51:25
import wx, plugins.ui.ui.images, math, plugins.poi.poi as poi

class StatusBarManager(poi.actions.ContributionManager, poi.actions.ContributionItem):
    __module__ = __name__

    def __init__(self, sid):
        poi.actions.ContributionItem.__init__(self, sid)
        poi.actions.ContributionManager.__init__(self)
        self.widget = None
        return

    def createControl(self, parent):
        mb = wx.StatusBar(parent, -1)
        if not parent in poi.actions.statusBarFrames.keys():
            poi.actions.statusBarFrames[parent] = self
        if isinstance(parent, wx.Frame):
            parent.SetStatusBar(mb)
        mb.shell = parent
        self.widget = mb
        self.defaultContribution = poi.actions.MessageStatusBarContributionItem('default')
        self.addItem(self.defaultContribution)
        self.update(True)
        parent.Bind(wx.EVT_SIZE, self.OnSize, self.widget)
        return self.widget

    def OnSize(self, event):
        event.Skip()
        self.widget.Reposition()

    def findByPath(self, path):
        current = self
        tokens = path.split('/')
        found = False
        for token in tokens:
            for item in current.items:
                if item.getId() == token:
                    current = item
                    found = True
                    break

            if found:
                continue
            return None

        return current
        return

    def setText(self, text):
        self.defaultContribution.setText(text)

    def removeAllItems(self):
        for child in self.widget.GetChildren():
            if id(child) == id(self.defaultContribution.widget):
                continue
            self.widget.Remove(child)
            child.Destroy()

    def update(self, force=False):
        if force:
            self.removeAllItems()
        self.widget.SetFieldsCount(len(self.items))
        statusWidthsCache = []
        for item in self.items:
            statusWidthsCache.append(item.getStatusWidth())
            self.widget.SetStatusWidths(statusWidthsCache)

        i = 0
        for item in self.items:
            if not force and False:
                if not hasattr(item, 'widget'):
                    continue
                widget = item.widget
                self.widget.EnableTool(widget.GetId(), item.isEnabled())
            else:
                item.fillStatusBar(self.widget, i)
            i += 1
