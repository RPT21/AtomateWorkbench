# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/images.py
# Compiled at: 2004-11-11 22:09:04
import kernel.pluginmanager, os, wx
inited = False
imagesTable = {}
RUN_ENABLED = 'run-image-enabled'
RUN_DISABLED = 'run-image-disabled'
ABORT_ENABLED = 'abort-image-enabled'
ABORT_DISABLED = 'abort-image-disabled'
PAUSE_ENABLED = 'run-pause-enabled'
PAUSE_DISABLED = 'run-pause-disabled'
ADVANCE_ENABLED = 'run-advance-enabled'
ADVANCE_DISABLED = 'run-advance-disabled'
RESUME_ENABLED = 'run-resume-enabled'
RESUME_DISABLED = 'run-resume-disabled'
STOP_PURGE_ENABLED = 'stop-purge-enabled'
STOP_PURGE_DISABLED = 'stop-purge-disabled'
ICONS_DIR_PREFIX = 'icons'
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
imagesFilenames = {RUN_ENABLED: (os.path.join(ENABLED_DIR_PREFIX, 'play_icon.png')), RUN_DISABLED: (os.path.join(DISABLED_DIR_PREFIX, 'run.png')), ABORT_ENABLED: (os.path.join(ENABLED_DIR_PREFIX, 'abort.png')), ABORT_DISABLED: (os.path.join(DISABLED_DIR_PREFIX, 'abort.png')), PAUSE_ENABLED: (os.path.join(ENABLED_DIR_PREFIX, 'suspend.gif')), PAUSE_DISABLED: (os.path.join(DISABLED_DIR_PREFIX, 'suspend.gif')), RESUME_ENABLED: (os.path.join(ENABLED_DIR_PREFIX, 'resume.png')), RESUME_DISABLED: (os.path.join(DISABLED_DIR_PREFIX, 'resume.gif')), ADVANCE_ENABLED: (os.path.join(ENABLED_DIR_PREFIX, 'advance.png')), ADVANCE_DISABLED: (os.path.join(DISABLED_DIR_PREFIX, 'advance.gif')), STOP_PURGE_ENABLED: (os.path.join(ENABLED_DIR_PREFIX, 'abort_purge.png')), STOP_PURGE_DISABLED: (os.path.join(DISABLED_DIR_PREFIX, 'stop_purge.gif'))}

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
            print("* ERROR: Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if key in imagesTable:
        return imagesTable[key]
    return None


def dispose():
    pass
