# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/help/src/help/__init__.py
# Compiled at: 2004-11-23 07:30:57
import wx, os, wx.html, ui, kernel.plugin, poi.actions, help.actions, help.frame, help.images as images, help.messages as messages, logging, configparser
import plugins.ui.ui as ui
instance = None
logger = logging.getLogger('help')

def getDefault():
    global instance
    return instance


class HelpPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.controller = None
        self.provider = None
        self.books = []
        instance = self
        ui.getDefault().setSplashText('Loading Help plugin ...')
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        messages.init(contextBundle)
        images.init(contextBundle)
        ui.getDefault().addInitListener(self)
        ui.getDefault().addCloseListener(self)

    def closing(self):
        global logger
        if self.controller is not None:
            logger.debug('Destroying help control')
            self.controller.Destroy()
        return

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)
        helpManager = ui.getDefault().getMenuManager().findByPath('atm.help')
        helpManager.appendToGroup('help-additions-begin', poi.actions.ActionContributionItem(help.actions.HelpContentsAction(self)))
        helpManager.update()
        wx.FileSystem_AddHandler(wx.ZipFSHandler())
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)
        self.loadPredefinedBooks()

    def loadPredefinedBooks(self):
        try:
            config = configparser.RawConfigParser()
            fname = os.path.join(self.contextBundle.dirname, 'default.books')
            config.readfp(open(fname), fname)
        except Exception as msg:
            logger.exception(msg)
            return

        if not config.has_section('books'):
            logger.error("Default books configuration does not have 'books' section")
            return
        for (key, value) in config.items('books'):
            logger.debug("Loading default book '%s'" % value)
            bookname = os.path.join(self.contextBundle.dirname, value)
            self.addBook(bookname)

    def addBook(self, bookPath):
        if bookPath in self.books:
            return
        self.books.append(bookPath)
        if self.controller is None:
            return
        logger.debug('Adding direct book %s to help controller' % bookPath)
        self.controller.addBook(bookPath)
        return

    def addBooks(self):
        for book in self.books:
            try:
                logger.debug("Adding cached book '%s' to help controller" % book)
                self.controller.addBook(book)
            except Exception as msg:
                logger.exception(msg)

    def xcreateController(self):
        self.controller = wx.html.HtmlHelpController()
        self.addBooks()

    def createController(self):
        self.controller = help.frame.HelpFrame()
        self.addBooks()

    def ShowHelp(self):
        focusedWindow = wx.Window_FindFocus()
        logger.debug("Looking for context help for window '%s'" % str(focusedWindow))
        mainFrame = ui.getDefault().getMainFrame().getControl()
        helpText = ''
        if focusedWindow is not None:
            while len(focusedWindow.GetHelpText()) == 0 and focusedWindow != mainFrame:
                focusedWindow = focusedWindow.GetParent()

            helpText = focusedWindow.GetHelpText()
        logger.debug("Will attempt to find help text: '%s'" % helpText)
        if self.controller is None:
            self.createController()
        self.controller.showHelpID(helpText)
        self.controller.show()
        return
