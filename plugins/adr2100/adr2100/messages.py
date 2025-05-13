# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/messages.py
# Compiled at: 2004-08-12 02:18:21
import configparser, os, logging
MESSAGES_FILENAME = 'messages.prop'
inited = False
config = None
logger = logging.getLogger('extendededitor')

def init(contextBundle):
    global MESSAGES_FILENAME
    global config
    global inited
    global logger
    if not inited:
        inited = True
        try:
            config = configparser.RawConfigParser()
            config.read([os.path.join(contextBundle.dirname, MESSAGES_FILENAME)])
        except Exception as msg:
            logger.warning("Unable to load messages from '%s':'%s'" % (contextBundle.dirname, msg))


def get(key):
    try:
        return config.get('messages', key)
    except Exception as msg:
        return '%%%s%%' % key
