# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/help/src/help/actions.py
# Compiled at: 2004-08-04 10:37:15
import plugins.poi.poi.actions, plugins.help.help.messages as messages, plugins.help.help.images as images
import plugins.poi.poi as poi

class HelpContentsAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, helper):
        poi.actions.Action.__init__(self, messages.get('actions.helpcontents.label'), messages.get('actions.helpcontents.help'), messages.get('actions.helpcontents.help'))
        self.setImage(images.getImage(images.HELP_ENABLED_ICON))
        self.setDisabledImage(images.getImage(images.HELP_DISABLED_ICON))
        self.helper = helper

    def run(self):
        self.helper.ShowHelp()
