# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/help/src/help/frame.py
# Compiled at: 2004-11-23 08:00:49
import wx, wx.html, configparser, time, logging
logger = logging.getLogger('help.controller')

class BookControl(wx.TreeCtrl):
    __module__ = __name__

    def __init__(self, parent, owner):
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.TR_NO_LINES | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_TWIST_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_SINGLE | wx.TR_HAS_BUTTONS | wx.SIMPLE_BORDER)
        self.owner = owner
        self.AddRoot('[help]')
        self.root = self.GetRootItem()
        self.books = {}
        self.nodes = {}
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)

    def OnSelChanged(self, event):
        event.Skip()
        nodeID = event.GetItem()
        data = self.GetPyData(nodeID)
        book = self.getBook(nodeID)
        self.owner.navigateToNode(book, data)

    def getBook(self, nodeID):
        data = self.GetPyData(nodeID)
        item = nodeID
        while not isinstance(data, Book) and item.m_pItem != self.root.m_pItem:
            item = self.GetItemParent(item)
            data = self.GetPyData(item)

        return data

    def addBook(self, book):
        self.books[book.getId()] = book
        wx.CallAfter(self.internalAddBook, book)

    def internalAddBook(self, book):
        bid = self.AppendItem(self.root, book.getTitle())
        i = self.GetCount()
        self.SetPyData(bid, book)
        for chapter in book.getChapters():
            cid = self.AppendItem(bid, chapter['title'])
            self.SetPyData(cid, chapter)
            for section in chapter['sections']:
                sid = self.AppendItem(cid, section['title'])
                self.SetPyData(sid, section)

        self.Refresh()


class ContentControl(wx.html.HtmlWindow):
    __module__ = __name__

    def __init__(self, parent, owner):
        wx.html.HtmlWindow.__init__(self, parent, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.SIMPLE_BORDER)
        self.owner = owner
        if 'gtk2' in wx.PlatformInfo:
            self.NormalizeFontSizes()

    def OnLinkClicked(self, linkinfo):
        logger.debug('Link Clicked: %s' % linkinfo.GetHref())
        self.base_OnLinkClicked(linkinfo)

    def OnSetTitle(self, title):
        self.base_OnSetTitle(title)
        self.owner.setTitle(title)


class HelpFrame(wx.Frame):
    __module__ = __name__

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent)
        self.__titlePrefix = 'Help Frame'
        self.__setTitle(None)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.split = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH)
        self.tree = BookControl(self.split, self)
        self.content = ContentControl(self.split, self)
        sizer.Add(self.split, 1, wx.GROW | wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        (w, h) = (
         600, 600)
        try:
            screenw = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_X)
            w = screenw - screenw / 3
            h = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y) - 100
        except Exception as msg:
            logger.exception(msg)

        self.SetSize(wx.Size(w, h))
        self.split.SplitVertically(self.tree, self.content, w / 3)
        self.SetPosition(wx.Point(0, 0))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.show()
        self.books = {}
        return

    def OnKey(self, event):
        event.Skip()
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.hide()

    def OnClose(self, event):
        if not event.CanVeto():
            event.Skip()
            return
        self.hide()

    def show(self):
        self.Show()
        self.Raise()

    def hide(self):
        self.Hide()

    def navigateToNode(self, book, data):
        sid = None
        if isinstance(data, Book):
            sid = data.indexid
        elif 'id' not in data:
            logger.debug('No id specified for book %s' % book.getTitle())
            return
        sid = data['id']
        items = book.getItems()
        if sid not in items:
            logger.debug('No id %s in book %s' % (sid, book.getTitle()))
            return
        self.showHelpIDWithBook(book.getId(), sid)
        return

    def showHelpID(self, hid):
        if hid.find(':') < 0:
            hid = 'help:index'
        (bookname, sid) = hid.split(':')
        self.showHelpIDWithBook(bookname, sid)

    def showHelpIDWithBook(self, bookname, sid):
        logger.debug('Going to show book name %s - %s' % (bookname, sid))
        if bookname not in self.books:
            bookname = 'help'
        book = self.books[bookname]
        logger.debug('Showing book: %s' % book.path)
        filepath = ''
        if sid in book.getItems():
            filepath = book.getItems()[sid]
        fp = 'file:%s#zip:%s' % (book.path, filepath)
        self.content.LoadPage(fp)

    def setTitle(self, title):
        wx.CallAfter(self.__setTitle, title)

    def __setTitle(self, title):
        s = '%s - %s' % (self.__titlePrefix, title)
        if title is None:
            s = '%s' % self.__titlePrefix
        self.SetTitle(s)
        return

    def addBook(self, bookpath):
        book = Book(bookpath)
        self.books[book.getId()] = book
        self.tree.addBook(book)


class Book(object):
    __module__ = __name__

    def __init__(self, bookpath):
        self.path = bookpath
        self.fh = wx.FileSystem()
        props = self.fh.OpenFile('file:%s#zip:book.props' % bookpath)
        if props is None:
            raise Exception('Not a properly formatted help file: %s' % bookpath)
        cp = configparser.ConfigParser()

        class Wrap(object):
            __module__ = __name__

            def __init__(self, fh):
                self.fh = fh

            def readline(self):
                x = self.fh.readline()
                if x.find('\x08') >= 0:
                    x = x.replace('\x08', '')
                return x

        cp.readfp(Wrap(props.GetStream()), bookpath)
        self.title = cp.get('book', 'title')
        self.id = cp.get('book', 'bookid')
        self.indexid = cp.get('book', 'id')
        self.chapters = []
        self.items = {}
        self.parseProps(cp)
        return

    def parseProps(self, props):
        numchapters = int(props.get('book', 'numchapters'))
        for i in range(1, numchapters + 1):
            chtitle = 'chapter.%d' % i
            cid = None
            if props.has_option(chtitle, 'id'):
                cid = props.get(chtitle, 'id')
            chapter = {'id': cid, 'sections': [], 'title': (props.get(chtitle, 'title'))}
            self.chapters.append(chapter)
            try:
                numsections = int(props.get('chapter.%d' % i, 'numsections'))
                sections = []
                chapter['sections'] = sections
                for j in range(1, numsections + 1):
                    seclabel = 'chapter.%d.section.%d' % (i, j)
                    section = {'id': None, 'title': (props.get(seclabel, 'title'))}
                    if props.has_option(seclabel, 'id'):
                        section['id'] = props.get(seclabel, 'id')
                    sections.append(section)

            except Exception as msg:
                print(('msg:', msg))

        items = props.items('ids')
        for (key, val) in items:
            self.items[key] = val

        return

    def getTitle(self):
        return self.title

    def getItems(self):
        return self.items

    def getChapters(self):
        return self.chapters

    def getFH(self):
        return self.fh

    def getId(self):
        return self.id
