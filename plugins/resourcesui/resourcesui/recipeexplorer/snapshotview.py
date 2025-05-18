# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/snapshotview.py
# Compiled at: 2004-11-19 21:54:36
import wx, time, plugins.poi.poi.views, plugins.poi.poi.utils.scrolledpanel
import plugins.resourcesui.resourcesui.messages as messages
import plugins.poi.poi as poi


class MainLabel(wx.StaticText):
    __module__ = __name__

    def __init__(self, parent, text):
        wx.StaticText.__init__(self, parent, -1, text)
        font = self.GetFont()
        font.SetWeight(wx.BOLD)
        self.SetFont(font)


class ResizableBitmap(wx.Panel):
    __module__ = __name__

    def __init__(self, parent, bitmap):
        self.bitmap = bitmap
        self.image = bitmap.ConvertToImage()
        self.drawbitmap = wx.EmptyBitmap(1, 1)
        wx.Panel.__init__(self, parent, -1)
        self.bs = (1, 1)
        self.sized = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.OnSize(None)
        return

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        (w, h) = self.GetSize()
        bmp = self.drawbitmap
        dc.DrawBitmap(bmp, 0, 0)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, w, h)

    def GetBestSize(self):
        return self.bs

    def OnSize(self, event):
        if event is not None:
            event.Skip()
        (w, h) = self.GetSize()
        nh = int(self.image.GetHeight() * (float(w) / self.image.GetWidth()))
        ni = self.image.Scale(w, nh)
        bmp = wx.BitmapFromImage(ni)
        self.drawbitmap = bmp
        if h != nh:
            self.SetMinSize(wx.Size(w, nh))
            self.GetParent().Refresh()
        self.bs = (w, nh)
        return


class ProjectInfoPane(wx.Panel):
    __module__ = __name__

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=wx.Size(1, 1))
        self.createUI()

    def setProjectInfo(self, project):
        if project is None:
            self.projectNameLabel.SetLabel('')
            self.commentLabel.SetLabel('')
            self.sharedLabel.SetLabel('')
        else:
            self.projectNameLabel.SetLabel(project.getName())
            self.commentLabel.SetLabel(project.getDescription().getComment())
            msg = 'No'
            if project.isShared():
                msg = 'Yes'
            self.sharedLabel.SetLabel(msg)
        return

    def createUI(self):
        self.projectNameLabel = wx.StaticText(self, -1, '')
        self.commentLabel = wx.StaticText(self, -1, '')
        self.sharedLabel = wx.StaticText(self, -1, '')
        sizer = wx.FlexGridSizer(2, 3, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(MainLabel(self, 'Name:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.ADJUST_MINSIZE)
        sizer.Add(self.projectNameLabel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        sizer.Add(MainLabel(self, 'Comment:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.ADJUST_MINSIZE)
        sizer.Add(self.commentLabel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        sizer.Add(MainLabel(self, 'Shared:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.ADJUST_MINSIZE)
        sizer.Add(self.sharedLabel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.sizer = sizer


class VersionInfoPane(wx.Panel):
    __module__ = __name__

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=wx.Size(1, 1))
        self.createUI()

    def setVersionInfo(self, version):
        if version is None:
            self.dateLabel.SetLabel('')
        else:
            self.dateLabel.SetLabel(time.strftime('%m/%d/%Y - %I:%M:%S %p', time.localtime(version.getCreationDate())))
        return

    def createUI(self):
        self.dateLabel = wx.StaticText(self, -1, '')
        fsizer = wx.FlexGridSizer(2, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        fsizer.Add(MainLabel(self, 'Date:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        fsizer.Add(self.dateLabel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(fsizer, 0, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.sizer = sizer


class RunlogInfoPane(wx.Panel):
    __module__ = __name__

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=wx.Size(1, 1))
        self.bmps = []
        self.createUI()
        self.sproks = False

    def clearThumbnails(self):
        for bmp in self.bmps:
            self.RemoveChild(bmp)
            self.sizer.Remove(bmp)
            bmp.Destroy()

        self.bmps = []

    def setRunlogInfo(self, runlog):
        self.clearThumbnails()
        if runlog is None:
            self.dateLabel.SetLabel('')
        else:
            self.dateLabel.SetLabel(time.strftime('%m/%d/%Y - %I:%M:%S %p', time.localtime(runlog.getModificationDate())))
            thumbnails = runlog.getThumbnails()
            for thumbnail in thumbnails:
                bmp = ResizableBitmap(self, thumbnail)
                self.bmps.append(bmp)
                self.sizer.Add(bmp, 0, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE, 3)

        self.sizer.Layout()
        self.Refresh()
        return

    def createUI(self):
        self.dateLabel = wx.StaticText(self, -1, '')
        fsizer = wx.FlexGridSizer(2, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        fsizer.Add(MainLabel(self, 'Date:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        fsizer.Add(self.dateLabel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ADJUST_MINSIZE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = sizer
        sizer.Add(fsizer, 0, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        sizer.Add(MainLabel(self, 'Snapshots'), 0, wx.ALIGN_CENTRE | wx.ADJUST_MINSIZE)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)


class SnapshotView(poi.views.StackedView):
    __module__ = __name__

    def __init__(self):
        poi.views.StackedView.__init__(self)
        self.project = None
        self.version = None
        self.runlog = None
        return

    def setupVersionInfo(self):
        self.versionPanel.setVersionInfo(self.version)
        self.update()

    def setupProjectInfo(self):
        self.projectPanel.setProjectInfo(self.project)
        self.update()

    def setupRunlogInfo(self):
        self.runlogPanel.setRunlogInfo(self.runlog)
        self.update()

    def setVersion(self, version):
        self.version = version
        wx.CallAfter(self.setupVersionInfo)

    def setProject(self, project):
        self.project = project
        wx.CallAfter(self.setupProjectInfo)

    def setRunlog(self, runlog):
        self.runlog = runlog
        wx.CallAfter(self.setupRunlogInfo)

    def clearRunlog(self):
        self.runlog = None
        wx.CallAfter(self.setupRunlogInfo)
        return

    def clearVersion(self):
        self.version = None
        self.runlog = None

        def p():
            self.setupVersionInfo()
            self.setupRunlogInfo()

        wx.CallAfter(p)
        return

    def clear(self):
        self.project = None
        self.version = None
        self.runlog = None

        def p():
            self.setupProjectInfo()
            self.setupVersionInfo()
            self.setupRunlogInfo()

        wx.CallAfter(p)
        return

    def createBody(self, parent):
        self.viewer = poi.utils.scrolledpanel.ScrolledPanel(parent)
        self.viewer.SetupScrolling()
        self.sps = []
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.p1 = wx.Panel(self.viewer, size=wx.Size(1, 1))
        box = wx.StaticBox(self.p1, -1, ' Project ')
        p = ProjectInfoPane(self.p1)
        self.projectPanel = p
        bs = wx.StaticBoxSizer(box, wx.VERTICAL)
        bs.Add(p, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        ps = wx.BoxSizer(wx.VERTICAL)
        ps.Add(bs, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE, 5)
        self.p1.SetSizer(ps)
        self.p1.SetAutoLayout(True)
        sizer.Add(self.p1, 0, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        self.p2 = wx.Panel(self.viewer, size=wx.Size(1, 1))
        box = wx.StaticBox(self.p2, -1, ' Version ')
        p = VersionInfoPane(self.p2)
        self.versionPanel = p
        bs = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.bs = bs
        bs.Add(p, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        ps = wx.BoxSizer(wx.VERTICAL)
        ps.Add(bs, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE, 5)
        self.p2.SetSizer(ps)
        self.p2.SetAutoLayout(True)
        sizer.Add(self.p2, 0, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        self.p3 = wx.Panel(self.viewer, size=wx.Size(1, 1))
        box = wx.StaticBox(self.p3, -1, ' Runlog ')
        p = RunlogInfoPane(self.p3)
        self.runlogPanel = p
        bs = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.bs = bs
        bs.Add(p, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        ps = wx.BoxSizer(wx.VERTICAL)
        ps.Add(bs, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE, 5)
        self.p3.SetSizer(ps)
        self.p3.SetAutoLayout(True)
        sizer.Add(self.p3, 0, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
        self.mainsizer.Add(sizer, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE, 5)
        self.viewer.SetSizer(self.mainsizer)
        self.viewer.SetAutoLayout(True)
        self.mainsizer.Layout()
        self.setTitle(messages.get('views.snapshot.title'))

    def OnButton(self, event):
        if self.prick:
            p = wx.Panel(self.p2, -1, size=wx.Size(20, 400))
            self.bs.Add(p, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE)
            self.stick = p
        else:
            parent = self.stick.GetParent()
            sizer = self.stick.GetContainingSizer()
            parent.RemoveChild(self.stick)
            sizer.Remove(self.stick)
            self.stick.Destroy()
        self.prick = not self.prick
        self.update()

    def update(self):

        def poforit(root):
            root.Layout()
            self.viewer.Refresh()
            self.viewer.SetupScrolling()

        wx.CallAfter(poforit, self.viewer)

    def getViewer(self):
        return self.viewer
