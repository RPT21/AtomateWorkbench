# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/images.py
# Compiled at: 2004-11-19 02:38:25
import lib.kernel.pluginmanager, os, wx
import logging
logger = logging.getLogger('adr2100 logger')
inited = False
imagesTable = {}
SMALL_ICON = 'small-icon'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
imagesFilenames = {SMALL_ICON: (os.path.join(TOOLS_DIR_PREFIX, 'small_icon.gif'))}

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
        except Exception as msg:
            logger.exception(msg)
            logger.error("* ERROR: Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if key in imagesTable:
        return imagesTable[key]
    return None


def dispose():
    pass
