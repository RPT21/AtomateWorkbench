# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/clipboard.py
# Compiled at: 2004-08-05 09:56:34
import wx, pickle
PYTHONDATA_MIME_TYPE = 'py/binary'
PYTHON_OBJECT = PYTHONDATA_MIME_TYPE
TEXT = 'text'
pyDataFormat = wx.CustomDataFormat(PYTHONDATA_MIME_TYPE)
clipboardListeners = []
currentObject = None
objects = {}

class PyClipboardData(object):
    __module__ = __name__

    def __init__(self):
        self.data = None
        return

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data


def addClipboardListeners(listener):
    global clipboardListeners
    if listener not in clipboardListeners:
        clipboardListeners.append(listener)


def removeClipboardListener(listener):
    if listener in clipboardListeners:
        clipboardListeners.remove(listener)


def fireClipboardChangeEvent():
    for listener in clipboardListeners:
        clipboardListeners.clipboardChanged()


def createObject():
    global currentObject
    global objects
    objects.clear()
    currentObject = wx.DataObjectComposite()


def commit():
    wx.TheClipboard.Open()
    success = wx.TheClipboard.SetData(currentObject)
    wx.TheClipboard.Close()
    if success:
        fireClipboardChangeEvent()
    return success


def hasPyObject():
    global pyDataFormat
    return wx.TheClipboard.IsSupported(pyDataFormat)


def hasText():
    return wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT))


def getObject():
    if not hasPyObject():
        return None
    wx.TheClipboard.Open()
    customObject = wx.CustomDataObject(pyDataFormat)
    wx.TheClipboard.GetData(customObject)
    ldata = customObject.GetData()
    wx.TheClipboard.Close()
    obj = pickle.loads(ldata)
    return obj


def getText():
    if not hasText():
        return None
    textObject = wx.TextDataObject()
    wx.TheClipboard.Open()
    wx.TheClipboard.GetData(textObject)
    text = textObject.GetText()
    wx.TheClipboard.Close()
    return text


def setObject(obj):
    customObject = wx.CustomDataObject(pyDataFormat)
    customObject.SetData(pickle.dumps(obj))
    currentObject.Add(customObject)


def setText(text):
    textObject = wx.TextDataObject()
    textObject.SetText(text)
    currentObject.Add(textObject)


# global PYTHON_OBJECT ## Warning: Unused global
