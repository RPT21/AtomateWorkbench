# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/__init__.py
# Compiled at: 2005-06-10 18:51:26
import lib.kernel.plugin, plugins.poi.poi.images as images, lib.kernel as kernel

class POIPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)

    def startup(self, contextBundle):
        images.init(contextBundle)
