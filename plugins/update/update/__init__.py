# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/update/src/update/__init__.py
# Compiled at: 2004-08-02 04:12:16
import lib.kernel.plugin, lib.kernel as kernel

class UpdatePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        super().__init__()
        self.contextBundle = None
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
