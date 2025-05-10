# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/messages.py
# Compiled at: 2004-11-19 01:58:13
import ConfigParser, kernel.pluginmanager, os
MESSAGES_FILENAME = 'messages.prop'
inited = False
config = None

def init(contextBundle):
    global MESSAGES_FILENAME
    global config
    global inited
    if not inited:
        inited = True
        try:
            config = ConfigParser.SafeConfigParser()
            config.read([os.path.join(contextBundle.dirname, MESSAGES_FILENAME)])
        except Exception, msg:
            print "Unable to load messages from '%s' - '%s'", contextBundle.dirname, msg
            print '\tUsing default messages'


def get(key):
    try:
        return config.get('messages', key)
    except Exception, msg:
        return '%%%s%%' % key
