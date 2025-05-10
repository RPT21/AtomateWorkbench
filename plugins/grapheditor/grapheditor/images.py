# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grapheditor/src/grapheditor/images.py
# Compiled at: 2004-08-10 09:09:42
import kernel.pluginmanager, os, wx
inited = False
imagesTable = {}
ZOOM_SMALL = 'zoom-small'
ZOOM_LARGE = 'zoom-large'
RESIZE_WE = 'resize-we'
VIEW_ICON = 'view-icon'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
imagesFilenames = {ZOOM_SMALL: (os.path.join(TOOLS_DIR_PREFIX, 'small_zoom.png')), ZOOM_LARGE: (os.path.join(TOOLS_DIR_PREFIX, 'large_zoom.png')), RESIZE_WE: (os.path.join(TOOLS_DIR_PREFIX, 'resize_we.png')), VIEW_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'grapheditor_icon.gif'))}

def init(contextBundle):
    global imagesFilenames
    global imagesTable
    global inited
    if inited:
        return
    inited = True
    for (key, filename) in imagesFilenames.items():
        try:
            imagesTable[key] = wx.Bitmap(os.path.join(contextBundle.dirname, filename))
        except Exception, msg:
            print "* ERROR: Could not load '%s' for '%s': '%s'" % (filename, key, msg)


def getImage(key):
    if imagesTable.has_key(key):
        return imagesTable[key]
    return None
    return


def dispose():
    pass
