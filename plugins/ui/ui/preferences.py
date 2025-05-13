# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/preferences.py
# Compiled at: 2004-08-04 10:40:36


# def pageCmd(a, b): #  Crec que ara ja no es necessita utilitzar dos parametres :D
    # return a.getOrder() - b.getOrder()

def pageCmd(a):
    return a.getOrder()


class InternalManager(object):
    __module__ = __name__

    def __init__(self):
        self.items = {}
        self.pages = []

    def addPage(self, page):
        if not page in self.pages:
            self.pages.append(page)
            self.pages.sort(key=pageCmd)

    def removePage(self, page):
        if page in self.pages:
            self.pages.remove(page)
            self.pages.sort(key=pageCmd)

    def getPages(self):
        return self.pages

    def findPage(self, path):
        for page in self.pages:
            if page.getPath() == path:
                return page

        return None


def init():
    global instance
    instance = InternalManager()


def getDefault():
    global instance
    return instance
