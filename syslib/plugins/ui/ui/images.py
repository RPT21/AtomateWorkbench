# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/images.py
# Compiled at: 2004-11-12 00:27:38
import kernel.pluginmanager, os, wx
inited = False
imagesTable = {}
TRANSPARENT = 'transparent'
TRANSPARENT_16 = 'transparent-16'
PREFERENCES_BANNER = 'preferences-banner'
ERROR_ICON = 'error-icon'
ERROR_ICON_16 = 'error-icon-16'
ENABLED_EDIT_CUT = 'enabled-edit-cut'
ENABLED_EDIT_PASTE = 'enabled-edit-paste'
ENABLED_EDIT_COPY = 'enabled-edit-paste'
ENABLED_EDIT_UNDO = 'enabled-edit-undo'
ENABLED_EDIT_REDO = 'enabled-edit-redo'
ENABLED_EDIT_DELETE = 'enabled-edit-delete'
DISABLED_EDIT_CUT = 'disabled-edit-cut'
DISABLED_EDIT_PASTE = 'disabled-edit-paste'
DISABLED_EDIT_COPY = 'disabled-edit-paste'
DISABLED_EDIT_UNDO = 'disabled-edit-undo'
DISABLED_EDIT_REDO = 'disabled-edit-redo'
SPLASH_BITMAP = 'splash-bitmap'
ICONS_DIR_PREFIX = 'icons'
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
imagesFilenames = {SPLASH_BITMAP: (os.path.join(TOOLS_DIR_PREFIX, 'splash.png')), TRANSPARENT: (os.path.join(TOOLS_DIR_PREFIX, 'transparent.png')), TRANSPARENT_16: (os.path.join(TOOLS_DIR_PREFIX, 'transparent_16.png')), PREFERENCES_BANNER: (os.path.join(TOOLS_DIR_PREFIX, 'prefs_banner.gif')), ERROR_ICON: (os.path.join(ENABLED_DIR_PREFIX, 'error_icon.png')), ERROR_ICON_16: (os.path.join(ENABLED_DIR_PREFIX, 'error_icon_16x16.png')), ENABLED_EDIT_CUT: (os.path.join(ENABLED_DIR_PREFIX, 'cut.png')), ENABLED_EDIT_PASTE: (os.path.join(ENABLED_DIR_PREFIX, 'paste.png')), ENABLED_EDIT_COPY: (os.path.join(ENABLED_DIR_PREFIX, 'copy.png')), ENABLED_EDIT_UNDO: (os.path.join(ENABLED_DIR_PREFIX, 'undo.png')), ENABLED_EDIT_REDO: (os.path.join(ENABLED_DIR_PREFIX, 'redo.png')), ENABLED_EDIT_DELETE: (os.path.join(ENABLED_DIR_PREFIX, 'delete.png')), DISABLED_EDIT_CUT: (os.path.join(DISABLED_DIR_PREFIX, 'cut_edit.gif')), DISABLED_EDIT_PASTE: (os.path.join(DISABLED_DIR_PREFIX, 'paste_edit.gif')), DISABLED_EDIT_COPY: (os.path.join(DISABLED_DIR_PREFIX, 'copy_edit.gif')), DISABLED_EDIT_UNDO: (os.path.join(DISABLED_DIR_PREFIX, 'undo_edit.gif')), DISABLED_EDIT_REDO: (os.path.join(DISABLED_DIR_PREFIX, 'redo_edit.gif'))}

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
