# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/actions/menumanager.py
# Compiled at: 2005-06-10 18:51:25
import wx, plugins.ui.ui.images, math
from wx import MenuBar, Menu, MenuItem, NewId, EvtHandler, EVT_MENU_OPEN
import plugins.poi.poi as poi

class MenuManager(poi.actions.ContributionManager, poi.actions.ContributionItem):
    __module__ = __name__

    def __init__(self, title, sid):
        poi.actions.ContributionItem.__init__(self, sid)
        poi.actions.ContributionManager.__init__(self)
        self.widget = None
        self.title = title
        return

    def createMenuBar(self, parent):
        mb = MenuBar()
        mb.shell = parent
        self.widget = mb
        self.update()
        parent.SetMenuBar(mb)

        class OpenCloseEvtHandler(EvtHandler):
            __module__ = __name__

            def __init__(innerself):
                EvtHandler.__init__(innerself)
                innerself.Bind(EVT_MENU_OPEN, self.OnMenuOpen)

        parent.PushEventHandler(OpenCloseEvtHandler())

    def createContextMenu(self, parent):
        self.widget = wx.Menu()
        self.widget.shell = parent
        self.update()
        return self.widget

    def OnMenuOpen(self, event):
        event.Skip()
        for item in self.items:
            try:
                getattr(item, 'widget')
            except:
                continue

            if id(item.widget) == id(event.GetMenu()):
                item.update()

    def fillMenu(self, parent):
        if isinstance(parent, MenuBar):
            self.widget = Menu()
            parent.Append(self.widget, self.title)
        elif isinstance(parent, Menu):
            if len(self.items) > 0:
                self.widget = Menu()
                parent.AppendMenu(NewId(), self.title, self.widget)
            else:
                self.widget = MenuItem(None, NewId(), self.title)
                parent.AppendItem(self.widget)
        self.widget.shell = parent.shell
        self.update()
        return

    def update(self):
        if isinstance(self.widget, Menu):
            for wi in self.widget.GetMenuItems():
                self.widget.Delete(wi.GetId())

        if isinstance(self.widget, MenuBar):
            length = self.widget.GetMenuCount()
            for i in range(0, length):
                self.widget.Remove(0)

        fontSize = 0
        lastWidth = 0
        for item in self.items:
            if item.isSeparator():
                idx = self.items.index(item)
                if idx < len(self.items) - 1:
                    if self.items[idx + 1].isSeparator():
                        continue
                if idx == len(self.items) - 1:
                    continue
            item.fillMenu(self.widget)
            if not hasattr(item, 'widget'):
                continue
            if not isinstance(item.widget, MenuItem):
                continue

        lastWidth = -1
        if lastWidth != 0 and False:
            for item in self.items:
                if not hasattr(item, 'widget'):
                    continue
                if not isinstance(item.widget, MenuItem):
                    continue
                if item.widget.GetBitmap().GetWidth() != 0:
                    continue
