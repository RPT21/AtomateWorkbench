# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: lib/kernel/pluginmanager.py
# Compiled at: 2004-07-24 10:26:33
_plugins = {}

def getPlugin(name):
    global _plugins
    if not name in _plugins:
        return None
    return _plugins[name]


def addPlugin(name, plugin):
    if not name in _plugins:
        _plugins[name] = plugin


def getPlugins():
    return list(_plugins.values())
