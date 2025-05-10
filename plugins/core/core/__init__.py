# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/__init__.py
# Compiled at: 2005-06-28 20:46:42
import kernel.plugin, kernel.pluginmanager as PluginManager
_cond_contrib = []

def addConditionalContribution(contrib):
    global _cond_contrib
    if contrib in _cond_contrib:
        return
    _cond_contrib.append(contrib)


def removeConditionalContribution(device):
    ctr = None
    for contrib in _cond_contrib:
        ctr = contrib
        if contrib.device is device:
            break

    print('remove contrib:', ctr)
    if ctr is not None:
        _cond_contrib.remove(ctr)
    return


def getConditionalContributions():
    return _cond_contrib


class CorePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)

    def startup(self, contextBundle):
        pass
