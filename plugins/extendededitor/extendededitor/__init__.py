# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/__init__.py
# Compiled at: 2004-10-08 00:47:07
import plugins.poi.poi.views, lib.kernel.plugin, logging
import plugins.extendededitor.extendededitor.images as images
import plugins.extendededitor.extendededitor.messages as messages
import plugins.ui.ui as ui
import lib.kernel as kernel
import plugins.poi.poi as poi
import plugins.extendededitor.extendededitor.editor as editor

VIEW_ID = 'extendededitor.editor'
logger = logging.getLogger('extendededitor')
contributionFactories = {}

def addContributionFactory(deviceType, factory):
    if not deviceType in contributionFactories:
        contributionFactories[deviceType] = factory


def getContributionFactory(deviceType):
    if deviceType in contributionFactories:
        return contributionFactories[deviceType]
    return None


class ExtendedEditorPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        ui.getDefault().setSplashText('Loading Extended Editor plugin ...')
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
        view = ExtendedEditorView()
        view.createControl(parent)
        return view


class ExtendedEditorView(poi.views.SectorView):
    __module__ = __name__

    def createControl(self, parent):
        self.viewer = editor.EditorViewer()
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

    def dispose(self):
        self.viewer.dispose()
