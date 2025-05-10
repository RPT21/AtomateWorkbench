# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resources/src/resources/utils/__init__.py
# Compiled at: 2004-09-02 22:15:46
import sys, os
APPNAME = 'AtomateWorkbench'

def getUsersDirectory():
    if sys.platform == 'win32':
        return os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
    else:
        return os.path.join(os.environ['HOME'], APPNAME)


def getUsername():
    if sys.platform == 'win32':
        return os.environ['USERNAME']
    else:
        return os.environ['USER']
