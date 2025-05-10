# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/images.py
# Compiled at: 2004-11-05 01:53:14
import lib.kernel.pluginmanager, os, wx, logging
inited = False
imagesTable = {}
logger = logging.getLogger('resources.ui')
OPEN_RESOURCE = 'open-resource'
VIEW_ICON = 'view-icon'
RECIPE_OPTIONS = 'recipe-options'
ERROR_VIEWER_OK = 'error-viewer-ok'
ERROR_VIEWER_FAILURE = 'error-viewer-failure'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
imagesFilenames = {OPEN_RESOURCE: (os.path.join(ENABLED_DIR_PREFIX, 'openresource.png')), VIEW_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'view_icon.gif')), RECIPE_OPTIONS: (os.path.join(ENABLED_DIR_PREFIX, 'recipe_options.png')), ERROR_VIEWER_OK: (os.path.join(ENABLED_DIR_PREFIX, 'error_list_ok.png')), ERROR_VIEWER_FAILURE: (os.path.join(ENABLED_DIR_PREFIX, 'error_list.png'))}

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
            logger.warning("Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if key in imagesTable:
        return imagesTable[key]
    return None

def dispose():
    pass
