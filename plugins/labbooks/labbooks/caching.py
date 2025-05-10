# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/labbooks/src/labbooks/caching.py
# Compiled at: 2004-09-30 21:18:13
import stat, sys, os, string, struct
SUFFIX = 'cache'

class CacheFile(object):
    __module__ = __name__

    def __init__(self, filename, f, create=True):
        self.filename = filename
        self.f = open(f.name, 'r')
        self.lastSecond = -1
        self.cache = self.openCache(filename, create)
        self.structSize = struct.calcsize('L')

    def getCachedFilename(self, filename):
        return '%s.%s' % (filename, SUFFIX)

    def openCache(self, filename, create):
        cacheFilename = self.getCachedFilename(filename)
        docreate = False
        if not os.path.exists(cacheFilename):
            if not create:
                raise Exception('No cache file found titled %s for %s' % (cacheFilename, filename))
            docreate = True
        return self.createCacheFile(cacheFilename, docreate)

    def createCacheFile(self, filename, create):
        mode = 'ab+'
        if create:
            mode = 'wb+'
        f = open(filename, mode)
        return f

    def getSecondOffset(self, second):
        offset = long(int(second)) * self.structSize
        fs = long(os.stat(self.cache.name)[stat.ST_SIZE])
        if offset >= fs:
            return None
        self.cache.seek(offset)
        s = self.cache.read(self.structSize)
        lineoffset = struct.unpack('L', s)[0]
        return lineoffset
        return

    def markSecond(self, second):
        offset = self.f.tell()
        intsec = int(second)
        if self.lastSecond == intsec:
            return
        self.lastSecond = intsec
        packed = struct.pack('L', long(offset))
        self.cache.write(packed)

    def close(self):
        self.cache.close()
        self.f.close()
