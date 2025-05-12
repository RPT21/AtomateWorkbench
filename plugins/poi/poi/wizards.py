# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/wizards.py
# Compiled at: 2005-06-10 18:51:26
import wx
from plugins.poi.poi.dialogs import MessageHeaderDialog

class Wizard(MessageHeaderDialog):
    __module__ = __name__

    def __init__(self):
        self.pages = {}
        self.buttons = {}
        self.content = None
        self.startingPage = None
        self.currentPage = None
        MessageHeaderDialog.__init__(self)
        return

    def createBody(self, parent):
        self.addPages()
        if len(list(self.pages.items())) > 0:
            self.showPage(self.startingPage)

    def setStartingPage(self, page):
        self.startingPage = page

    def showPage(self, page):
        if self.currentPage is not None:
            self.currentPage.getControl().Hide()
            self.getContent().Hide()
            self.contentSizer.RemoveWindow(self.currentPage.getControl())
        if page.getControl() is None:
            page.createControl(self.getContent())
        self.currentPage = page
        self.contentSizer.Add(page.getControl(), 1, wx.EXPAND | wx.ALL, 0)
        self.setMessage(page.getMessage())
        self.setTitle(page.getTitle())
        self.setInfo(page.getInfo())
        self.contentSizer.Layout()
        page.aboutToShow()
        page.getControl().Show()
        self.getContent().Show()
        self.update()
        return

    def getContent(self):
        return self.content

    def addPages(self):
        pass

    def addPage(self, page):
        self.pages[page.getName()] = page
        page.setWizard(self)

    def getPage(self, pageName):
        if pageName not in self.pages:
            return None
        return self.pages[pageName]

    def setFinish(self, canFinish):
        self.buttons['finish'].Enable(canFinish)
        if canFinish:
            self.buttons['finish'].SetDefault()

    def setTitle(self, title):
        if title is not None:
            self.control.SetTitle(title)
        else:
            self.control.SetTitle('Licensing Wizard')
        return

    def createButtons(self, parent):
        buttonBack = wx.Button(parent, wx.NewId(), '< &Back')
        buttonBack.Enable(False)
        buttonNext = wx.Button(parent, wx.NewId(), '&Next >')
        buttonNext.Enable(False)
        buttonFinish = wx.Button(parent, -1, '&Finish')
        buttonFinish.Enable(False)
        buttonCancel = wx.Button(parent, wx.ID_CANCEL, '&Cancel')
        buttonFinish.Bind(wx.EVT_BUTTON, self.OnClickFinish)
        buttonNext.Bind(wx.EVT_BUTTON, self.OnClickNext)
        buttonBack.Bind(wx.EVT_BUTTON, self.OnClickBack)
        buttonCancel.Bind(wx.EVT_BUTTON, self.OnClickCancel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(buttonBack, 0, wx.ALL, 0)
        sizer.Add(buttonNext, 0, wx.ALL, 0)
        sizer.Add(buttonFinish, 0, wx.LEFT | wx.RIGHT, 5)
        sizer.Add(buttonCancel, 0, wx.ALL, 0)
        self.buttons = {'finish': buttonFinish, 'cancel': buttonCancel, 'next': buttonNext, 'back': buttonBack}
        return sizer

    def OnClickFinish(self, event):
        event.Skip()
        self.currentPage.performFinish()
        self.getControl().EndModal(wx.ID_OK)

    def OnClickNext(self, event):
        nextPage = self.currentPage.getNextPage()
        self.showPage(nextPage)
        event.Skip()

    def OnClickBack(self, event):
        prevPage = self.currentPage.getPreviousPage()
        self.showPage(prevPage)
        event.Skip()

    def OnClickCancel(self, event):
        self.currentPage.performCancel()
        self.getControl().EndModal(wx.ID_CANCEL)
        event.Skip()

    def createContent(self, composite):
        panel = wx.Panel(composite, -1, size=wx.Size(1, 1), style=wx.CLIP_CHILDREN)
        self.content = wx.Panel(panel, -1, size=wx.Size(1, 1), style=wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)
        self.contentSizer = wx.BoxSizer(wx.VERTICAL)
        self.content.SetSizer(self.contentSizer)
        buttons = self.createButtons(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.content, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(wx.StaticLine(panel, -1, style=wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Fit(composite)
        composite.SetSizer(sizer)
        composite.SetAutoLayout(True)
        self.addPages()
        if len(list(self.pages.items())) > 0:
            self.showPage(self.startingPage)
        return panel

    def update(self):
        if self.currentPage is None:
            return
        self.setMessage(self.currentPage.getMessage())
        self.setTitle(self.currentPage.getTitle())
        self.setInfo(self.currentPage.getInfo())
        self.buttons['next'].Enable(self.currentPage.canFlipToNextPage())
        self.buttons['back'].Enable(self.currentPage.getPreviousPage() is not None)
        self.buttons['finish'].Enable(self.currentPage.isPageComplete())
        return

    def fitWizardHeightToPage(self, page):
        sizer = page.getControl().GetSizer()
        if sizer is None:
            sizer = self.getContent().GetSizer()
        minDesiredSize = sizer.CalcMin()
        dlgSize = self.GetSize()
        contentSize = self.getContent().GetSize()
        if minDesiredSize[1] != contentSize[1]:
            delta = minDesiredSize[1] - contentSize[1]
            self.SetSize((dlgSize[0], dlgSize[1] + delta))
            self.CentreOnScreen()
        return


class WizardPage(object):
    __module__ = __name__

    def __init__(self, pageName, title=None, titleImage=None):
        self.pageName = pageName
        self.title = title
        self.info = None
        self.message = None
        self.titleImage = titleImage
        self.control = None
        self.nextPage = None
        self.previousPage = None
        self.pageComplete = False
        self.wizard = None
        self.canFinish = False
        return

    def performFinish(self):
        pass

    def performCancel(self):
        pass

    def aboutToShow(self):
        pass

    def createControl(self, container):
        pass

    def getWizard(self):
        return self.wizard

    def getControl(self):
        return self.control

    def setFinished(self, canFinish):
        self.canFinish = canFinish

    def isFinished(self):
        return self.canFinish

    def canFlipToNextPage(self):
        return self.isFinished() and self.getNextPage() is not None
        return

    def getImage(self):
        return self.titleImage

    def getName(self):
        return self.pageName

    def getNextPage(self):
        return self.nextPage

    def getPreviousPage(self):
        return self.previousPage

    def isPageComplete(self):
        return self.pageComplete

    def setPageComplete(self, complete):
        self.pageComplete = complete
        if self.wizard is not None:
            self.wizard.update()
        return

    def setPreviousPage(self, previousPage):
        self.previousPage = previousPage

    def setNextPage(self, nextPage):
        self.nextPage = nextPage

    def setWizard(self, wizard):
        self.wizard = wizard

    def getMessage(self):
        return self.message

    def setErrorMessage(self, message):
        if self.wizard is not None:
            self.wizard.setErrorMessage(message)
        return

    def setMessage(self, message):
        self.message = message
        if self.wizard is not None:
            self.wizard.setMessage(message)
        return

    def setInfo(self, info):
        self.info = info
        if self.wizard is not None:
            self.wizard.setDescription(info)
        return

    def setDescription(self, description):
        self.setInfo(description)

    def getInfo(self):
        return self.info

    def setTitle(self, title):
        self.title = title
        self.wizard.setTitle(title)

    def getTitle(self):
        return self.title
