# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/dialog/preferences.py
# Compiled at: 2004-12-07 10:45:16
import wx, os, sys, string, configparser, logging, lib.kernel, plugins.poi.poi.dialogs as poi_dialogs, plugins.poi.poi.views
import plugins.ui.ui.messages as messages, plugins.ui.ui.images as images, plugins.ui.ui.preferences as ui_preferences
DIALOG_PREFS_FILE = 'prefsdialog.prefs'
logger = logging.getLogger('ui.preferences')

class PreferencesDialog(poi_dialogs.Dialog):
    __module__ = __name__

    def __init__(self):
        poi_dialogs.Dialog.__init__(self)
        self.control = None
        self.setSaveLayout(True)
        self.setStyle(wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.root = None
        self.currentPage = None
        self.canChange = False
        return

    def handleClosing(self, id):
        if id == wx.ID_OK:
            self.removeCurrentPage()
        pages = ui_preferences.getDefault().getPages()
        for page in pages:
            page.handleClosing(id)

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, messages.get('preferences.frame.title'), style=self.getStyle())
        self.tree = self.createTree()
        self.body = self.createBody()
        bodysizer = wx.BoxSizer(wx.HORIZONTAL)
        bodysizer.Add(self.tree, 0, wx.GROW | wx.RIGHT, 5)
        bodysizer.Add(self.body, 1, wx.GROW)
        self.okButton = wx.Button(self.control, -1, 'OK')
        self.okButton.SetDefault()
        self.cancelButton = wx.Button(self.control, wx.ID_CANCEL, 'Cancel')
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.okButton, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        buttonsizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(bodysizer, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(wx.StaticLine(self.control, -1), 0, wx.GROW)
        mainsizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.control.SetSizer(mainsizer)
        self.control.SetAutoLayout(True)
        self.populateTree()
        self.restoreLayout()
        self.control.Bind(wx.EVT_BUTTON, self.OnOKButton, self.okButton)
        self.control.Bind(wx.EVT_BUTTON, self.OnCancelButton, self.cancelButton)
        return poi.dialogs.Dialog.createControl(self, parent)

    def OnOKButton(self, event):
        self.endModal(wx.ID_OK)

    def OnCancelButton(self, event):
        self.endModal(wx.ID_CANCEL)

    def createTree(self):
        treectrl = wx.TreeCtrl(self.control, -1, size=(200, -1), style=wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_SINGLE | wx.TR_HIDE_ROOT | wx.TR_NO_LINES | wx.SUNKEN_BORDER)
        self.root = treectrl.AddRoot('#ROOT')
        self.control.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged, treectrl)
        self.control.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnTreeSelChanging, treectrl)
        return treectrl

    def OnTreeSelChanging(self, event):
        if not self.canChange:
            event.Veto()
            wx.Bell()

    def OnTreeSelChanged(self, event):
        event.Skip()
        item = event.GetItem()
        page = self.tree.GetPyData(item)
        if page != self.currentPage:
            self.setCurrentPage(page)

    def createBody(self):
        body = wx.Panel(self.control, -1)
        banner = wx.Panel(body, -1)
        self.banner = banner

        def bannerresizer(event):
            event.Skip()
            self.layoutBanner()

        banner.Bind(wx.EVT_SIZE, bannerresizer, banner)
        self.messageBanner = wx.Panel(banner, -1, style=wx.SUNKEN_BORDER)
        self.messageBanner.SetBackgroundColour(wx.WHITE)
        self.bannerText = wx.StaticText(self.messageBanner, -1, 'Preferences')
        dlgFont = self.control.GetFont()
        dlgFont.SetWeight(wx.BOLD)
        self.bannerText.SetFont(dlgFont)
        bannerGrade = wx.StaticBitmap(self.messageBanner, -1, images.getImage(images.PREFERENCES_BANNER))
        self.bannerGrade = bannerGrade
        bs = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(self.bannerText, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)
        bs.Add(bannerGrade, 0, wx.ALIGN_CENTRE_VERTICAL)
        self.messageBanner.SetSizer(bs)
        self.messageBanner.SetAutoLayout(True)
        self.errorBanner = wx.Panel(banner, -1, style=wx.SIMPLE_BORDER)
        self.bannerErrorText = wx.StaticText(self.errorBanner, -1, 'Error')
        errorImage = wx.StaticBitmap(self.errorBanner, -1, images.getImage(images.ERROR_ICON))
        bs = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(errorImage, 0, wx.ALIGN_CENTRE_VERTICAL)
        bs.Add(self.bannerErrorText, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)
        self.errorBanner.SetSizer(bs)
        self.errorBanner.SetAutoLayout(True)
        self.errorBanner.Hide()
        banner.SetSize((-1, images.getImage(images.PREFERENCES_BANNER).GetHeight()))
        self.stage = wx.Panel(body, -1)
        self.stage.SetSizer(wx.BoxSizer(wx.VERTICAL))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(banner, 0, wx.GROW | wx.BOTTOM, 10)
        sizer.Add(self.stage, 1, wx.GROW)
        body.SetSizer(sizer)
        body.SetAutoLayout(True)
        return body

    def layoutBanner(self):
        size = self.banner.GetSize()
        gradeheight = images.getImage(images.PREFERENCES_BANNER).GetHeight()
        if self.errorBanner.IsShown():
            self.errorBanner.SetSize((size[0], gradeheight))
        else:
            self.messageBanner.SetSize((size[0], gradeheight))

    def removeCurrentPage(self):
        if self.currentPage is None:
            return
        self.currentPage.handleRemove()
        self.stage.Hide()
        sizer = self.stage.GetSizer()
        for child in self.stage.GetChildren():
            self.stage.RemoveChild(child)
            sizer.Remove(child)
            child.Destroy()

        return

    def setCurrentPage(self, page):
        global logger
        try:
            self.removeCurrentPage()
            self.currentPage = page
            control = page.createControl(self.stage)
            page.setOwner(self)
            page.handleShowing()
            sizer = self.stage.GetSizer()
            sizer.Add(control, 1, wx.GROW | wx.ALL)
            sizer.Layout()
            self.setBannerText(page.getTitle())
            self.stage.Show()
        except Exception as msg:
            logger.exception(msg)

    def setDefaultText(self):
        text = 'Preferences'
        if self.currentPage is not None:
            text = self.currentPage.getTitle()
        self.setBannerText(text)
        return

    def setBannerErrorText(self, text):
        if text is None:
            self.setDefaultText()
            return
        self.bannerErrorText.SetLabel(text)

        def updateMe():
            self.messageBanner.Hide()
            self.errorBanner.Show()
            self.layoutBanner()

        wx.CallAfter(updateMe)
        return

    def setBannerText(self, text):
        self.bannerText.SetLabel(text)

        def updateMe():
            self.messageBanner.Show()
            self.errorBanner.Hide()
            self.layoutBanner()

        wx.CallAfter(updateMe)

    def populateTree(self):
        pages = ui.preferences.getDefault().getPages()
        idx = 0
        for page in pages:
            data = wx.TreeItemData()
            data.SetData(page)
            self.tree.AppendItem(self.root, page.getTitle(), data=data)
            idx += 1

    def getMementoID(self):
        global DIALOG_PREFS_FILE
        return DIALOG_PREFS_FILE

    def fillLayoutMemento(self, memento):
        size = self.control.GetSize()
        memento.set('layout', 'size', '%s,%s' % (size[0], size[1]))
        memento.add_section('selection')
        memento.set('selection', 'selected-node', 'None')

    def createDefaultLayout(self):
        scrsize = (
         wx.SystemSettings_GetMetric(wx.SYS_SCREEN_X), wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y))
        preferred = (800, 600)
        rw = max(scrsize, preferred)
        if rw == preferred:
            rw = (
             400, 450)
        else:
            rw = preferred
        self.control.SetSize(rw)
        self.control.CentreOnScreen()

    def updateButtons(self):
        if self.currentPage.canPressOK():
            self.okButton.Enable()
            self.canChange = True
        else:
            self.okButton.Disable()
            self.canChange = False

    def restoreLayoutFromMemento(self, memento):
        try:
            size = list(map(int, tuple(memento.get('layout', 'size').split(','))))
        except Exception as msg:
            size = (
             600, 600)

        try:
            selectedNode = memento.get('selection', 'selected-node')
        except Exception as msg:
            selectedNode = 'none'

        pages = ui.preferences.getDefault().getPages()
        page = None
        if pages > 0:
            page = pages[0]
        if selectedNode.lower() is not 'none':
            found = ui.preferences.getDefault().findPage(selectedNode)
            if found is not None:
                page = found
        if page is not None:
            self.setCurrentPage(page)
        self.control.SetSize(size)
        self.control.CentreOnScreen()
        return


class PreferencesPage(object):
    __module__ = __name__

    def __init__(self, preferencesStore):
        self.dirty = False
        self.control = None
        self.preferencesStore = preferencesStore
        self.owner = None
        self.okToProceed = False
        return

    def getPreferencesStore(self):
        return self.preferencesStore

    def getTitle(self):
        return ''

    def createControl(self, parent):
        pass

    def setError(self, text):
        self.owner.setBannerErrorText(text)

    def handleShowing(self):
        store = self.getPreferencesStore()
        try:
            self.setData(store.getPreferences())
        except Exception as msg:
            try:
                self.setData(store.getDefaultPreferences())
            except Exception as msg:
                print(('*ERROR:', Exception, msg))

    def setData(self, data):
        pass

    def getData(self, data):
        pass

    def setOwner(self, owner):
        self.owner = owner

    def update(self):
        self.owner.updateButtons()

    def handleRemove(self):
        """Called by dialog when switching to a different page"""
        self.saveIfDirty()

    def handleClosing(self, id):
        """Called by dialog when closing completely, passes OK or CANCEL"""
        if id == wx.ID_CANCEL:
            return
        self.saveIfDirty()

    def saveIfDirty(self):
        if not self.isDirty():
            return
        if not self.canPressOK():
            return
        store = self.getPreferencesStore()
        self.getData(store.getPreferences())
        store.commit()
        self.setDirty(False)

    def isDirty(self):
        return self.dirty

    def setDirty(self, dirty=True):
        self.dirty = dirty

    def setCanPressOK(self, canit):
        self.okToProceed = canit

    def canPressOK(self):
        return self.okToProceed

    def getControl(self):
        return self.control

    def getPath(self):
        return ''

    def getOrder(self):
        return 0
