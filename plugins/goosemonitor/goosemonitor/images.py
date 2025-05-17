# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/goosemonitor/src/goosemonitor/images.py
# Compiled at: 2005-06-22 19:41:30
import os, wx, logging
logger = logging.getLogger('goosemonitor')
inited = False
imagesTable = {}
STATUS_VIEW_FAILURE_ICON = 'status-failure-icon'
STATUS_VIEW_NORMAL_ICON = 'status-normal-icon'
SHOW_VIEW_ICON = 'show-view-icon'
STATUS_DEVICE_STATUS_NORMAL = 'status-device-normal-icon'
STATUS_DEVICE_STATUS_ERROR = 'status-device-error-icon'
STATUS_DEVICE_STATUS_NONE = 'status-device-none-icon'
ICONS_DIR_PREFIX = 'icons'
TOOLS_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'tools')
DISABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'disabled')
ENABLED_DIR_PREFIX = os.path.join(ICONS_DIR_PREFIX, 'enabled')
ONOFF_DEVICE_STATUS_UNKNOWN = 'onoff-device-status-unknown'
ONOFF_DEVICE_STATUS_ON = 'onoff-device-status-on'
ONOFF_DEVICE_STATUS_OFF = 'onoff-device-status-off'
imagesFilenames = {SHOW_VIEW_ICON: (os.path.join(TOOLS_DIR_PREFIX, 'goosemonitor_icon.png')),
                   STATUS_DEVICE_STATUS_NORMAL: (os.path.join(TOOLS_DIR_PREFIX, 'status_normal.png')),
                   STATUS_DEVICE_STATUS_ERROR: (os.path.join(TOOLS_DIR_PREFIX, 'status_error.png')),
                   STATUS_DEVICE_STATUS_NONE: (os.path.join(TOOLS_DIR_PREFIX, 'status_none.png')),
                   ONOFF_DEVICE_STATUS_UNKNOWN: (os.path.join(TOOLS_DIR_PREFIX, 'button_unknown.png')),
                   ONOFF_DEVICE_STATUS_ON: (os.path.join(TOOLS_DIR_PREFIX, 'button_on.png')),
                   ONOFF_DEVICE_STATUS_OFF: (os.path.join(TOOLS_DIR_PREFIX, 'button_off.png'))}

def init(contextBundle):
    global imagesFilenames
    global imagesTable
    global inited
    global logger
    if inited:
        return
    inited = True
    for (key, filename) in list(imagesFilenames.items()):
        try:
            imagesTable[key] = wx.Bitmap(os.path.join(contextBundle.dirname, filename))
        except Exception as msg:
            logger.exception(msg)
            logger.error("Could not load '%s' for '%s': '%s'" % (filename, key, msg))


def getImage(key):
    if key in imagesTable:
        return imagesTable[key]
    return None


def dispose():
    pass
