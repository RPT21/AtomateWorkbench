# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/panelview/src/panelview/__init__.py
# Compiled at: 2004-11-04 19:42:53
import ui, poi.views, kernel.plugin, kernel.pluginmanager as PluginManager, logging, ui.context, panelview.images as images, panelview.messages as messages, panelview.view
VIEW_ID = 'panelview.view'
logger = logging.getLogger('panelview')
instance = None

def getDefault():
    global instance
    return instance


class PanelViewPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        self.panelViewFactories = {}
        instance = self
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        images.init(contextBundle)
        messages.init(contextBundle)

    def engineInit(self, engine):
        logger.debug('Engine init, creating views ...')
        self.engine = engine
        engine.addEngineListener(self)

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)

    def handlePartInit(self, part):
        global VIEW_ID
        ui.getDefault().removeInitListener(self)
        ui.getDefault().registerViewProvider(VIEW_ID, self)

    def createView(self, viewID, parent):
        view = PanelView()
        view.createControl(parent)
        return view


class PanelView(poi.views.SectorView):
    __module__ = __name__

    def createControl(self, parent, horizontal=True):
        self.viewer = panelview.view.ViewerView(horizontal)
        self.viewer.createControl(parent)
        return self.viewer.getControl()

    def getControl(self):
        return self.viewer.getControl()

    def setFocus(self, focused):
        pass

    def getId(self):
        return VIEW_ID

    def getViewer(self):
        return self.viewer

    def dispose(self):
        self.viewer.dispose()
