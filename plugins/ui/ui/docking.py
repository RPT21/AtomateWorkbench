# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/docking.py
# Compiled at: 2004-10-30 02:13:25
import wx

class DockingWindow(wx.Window):
    __module__ = __name__

    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.parent = parent
        self.originalParent = parent
        self.init()
        self.childWindow = None
        return

    def init(self):
        pass

    def split(self, withWindow, direction, dividerLocation):
        if withWindow == self.childWindow:
            raise Exception("can't split window with self!")
        sw = SplitWindow(self.getParentWindow())
        sw.setWindows(self, withWindow)
        self.getParentWindow().replaceChildWindow(self, sw)
        return sw

    def getRootWidow(self):
        if self.parent is not None:
            return self.parent.getRootWindow()
        return None

    def getChildWindowCount(self):
        return 0

    def getChildWindow(self, index):
        return None

    def getWindowParent(self):
        return self.parent

    def setWindowParent(self, parent):
        if self.parent == parent:
            return
        oldRoot = self.getRootWindow()
        if self.parent is not None:
            pass
        self.parent = parent
        newRoot = self.getRootWindow()
        return

    def doReplace(self, oldWindow, newWindow):
        raise Exception('poo!')

    def doRemoveWindow(self, window):
        raise Exception('Cho!')

    def getContentWindow(self, parent):
        return self

    def replaceChildWindow(self, oldWindow, newWindow):
        nw = newWindow.getContentWindow(self)
        if nw.getWindowParent() is not None:
            nw.getWindowParent().removeChildWindow(nw)
        nw.setWindowParent(self)
        oldWindow.setWindowParent(None)
        self.doReplace(oldWindow, nw)
        return

    def removeChildWindow(self, window):
        window.setParentWindow(None)
        self.doRemoveWindow(window)
        return

    def addWindow(self, window):
        if window is None:
            return
        w = window.getContentWindow(self)
        oldParent = w.getWindowParent()
        if oldParent is not None:
            oldParent.removeChildWindow(w)
        w.setParentWindow(self)
        return w
        return


class RootWindow(DockingWindow):
    __module__ = __name__

    def init(self):
        DockingWindow.init(self)
        self.SetBackgroundColour(wx.RED)
        self.window = None
        self.views = []
        self.Bind(wx.EVT_SIZE, self.OnSize)
        return

    def OnSize(self, event):
        event.Skip()
        if self.window is not None:
            self.window.SetSize(self.GetSize())
        return

    def getChildWindowCount(self):
        return 1

    def getChildWindow(self, index):
        return self.window

    def addView(self, view):
        if not view in self.views:
            self.views.append(view)

    def removeView(self, view):
        if view in self.views:
            self.views.remove(view)

    def doReplace(self, oldWindow, newWindow):
        if oldWindow == newWindow:
            if self.window is None:
                pass
        return

    def setWindow(self, window):
        if self.window == window:
            return
        if self.window == None:
            self.doReplace(None, self.addWindow(window))
        elif window is None:
            self.removeChildWindow(self.window)
            self.window = None
        else:
            self.replaceChildWindow(self.window, window)
        return

    def replaceChildWindow(self, oldWindow, newWindow):
        if self.window != oldWindow:
            return
        old = self.window
        self.setWindow(newWindow)
        old.Destroy()


class View(DockingWindow):
    __module__ = __name__

    def init(self):
        DockingWindow.init(self)
        self.SetBackgroundColour(wx.GREEN)
        self.component = None
        self.contentPanel = wx.Panel(self)
        self.contentPanel.SetSizer(wx.BoxSizer())
        self.contentPanel.SetAutoLayout(True)

        class SizeHandler(wx.EvtHandler):
            __module__ = __name__

            def __init__(self, owner):
                wx.EvtHandler.__init__(self)
                owner.PushEventHandler(self)
                self.Bind(wx.EVT_SIZE, owner.viewOnSize)

        SizeHandler(self)
        return

    def viewOnSize(self, event):
        event.Skip()
        self.contentPanel.SetSize(self.GetSize())

    def setComponent(self, component):
        sizer = self.contentPanel.GetSizer()
        if len(self.contentPanel.GetChildren()) > 0:
            for child in self.contentPanel.GetChildren():
                self.contentPanel.Remove(child)
                sizer.Remove(child)

        component.Reparent(self.contentPanel)
        sizer.Add(component)


class SplitWindow(DockingWindow):
    __module__ = __name__

    def init(self):
        DockingWindow.init(self)
        self.SetBackgroundColour(wx.BLUE)
        self.leftWindow = None
        self.rightWindow = None
        self.splitPane = wx.SplitterWindow(self)
        return

    def setWindows(self, leftWindow, rightWindow):
        self.leftWindow = leftWindow
        self.rightWindow = rightWindow
        if leftWindow or rightWindow is None:
            if leftWindow is not None:
                self.parent.replaceChildWindow(self, leftWindow)
            elif rightWindow is not None:
                self.parent.replaceChildWindow(self, rightWindow)
            else:
                nv = View(self.parent)
                self.parent.replaceChildWindow(self, nv)
            return
        self.leftWindow.setWindowParent(self)
        self.rightWindow.setWindowParnet(self)
        self.splitPane.SplitVertically(self.leftWindow, self.rightWindow, 0)
        return


if __name__ == '__main__':

    class SimApp(wx.App):
        __module__ = __name__

        def OnInit(self):
            f = wx.Frame(None, -1, 'Docking Window Test', size=wx.Size(300, 300), pos=wx.Point(100, 100))
            root = RootWindow(f)
            self.viewOne = View(root)
            self.labelOne = wx.StaticText(self.viewOne, -1, 'One')
            self.viewOne.setComponent(self.labelOne)
            buttons = wx.Panel(f)
            bsizer = wx.BoxSizer()
            sp1 = wx.Button(buttons, -1, 'Split View 1')
            sp2 = wx.Button(buttons, -1, 'Split Root')
            bsizer.Add(sp1, 0, wx.EXPAND | wx.ALL, 5)
            bsizer.Add(sp2, 0, wx.EXPAND | wx.ALL, 5)
            buttons.SetSizer(bsizer)
            buttons.SetAutoLayout(True)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(root, 1, wx.EXPAND)
            sizer.Add(buttons, 0, wx.EXPAND)
            f.SetSizer(sizer)
            f.SetAutoLayout(True)
            f.Show()
            return True


    def OnSplit(self, event):
        if self.split:
            pass


    app = SimApp(redirect=None)
    app.MainLoop()
