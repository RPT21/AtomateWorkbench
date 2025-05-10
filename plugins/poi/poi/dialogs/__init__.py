# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/dialogs/__init__.py
# Compiled at: 2005-06-10 18:51:25
import plugins.core.core.utils, lib.kernel, wx, os, sys, configparser, plugins.poi.poi.views
import threading, plugins.poi.poi.utils.staticwraptext, plugins.poi.poi.images as images
DIALOG_PREFS_DIR = 'dialogs'

class Dialog(object):
    __module__ = __name__

    def __init__(self):
        self.save_layout = False
        self.style = wx.DEFAULT_DIALOG_STYLE

    def setStyle(self, style):
        self.style = style

    def getStyle(self):
        return self.style

    def createControl(self, parent):
        if self.getSaveLayout():
            self.saveLayout()
        self.control.Bind(wx.EVT_CLOSE, self.OnHandleClose, self.control)

    def OnHandleClose(self, event):
        event.Skip()
        if event.CanVeto():
            if not self.canClose():
                event.Veto()
                return
        self.endModal(wx.ID_CANCEL)

    def canClose(self):
        return True

    def setSaveLayout(self, saveIt):
        self.save_layout = saveIt

    def getSaveLayout(self):
        return self.save_layout

    def getMementoID(self):
        raise Exception('Sub-classes must implemente')

    def getMementoPath(self):
        global DIALOG_PREFS_DIR
        wp = kernel.getMetadataDir()
        path = os.path.join(wp, DIALOG_PREFS_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, self.getMementoID())
        return path

    def getMemento(self):
        try:
            config = ConfigParser.RawConfigParser()
            fullpath = self.getMementoPath()
            config.read([fullpath])
        except Exception as msg:
            print("* ERROR: Cannot create dialog preferences file '%s':" % self.getMementoID(), msg)
            return None

        return config

    def restoreLayout(self):
        memento = None
        try:
            memento = self.getMemento()
            self.restoreLayoutFromMemento(memento)
        except Exception as msg:
            print('Error loading memento:', msg)
            self.createDefaultLayout()

        return

    def restoreLayoutFromMemento(self, memento):
        pass

    def createDefaultLayout(self):
        pass

    def fillLayoutMemento(self, memento):
        """To be implemented by sub-classes to fill out layout prior to saving"""
        pass

    def saveLayout(self):
        config = ConfigParser.RawConfigParser()
        config.add_section('layout')
        self.fillLayoutMemento(config)
        try:
            fullpath = self.getMementoPath()
            f = open(fullpath, 'w')
            config.write(f)
            f.close()
        except Exception as msg:
            print("* ERROR: Could not save dialog preferences '%s':" % self.getMementoID(), msg)

    def dispose(self):
        self.control.Destroy()
        del self.control
        self.control = None
        return

    def showModal(self):
        return self.control.ShowModal()

    def handleClosing(self, id):
        pass

    def endModal(self, id=wx.ID_OK):
        self.handleClosing(id)
        self.control.EndModal(id)


class ProgressDialog(Dialog):
    __module__ = __name__

    def __init__(self, title):
        Dialog.__init__(self)
        self.title = title
        self.totalWork = 100
        self.currentWorkTotal = 0

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, self.title, style=wx.CAPTION)
        self.panel = self.control
        msgp = self.createMessage(self.panel)
        prgp = self.createProgress(self.panel)
        butp = self.createButtons(self.panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(msgp, 0, wx.GROW | wx.ALL, 10)
        sizer.Add(prgp, 0, wx.GROW | wx.ALL, 10)
        sizer.Add(butp, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)
        sizer.Fit(self.panel)
        self.control.SetSize((400, -1))
        Dialog.createControl(self, parent)

    def setTotalWork(self, totalWork):
        self.totalWork = totalWork
        self.progressGroup.SetRange(totalWork)
        self.update()

    def update(self):
        self.control.Refresh()

    def incrementWork(self, units):
        """Increment work by x units"""
        self.currentWorkTotal += units
        self.progressGroup.SetValue(self.currentWorkTotal)

    def createMessage(self, control):
        self.message = wx.StaticText(control, -1, '[message]')
        return self.message

    def createProgress(self, control):
        self.progressGroup = wx.Gauge(control, -1, self.totalWork)
        return self.progressGroup

    def createButtons(self, control):
        panel = wx.Panel(control, -1)
        self.cancelButton = wx.Button(panel, -1, 'Cancel')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.cancelButton, 0, wx.ALL, 10)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        sizer.Fit(panel)
        panel.Bind(wx.EVT_BUTTON, self.OnCancelButton, id=self.cancelButton.GetId())
        return panel

    def endProgress(self, id=wx.ID_OK):
        self.control.EndModal(id)

    def OnCancelButton(self, event):
        event.Skip()
        self.endProgress(wx.ID_CANCEL)


class MessageHeaderDialog(Dialog):
    __module__ = __name__

    def __init__(self, title=None, message=None, info=None, image=None):
        Dialog.__init__(self)
        self.image = image
        self.message = message
        if message is None:
            self.message = ''
        self.info = info
        if info is None:
            self.info = ''
        self.title = title
        if title is None:
            self.title = ''
        if image is None:
            self.image = wx.EmptyBitmap(1, 1)
        return

    def getBody(self):
        return None
        return

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, self.title, style=self.getStyle())
        self.control.Bind(wx.EVT_CLOSE, self.OnClose)
        self.header = self.createHeader()
        self.content = self.createContent(self.control)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.header, 0, wx.GROW)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.GROW)
        sizer.Add(self.content, 1, wx.GROW)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.createBody(self.content)
        Dialog.createControl(self, parent)

    def createHeader(self):
        p = wx.Panel(self.control, -1, size=(300, 56))
        color = wx.WHITE
        p.SetBackgroundColour(color)
        self.descriptionLabel = wx.StaticText(p, -1, '')
        self.messageLabel = wx.StaticText(p, -1, '')
        self.errorMessageLabel = wx.StaticText(p, -1, '')
        self.errorMessageLabel.Hide()
        self.errorIcon = wx.StaticBitmap(p, -1, images.getImage(images.ERROR_ICON))
        self.errorIcon.Hide()
        emptybmp = wx.EmptyBitmap(1, 1)
        self.imageLabel = wx.StaticBitmap(p, -1, self.image)
        font = self.control.GetFont()
        self.descriptionLabel.SetFont(font)
        self.errorMessageLabel.SetFont(font)
        font.SetWeight(wx.BOLD)
        self.messageLabel.SetFont(font)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.messageLabel, 0, wx.GROW | wx.LEFT | wx.TOP | wx.BOTTOM, 10)
        sizer.Add(self.descriptionLabel, 0, wx.GROW | wx.LEFT, 15)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.errorIcon, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        hsizer.Add(self.errorMessageLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 4)
        sizer.Add(hsizer, 0, wx.GROW | wx.LEFT | wx.BOTTOM, 5)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(sizer, 1, wx.GROW | wx.ALL, 0)
        bsizer.Add(self.imageLabel, 0, wx.ALL | wx.ALIGN_BOTTOM, 0)
        p.SetSizer(bsizer)
        p.SetAutoLayout(True)
        bsizer.Fit(p)
        return p

    def createContent(self, parent):
        b = poi.views.OneChildWindow(self.control, -1)
        return b

    def setImage(self, image):
        pass

    def setMessage(self, message):
        msg = message
        if message == None:
            msg = ''
        self.messageLabel.SetLabel(message)
        self.updateHeaderLayout()
        return

    def setErrorMessage(self, message):
        msg = message
        if message is None:
            msg = ''
        self.errorMessageLabel.Show(message is not None)
        self.errorIcon.Show(message is not None)
        self.descriptionLabel.Show(message is None)
        self.errorMessageLabel.SetLabel(msg)
        self.updateHeaderLayout()
        return

    def updateHeaderLayout(self):
        pass

    def internalUpdateLayout(self):
        sizer = self.header.GetSizer()
        sizer.RecalcSizes()
        psizer = self.header.GetParent().GetSizer()
        psizer.SetItemMinSize(self.header, self.header.GetSize())
        psizer.RecalcSizes()
        psizer.Layout()
        self.header.Refresh()

    def setInfo(self, info):
        if info is None:
            info = ''
        self.descriptionLabel.SetLabel(info)
        return

    def OnClose(self, event):
        if self.canClose() or not event.CanVeto():
            if self.getSaveLayout():
                self.saveLayout()
            event.Skip()
            self.closing()
        else:
            event.Veto()

    def closing(self):
        pass

    def canClose(self):
        return True

    def getControl(self):
        return self.control

    def setTitle(self, title):
        self.control.SetTitle(title)

    def showModal(self):
        return self.control.ShowModal()

    def createBody(self, parent):
        raise Exception('Sub-classes must implement')

    def setImage(self, image):
        pass


class ExceptionDialog(wx.Dialog):
    __module__ = __name__

    def __init__(self, parent, exception, title=None):
        dialogstyle = wx.DEFAULT_DIALOG_STYLE
        if title is None:
            title = 'Error'
        wx.Dialog.__init__(self, parent, -1, title, style=dialogstyle)
        sizer = wx.BoxSizer(wx.VERTICAL)
        bmp = None
        try:
            bmp = wx.StaticBitmap(self, -1, images.getImage(images.DIALOG_ERROR_ICON))
        except Exception as msg:
            pass

        errorLabel = wx.StaticText(self, -1, 'Error:')
        font = errorLabel.GetFont()
        font.SetWeight(wx.BOLD)
        errorLabel.SetFont(font)
        vp = wx.Panel(self, -1, size=(200, -1))
        self.valueLabel = poi.utils.staticwraptext.StaticWrapText(vp, -1, '')
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(self.valueLabel, 1, wx.GROW | wx.ALL, 0)
        vp.SetSizer(s)
        vp.SetAutoLayout(True)
        if isinstance(exception, core.utils.WrappedException):
            self.valueLabel.SetLabel(str(exception.getValue()))
        elif isinstance(exception, tuple):
            self.valueLabel.SetLabel(str(exception[1]))
        else:
            self.valueLabel.SetLabel(str(exception))
        self.okButton = wx.Button(self, -1, '&OK')
        if bmp is not None:
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(bmp, 0, wx.ALL, 10)
            vsizer = wx.BoxSizer(wx.VERTICAL)
            vsizer.Add(errorLabel, 0, wx.GROW)
            vsizer.Add(vp, 1, wx.GROW | wx.LEFT, 10)
            hsizer.Add(vsizer, 1, wx.GROW | wx.ALL)
            sizer.Add(hsizer, 1, wx.GROW | wx.ALL, 5)
        else:
            sizer.Add(errorLable, 0, wx.GROW | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
            sizer.Add(vp, 1, wx.GROW | wx.LEFT, 10)
        sizer.Add(self.okButton, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        minWidth = 300
        sizer.Fit(self)
        if self.GetSize()[0] < minWidth:
            self.SetSize((minWidth, self.GetSize()[1]))
        self.CentreOnScreen()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        return

    def OnOK(self, event):
        self.EndModal(wx.ID_OK)
        wx.CallAfter(self.Destroy)


class MessageDialog(wx.Dialog):
    __module__ = __name__

    def __init__(self, parent, message, title, style=wx.OK):
        dialogstyle = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, -1, title, style=dialogstyle)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.createMessageIcon(sizer, style, message)
        self.createButtons(sizer, style)
        self.SetSize((400, 150))
        self.CentreOnScreen()
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def createMessageIcon(self, sizer, style, message):
        icon = self.createIcon(style)
        msg = poi.utils.staticwraptext.StaticWrapText(self, -1, message)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        if icon is not None:
            hsizer.Add(icon, 0, wx.ALIGN_TOP | wx.RIGHT, 10)
        hsizer.Add(msg, 1, wx.ALIGN_TOP | wx.GROW)
        sizer.Add(hsizer, 1, wx.GROW | wx.ALL, 5)
        return

    def createButtons(self, sizer, style):
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        if style & wx.OK:
            b = wx.Button(self, wx.OK, '&OK')
            b.SetDefault()
            b.Bind(wx.EVT_BUTTON, (lambda event: self.onButton(event, wx.ID_OK)))
            hsizer.Add(b, 0, wx.RIGHT, 5)
            b.SetDefault()
            self.SetReturnCode(wx.ID_OK)
        if style & wx.CANCEL:
            b = wx.Button(self, wx.CANCEL, '&Cancel')
            b.Bind(wx.EVT_BUTTON, (lambda event: self.onButton(event, wx.ID_CANCEL)))
            hsizer.Add(b, 0, wx.RIGHT, 5)
        if style & wx.YES:
            b = wx.Button(self, wx.YES, '&Yes')
            b.Bind(wx.EVT_BUTTON, (lambda event: self.onButton(event, wx.ID_YES)))
            hsizer.Add(b, 0, wx.RIGHT, 5)
            b.SetDefault()
        if style & wx.NO:
            b = wx.Button(self, wx.NO, '&No')
            b.Bind(wx.EVT_BUTTON, (lambda event: self.onButton(event, wx.ID_NO)))
            hsizer.Add(b, 0, wx.RIGHT, 5)
        sizer.Add(hsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

    def onButton(self, event, id):
        self.EndModal(id)

    def createIcon(self, style):
        if style & wx.ICON_INFORMATION:
            bmp = images.getImage(images.DIALOG_INFO_ICON)
        elif style & wx.ICON_WARNING:
            bmp = images.getImage(images.DIALOG_WARNING_ICON)
        elif style & wx.ICON_ERROR:
            bmp = images.getImage(images.DIALOG_ERROR_ICON)
        else:
            return None
        icon = wx.StaticBitmap(self, -1, bmp)
        return icon
        return
