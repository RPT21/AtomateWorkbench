# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/graphview/src/graphview/__init__.py
# Compiled at: 2004-11-16 18:55:55
import ui, poi.views, wx, kernel.plugin, kernel.pluginmanager as PluginManager, grideditor, logging, ui.context, graphview.images as images, graphview.messages as messages, executionengine, executionengine.engine, graphview.view, threading, labbooks
VIEW_ID = 'graphview.view'
logger = logging.getLogger('graphview')
instance = None

def getDefault():
    global instance
    return instance


class GraphViewPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        self.panelViewFactories = {}
        instance = self
        self.model = None
        self.groups = {}
        ui.getDefault().setSplashText('Loading Graph View plugin ...')
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        images.init(contextBundle)
        messages.init(contextBundle)
        ui.context.addContextChangeListener(self)

    def contextChanged(self, event):
        key = event.getKey()
        value = event.getNewValue()
        if key == 'recipe':
            if value is None:
                if self.model is None:
                    return
                self.model.removeModifyListener(self)
                self.disposeGroups()
            else:
                self.model = grideditor.getDefault().getEditor().getInput()
                self.model.addModifyListener(self)
                self.prepareInput()
        return

    def prepareInput(self):
        for device in self.model.getDevices():
            self.prepareGroupDevice(device)

    def disposeGroups(self):
        for types in self.groups.keys():
            self.groups[types].dispose()
            del self.groups[types]

    def recipeModelChanged(self, event):
        if event.getEventType() not in (event.CHANGE_DEVICE, event.REMOVE_DEVICE, event.ADD_DEVICE):
            return
        self.updatePanelGroups(event.getEventType(), event.getDevice())

    def prepareGroupDevice(self, device):
        deviceType = device.getType()
        if not self.hasDeviceGroup(deviceType):
            if not self.createDeviceGroup(deviceType):
                return
        self.addDeviceToGroup(device)

    def updatePanelGroups(self, eventType, device):
        deviceType = device.getType()
        if eventType is grideditor.recipemodel.ADD_DEVICE:
            self.prepareGroupDevice(device)
        if eventType is grideditor.recipemodel.CHANGE_DEVICE:
            if not self.hasDeviceGroup(deviceType):
                return
            self.updateDeviceGroup(device)
        if eventType is grideditor.recipemodel.REMOVE_DEVICE:
            if not self.hasDeviceGroup(deviceType):
                return
            self.removeDeviceFromGroup(device)

    def updateDeviceGroup(self, device):
        self.groups[device.getType()].updateDevice(device)

    def removeDeviceFromGroup(self, device):
        deviceType = device.getType()
        group = self.groups[deviceType]
        group.removeDevice(device)

    def addDeviceToGroup(self, device):
        deviceType = device.getType()
        group = self.groups[deviceType]
        group.addDevice(device)

    def createDeviceGroup(self, deviceType):
        if not self.panelViewFactories.has_key(deviceType):
            return False
        panel = ui.getDefault().getMainFrame().getPerspective('run').getGraphPanel()
        group = self.panelViewFactories[deviceType](self, panel)
        self.groups[deviceType] = group
        return True

    def destroyDeviceGroup(self, deviceType):
        self.groups[deviceType].dispose()
        del self.groups[deviceType]

    def hasDeviceGroup(self, deviceType):
        return self.groups.has_key(deviceType)

    def registerViewFactory(self, id, factory):
        self.panelViewFactories[id] = factory

    def engineInit(self, engine):
        logger.debug('Engine init, creating graph views ...')
        self.engine = engine
        engine.addEngineListener(self)

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)
        persp = ui.getDefault().getMainFrame().getPerspective('run')
        logger.debug('Creating stuff in %s' % threading.currentThread())


class PanelView(labbooks.RunLogParticipant):
    __module__ = __name__

    def __init__(self, owner, panel):
        labbooks.RunLogParticipant.__init__(self)
        labbooks.getDefault().registerDeviceParticipant(self)
        self.owner = owner
        self.devices = []
        self.panel = panel

    def addDevice(self, device):
        self.devices.append(device)

    def removeDevice(self, device):
        self.devices.remove(device)

    def updateDevice(self, device):
        pass

    def saveSnapshot(self, runlog):
        pass

    def dispose(self):
        labbooks.getDefault().deregisterParticipant(self)

    def getRunLogHeaders(self, devices):
        return []

    def handleEngineEvent(self, event, runlog):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.saveSnapshot(runlog)


# global VIEW_ID ## Warning: Unused global
