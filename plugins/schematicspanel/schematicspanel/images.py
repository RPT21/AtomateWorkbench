# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/schematicspanel/src/schematicspanel/images.py
# Compiled at: 2004-08-09 11:44:20
import kernel.pluginmanager, os, wx
inited = False
imagesTable = {}
VIEW_ICON = 'view-icon'
ICONS_DIR_PREFIX = 'icons'
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
imagesFilenames = {VIEW_ICON: (os.path.join(TOOLS_DIR_PREFIX, 'schematicspanel_icon.gif'))}

def init(contextBundle):
    global imagesFilenames
    global imagesTable
    global inited
    if inited:
        return
    inited = True
    for (key, filename) in list(imagesFilenames.items()):
        try:
            imagesTable[key] = wx.Bitmap(os.path.join(contextBundle.dirname, filename))
        except Exception as msg:
            print(("* ERROR: Could not load '%s' for '%s': '%s'" % (filename, key, msg)))


def getImage(key):
    if key in imagesTable:
        return imagesTable[key]
    return None


def dispose():
    pass
