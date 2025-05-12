# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resources/src/resources/runlog.py
# Compiled at: 2004-11-02 01:45:16
import wx, lib.kernel, glob, os
from plugins.resources.resources.__init__ import *
logger = logging.getLogger('runlog')
RUNLOG_SUFFIX = '.runlog'

def isRunLog(fullpath):
    global RUNLOG_SUFFIX
    return fullpath.endswith(RUNLOG_SUFFIX)


class RunLog(Resource):
    __module__ = __name__

    def __init__(self, number):
        Resource.__init__(self, number)
        self.dataBuffer = ''

    def create(self):
        lib.kernel.setAtomateGroupID()
        self.runlogFile = open(self.getRunlogFilename(), 'w')
        lib.kernel.resetUserGroupID()

    def getThumbnails(self):
        results = []
        finds = glob.glob('%s/%s*.jpg' % (os.path.dirname(self.location), self.getName()))
        for find in finds:
            try:
                img = wx.Bitmap(find, wx.BITMAP_TYPE_JPEG)
                results.append(img)
            except Exception as msg:
                logger.exception(msg)

        return results

    def getRunlogFilename(self):
        return os.path.join(self.location, self.name + RUNLOG_SUFFIX)

    def appendBuffer(self, data):
        self.dataBuffer += str(data)

    def getFile(self):
        return self.runlogFile

    def writeEndOfLine(self):
        self.dataBuffer += '\n'
        self.runlogFile.write(self.dataBuffer)
        self.runlogFile.flush()
        self.dataBuffer = ''

    def end(self):
        self.runlogFile.write('\n')
        self.runlogFile.flush()
        self.runlogFile.close()
