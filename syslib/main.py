# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../main.py
# Compiled at: 2005-07-11 23:40:38
import sys, base, os
print 'pid:', os.getpid()
sys.path.insert(0, 'syslib')
sys.path.insert(0, 'lib')
import kernel.boot

def init():
    kernel.boot.boot()


if __name__ == '__main__':
    init()
