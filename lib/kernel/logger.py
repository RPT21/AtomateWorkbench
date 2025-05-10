# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../lib/kernel/logger.py
# Compiled at: 2004-08-23 08:14:42
import os, sys, logging, logging.config
from logging.handlers import RotatingFileHandler
import traceback
rootLog = None
basicFormat = '%(levelname)s\t%(asctime)s\t%(name)s\t%(thread)d-%(filename)s-%(lineno)d\t%(message)s'

def initDefaultConfig():
    global basicFormat
    global rootLog
    rootLog = logging.getLogger()
    try:
        handler = logging.FileHandler(os.path.join(os.getcwd(), 'errors.log'), 'a')
        formatter = logging.Formatter(basicFormat)
        handler.setFormatter(formatter)
        rootLog.addHandler(handler)
        rootLog.setLevel(logging.NOTSET)
        rootLog.info('Default file logger created')
    except Exception, msg:
        print '* ERROR: Unable to create file formatter.  Defaulting to console!'
        handler = logging.StreamHandler(os.path.join(os.getcwd(), 'errors.log'))
        formatter = logging.Formatter(basicFormat)
        handler.setFormatter(formatter)
        rootLog.addHandler(handler)
        rootLog.setLevel(logging.NOTSET)
        rootLog.info('Default stderr logger created')


def init():
    global rootLog
    try:
        logging.config.fileConfig('logging.cfg')
    except Exception, msg:
        print "* WARNING: Unable to read logging configuration. Using default log configuration with filename 'errors.log'"
        print "\t'%s-%s'" % (Exception, msg)
        initDefaultConfig()
        return

    rootLog = logging.getLogger()
    sys.excepthook = loggingExceptionHook


def loggingExceptionHook(type, value, tb):
    print 'Unhandled exception'
    lst = traceback.format_exception(type, value, tb)
    for e in lst:
        print e

    del tb
