# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/schematicspanel/src/schematicspanel/editor.py
# Compiled at: 2004-08-10 09:09:48
import wx, poi.views, logging, schematicspanel.images as images, schematicspanel.messages as messages
logger = logging.getLogger('schematicspanel')

class EditorViewer(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        return

    def createControl(self, parent):
        self.view = poi.views.StackedView()
        self.view.createControl(parent)
        self.control = wx.lib.scrolledpanel.ScrolledPanel(self.view.getContent(), -1)
        self.control.SetBackgroundColour(wx.WHITE)
        self.viewcontrol = self.view.getControl()
        self.view.setTitle(messages.get('view.title'))
        self.view.setTitleImage(images.getImage(images.VIEW_ICON))
        return self.viewcontrol

    def setFocus(self, focused):
        self.view.setFocus(focused)

    def getControl(self):
        return self.viewcontrol
