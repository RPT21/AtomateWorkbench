# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/help/src/help/images.py
# Compiled at: 2004-08-04 10:37:15
import kernel.pluginmanager, os, wx, logging
logger = logging.getLogger('help')
inited = False
imagesTable = {}
HELP_ENABLED_ICON = 'help-icon'
HELP_DISABLED_ICON = 'help-disabled-icon'
ICONS_DIR_PREFIX = 'icons'
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
imagesFilenames = {HELP_ENABLED_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'help.gif')), HELP_DISABLED_ICON: (os.path.join(DISABLED_DIR_PREFIX, 'help.gif'))}

def init(contextBundle):
    global imagesFilenames
    global imagesTable
    global inited
    global logger
    if inited:
        return
    inited = True
    for (key, filename) in imagesFilenames.items():
        try:
            imagesTable[key] = wx.Bitmap(os.path.join(contextBundle.dirname, filename))
        except Exception, msg:
            logger.exception(msg)
            logger.error("Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if imagesTable.has_key(key):
        return imagesTable[key]
    return None
    return


def dispose():
    pass
