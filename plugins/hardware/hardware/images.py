# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/images.py
# Compiled at: 2005-06-10 18:51:17
import kernel.pluginmanager, os, wx, logging
inited = False
imagesTable = {}
logger = logging.getLogger('hardware')
CONFIG_WIZARD = 'config-wiz'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
WIZARDS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'wizban')
imagesFilenames = {CONFIG_WIZARD: (os.path.join(WIZARDS_DIR_PREFIX, 'config_wiz.gif'))}

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
            logger.warn("Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if imagesTable.has_key(key):
        return imagesTable[key]
    return None
    return


def dispose():
    pass
