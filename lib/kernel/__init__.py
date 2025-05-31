# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../lib/kernel/__init__.py
# Compiled at: 2005-07-11 23:42:46
import os, traceback, sys, pwdpy
VERSION_MAJOR = 2
VERSION_MINOR = 2
BUILD_INFO = 0
METADATA_DIR = '.metadata'
WORKBENCH_HIDDEN_DIR = '.atomate'

def getSite():
    return os.getcwd()


def getLocalSite():
    dirp = None
    if sys.platform == 'win32':
        dirp = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
    else:
        dirp = os.path.join(os.environ['HOME'])
    dirp = os.path.join(dirp, WORKBENCH_HIDDEN_DIR)
    if not os.path.exists(dirp):
        os.makedirs(dirp)
    return dirp


def getMetadataDir():
    global METADATA_DIR
    path = os.path.join(getSite(), METADATA_DIR)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def getPluginWorkspacePath(pluginId):
    path = os.path.join(getSite(), METADATA_DIR, pluginId)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def debugDumpStack():
    traceback.print_stack()


def setNiceMask():
    """Set the mask for all created files/directories to be writable by all"""
    os.umask(0)


def getGroupID():
    return pwdpy.getpwnam(os.environ['USER'])[3]


def resetUserGroupID():
    if sys.platform.find('linux') < 0:
        return
    gid = getGroupID()
    os.setgid(gid)


def setAtomateGroupID():
    if sys.platform.find('linux') < 0:
        return
    setNiceMask()
