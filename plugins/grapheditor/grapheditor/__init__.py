# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grapheditor/src/grapheditor/__init__.py
# Compiled at: 2004-08-09 11:44:20
import lib.kernel.plugin, lib.kernel as kernel
import plugins.grapheditor.grapheditor.images as images
import plugins.grapheditor.grapheditor.messages as messages, logging
import plugins.grapheditor.grapheditor.editor as grapheditor_editor
import plugins.ui.ui as ui
import plugins.poi.poi as poi
import plugins.poi.poi.views as poi_views

VIEW_ID = 'graph.editor'
logger = logging.getLogger('grapheditor')
contributionFactories = {}

def addGraphContributionFactory(deviceType, factory):
    global contributionFactories
    if not deviceType in contributionFactories:
        contributionFactories[deviceType] = factory


def getGraphContributionFactory(deviceType):
    if not deviceType in contributionFactories:
        return None
    return contributionFactories[deviceType]


class GraphEditorPlugin(kernel.plugin.Plugin):
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
        view = GraphEditorView()
        view.createControl(parent)
        return view


class GraphEditorView(poi.views.SectorView):
    __module__ = __name__

    def createControl(self, parent):
        self.viewer = grapheditor_editor.EditorViewer()
        self.viewer.createControl(parent)
        return self.viewer.getControl()

    def setFocus(self, focused):
        self.viewer.setFocus(focused)

    def getControl(self):
        return self.viewer.getControl()

    def getId(self):
        return VIEW_ID

    def getViewer(self):
        return self.viewer
