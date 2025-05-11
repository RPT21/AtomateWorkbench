# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/utils/caching.py
# Compiled at: 2004-10-01 23:57:40
import struct
MEGABYTE = 1048576

class Cache(object):
    __module__ = __name__

    def __init__(self, max, typedef):
        self.typedef = typedef
        self.max = max
        self.formatChar = self.getTypeFormatChar(typedef)
        self.multiplier = struct.calcsize('f%c' % self.formatChar)
        self.cache = []
        self.indexer = []

    def clear(self):
        self.cache = []
        self.indexer = []

    def addvalue(self, time, value):
        inttime = int(time)
        if len(self.indexer) <= inttime:
            diff = inttime - len(self.indexer)
            self.indexer.extend(list(map((lambda x: 0), list(range(diff + 1)))))
            self.indexer[inttime] = len(self.cache)
        self.cache.append((time, value))

    def print_time(self):
        print((self.indexer))
        print('---')
        print((self.cache))

    def getvalueindex(self, time):
        return self.indexer[int(time)]

    def getvalue(self, index):
        return self.cache[index]

    def getTypeFormatChar(self, typedef):
        return {(type(int)): 'I', (type(int)): 'L', (type(float)): 'f'}[typedef]
