# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/images.py
# Compiled at: 2005-06-10 18:51:25
import kernel.pluginmanager, os, wx, logging
inited = False
imagesTable = {}
logger = logging.getLogger('poi')
ERROR_ICON = 'error-icon'
WARNING_ICON_32 = 'warning-icon-32'
TOOLBAR_SEPARATOR_IMAGE = 'toolbar-separator'
DIALOG_ERROR_ICON = 'dialog-error-icon'
DIALOG_WARNING_ICON = 'dialog-warning-icon'
DIALOG_INFO_ICON = 'dialog-info-icon'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
imagesFilenames = {ERROR_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'error.gif')), WARNING_ICON_32: (os.path.join(TOOLS_DIR_PREFIX, 'dialog_warning_icon_32x32.png')), TOOLBAR_SEPARATOR_IMAGE: (os.path.join(TOOLS_DIR_PREFIX, 'toolbar_separator.png')), DIALOG_ERROR_ICON: (os.path.join(TOOLS_DIR_PREFIX, 'dialog_error_icon.png')), DIALOG_WARNING_ICON: (os.path.join(TOOLS_DIR_PREFIX, 'dialog_warning_icon.png')), DIALOG_INFO_ICON: (os.path.join(TOOLS_DIR_PREFIX, 'dialog_info_icon.png'))}

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
            logger.warn("Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if imagesTable.has_key(key):
        return imagesTable[key]
    return None
    return


def dispose():
    pass
