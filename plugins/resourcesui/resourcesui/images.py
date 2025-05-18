# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/images.py
# Compiled at: 2004-11-05 00:57:10
import os, wx, logging
inited = False
imagesTable = {}
logger = logging.getLogger('resources.ui')
OPEN_RESOURCE = 'open-resource'
VERSION_ICON = 'version-icon'
PROJECT_ICON = 'project-icon'
SHARED_PROJECT_ICON = 'shared-project-icon'
EXPORT_RUNLOG_ICON = 'export-runlog-icon'
DELETE_ICON = 'delete-icon'
DELETE_VERSION_ICON = 'delete-version-icon'
OPEN_VERSION_ICON = 'open-version-icon'
SHARED_ICON = 'shared-icon'
SHARE_ACTION_ICON = 'share-action-icon'
UNSHARE_ACTION_ICON = 'unshare-action-icon'
CREATE_NEW_VERSION_ICON = 'create-new-version-icon'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
imagesFilenames = {OPEN_RESOURCE: (os.path.join(ENABLED_DIR_PREFIX, 'openresource.png')), VERSION_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'project_icon.png')), PROJECT_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'project_icon.png')), CREATE_NEW_VERSION_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'create_new_version.png')), SHARED_PROJECT_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'shared_icon.png')), EXPORT_RUNLOG_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'export_runlog.png')), DELETE_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'delete.png')), DELETE_VERSION_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'delete_version.png')), OPEN_VERSION_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'open_version.png')), SHARED_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'shared_icon.png')), SHARE_ACTION_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'share.png')), UNSHARE_ACTION_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'unshare.png'))}

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
            logger.warning("Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if key in imagesTable:
        return imagesTable[key]
    return None


def dispose():
    pass
