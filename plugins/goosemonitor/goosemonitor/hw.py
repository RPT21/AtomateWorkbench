# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/goosemonitor/src/goosemonitor/hw.py
# Compiled at: 2005-06-21 21:49:37
import threading, goosemonitor, goosemonitor.userinterface, logging, hardware.hardwaremanager, urllib.request, urllib.parse, urllib.error, time, copy, xml.dom.minidom

class RefreshThread(threading.Thread):
    __module__ = __name__

    def __init__(self, refreshInterval, callee):
        threading.Thread.__init__(self)
        self.refreshInterval = refreshInterval
        self.callee = callee
        self.setDaemon(True)
        self.done = False

    def run(self):
        while not self.done:
            try:
                self.callee.refreshData()
            except Exception as msg:
                print(('EXCEPTION: ', msg))

            time.sleep(self.refreshInterval)


class GooseMonitorHardware(hardware.hardwaremanager.Hardware):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaremanager.Hardware.__init__(self)
        self.logger = logging.getLogger('goosemonitorHardware')
        self.opener = None
        self.configured = False
        self.refreshThread = None
        self.listeners = []
        self.fields = {}
        self.devices = {}
        self.name = ''
        return

    def addGooseListener(self, listener):
        if not listener in self.listeners:
            self.listeners.append(listener)

    def removeGooseListener(self, listener):
        if not listener in self.listeners:
            return
        self.listeners.remove(listener)

    def fireGooseUpdate(self, error, extra=None):
        myListeners = copy.copy(self.listeners)
        for listener in myListeners:
            listener.gooseUpdate(self, error, extra)

    def dispose(self):
        hardware.hardwaremanager.Hardware.dispose(self)

    def checkDriver(self):
        pass

    def getDeviceName(self):
        return self.name

    def getFields(self):
        return self.fields

    def getDevices(self):
        return self.devices

    def getAndParseData(self, url):
        if self.opener is None:
            self.opener = urllib.request.FancyURLopener({})
        try:
            source = self.opener.open(url).read()
        except Exception as msg:
            self.logger.exception(msg)
            self.fireGooseUpdate(goosemonitor.ERROR_RETRIEVING, str(msg))
            return goosemonitor.ERROR_RETRIEVING

        try:
            doc = xml.dom.minidom.parseString(source)
            serverNode = doc.documentElement
            devicesNode = serverNode.getElementsByTagName('devices')[0]
            devNodes = devicesNode.getElementsByTagName('device')
            for node in devNodes:
                did = node.getAttribute('id')
                dobj = {}
                dobj['name'] = node.getAttribute('name')
                dobj['type'] = node.getAttribute('type')
                fieldNodes = node.getElementsByTagName('field')
                fields = {}
                for fieldnode in fieldNodes:
                    key = fieldnode.getAttribute('key')
                    value = fieldnode.getAttribute('value')
                    niceName = fieldnode.getAttribute('niceName')
                    min = fieldnode.getAttribute('min')
                    max = fieldnode.getAttribute('max')
                    fields[key] = {'value': value, 'name': niceName, 'min': min, 'max': max}

                dobj['fields'] = fields
                self.devices[did] = dobj

            if False:
                deviceNode = devicesNode.getElementsByTagName('device')[0]
                self.name = deviceNode.getAttribute('name')
                fieldsNodes = devicesNode.getElementsByTagName('field')
                newFields = {}
                for node in fieldsNodes:
                    key = node.getAttribute('key')
                    value = node.getAttribute('value')
                    niceName = node.getAttribute('niceName')
                    min = node.getAttribute('min')
                    max = node.getAttribute('max')
                    newFields[key] = {'value': value, 'name': niceName, 'min': min, 'max': max}
                    self.fields = copy.copy(newFields)

        except Exception as msg:
            self.logger.exception(msg)
            self.fireGooseUpdate(goosemonitor.ERROR_PARSING, str(msg))
            return goosemonitor.ERROR_PARSING

        self.fireGooseUpdate(goosemonitor.ERROR_OK)
        return goosemonitor.ERROR_OK

    def refreshData(self):
        if not self.configured:
            return
        self.getAndParseData(self.url)

    def initialize(self):
        config = self.description.getConfiguration()
        try:
            self.url = config.get('main', 'url').strip()
            self.interval = int(config.get('main', 'requestinterval').strip())
            self.logger.debug("Goose Monitor URL is: '" + self.url + "'")
            if not self.url == '':
                self.configured = True
        except Exception as msg:
            self.logger.exception(msg)

        if self.configured:
            self.startRefreshThread()
        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()

    def startRefreshThread(self):
        self.refreshThread = RefreshThread(self.interval, self)
        self.refreshThread.start()

    def shutdown(self):
        print('goosemonitor shutdown')
        if self.refreshThread is not None:
            if self.refreshThread.isAlive():
                self.refreshThread.done = True
        self.status = hardware.hardwaremanager.STATUS_STOPPED
        self.fireHardwareStatusChanged()
        return

    def setupDriver(self, description):
        print('goosemonitor setup driver')

    def dispose(self):
        hardware.hardwaremanager.Hardware.dispose(self)
        print('goosemonitor dispose')
