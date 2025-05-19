# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/schematicspanel/src/schematicspanel/__init__.py
# Compiled at: 2004-08-10 09:09:48
import plugins.poi.poi.views, lib.kernel.plugin, lib.kernel as kernel, logging
import plugins.schematicspanel.schematicspanel.images as images
import plugins.schematicspanel.schematicspanel.messages as messages
import plugins.schematicspanel.schematicspanel.editor as schematicspanel_editor
import plugins.ui.ui as ui
import plugins.poi.poi as poi

VIEW_ID = 'schematicspanel.editor'
logger = logging.getLogger('schematicspanel')

class SchematicsPanelPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        images.init(contextBundle)
        messages.init(contextBundle)

    def handlePartInit(self, part):
        global VIEW_ID
        ui.getDefault().removeInitListener(self)
        ui.getDefault().registerViewProvider(VIEW_ID, self)

    def createView(self, viewID, parent):
        view = SchematicsPanelView()
        view.createControl(parent)
        return view


class SchematicsPanelView(poi.views.SectorView):
    __module__ = __name__

    def createControl(self, parent):
        self.viewer = schematicspanel_editor.EditorViewer()
        self.viewer.createControl(parent)
        return self.viewer.getControl()

    def getControl(self):
        return self.viewer.getControl()

    def setFocus(self, focused):
        self.viewer.setFocus(focused)

    def getId(self):
        return VIEW_ID

    def getViewer(self):
        return self.viewer
