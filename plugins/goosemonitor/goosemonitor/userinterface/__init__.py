# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/goosemonitor/src/goosemonitor/userinterface/__init__.py
# Compiled at: 2005-06-22 20:36:49
import os, traceback, copy, wx, string, logging, core.utils, poi.views, poi.dialogs, hardware.userinterface.configurator, hardware.hardwaremanager, threading, ui, poi.operation, time, poi.dialogs.progress, ui.images as uiimages, goosemonitor, goosemonitor.images as images
logger = logging.getLogger('goosemonitor.ui')

class ConfigurationPage(hardware.userinterface.configurator.ConfigurationPage):
    __module__ = __name__

    def __init__(self):
        hardware.userinterface.configurator.ConfigurationPage.__init__(self)
        self.changedDriverSegment = False

    def getDriverSegmentChanged(self):
        return self.changedDriverSegment

    def createConfigPanel(self, parent):
        panel = poi.utils.scrolledpanel.ScrolledPanel(parent)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        infoBox = wx.StaticBox(panel, -1, ' Hardware Information ', style=0)
        nameLabel = wx.StaticText(panel, -1, 'Name:')
        nameField = wx.TextCtrl(panel, -1, '')
        nameField.Enable(False)
        self.nameField = nameField
        statusLabel = wx.StaticText(panel, -1, 'Status:')
        self.statusLabel = wx.StaticText(panel, -1, '')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        sizer = wx.FlexGridSizer(0, 2, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(nameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(nameField, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(statusLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.statusLabel, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        boxSizer.Add(sizer, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
        urlLabel = wx.StaticText(panel, -1, 'Data URL:')
        self.urlText = wx.TextCtrl(panel, -1)
        panel.Bind(wx.EVT_TEXT, self.OnContentChanged, self.urlText)
        testButton = wx.Button(panel, -1, 'Test')
        panel.Bind(wx.EVT_BUTTON, self.OnTest, testButton)
        infoBox = wx.StaticBox(panel, -1, ' Settings ', style=0)
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        sizer = wx.FlexGridSizer(0, 3, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(urlLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.urlText, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(testButton, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        boxSizer.Add(sizer, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
        self.startButton = wx.Button(panel, -1, 'Start')
        panel.Bind(wx.EVT_BUTTON, self.OnStart, self.startButton)
        self.stopButton = wx.Button(panel, -1, 'Stop')
        panel.Bind(wx.EVT_BUTTON, self.OnStop, self.stopButton)
        self.restartButton = wx.Button(panel, -1, 'Restart')
        panel.Bind(wx.EVT_BUTTON, self.OnRestart, self.restartButton)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.startButton, 0, wx.RIGHT, 5)
        sizer.Add(self.stopButton, 0, wx.RIGHT, 5)
        sizer.Add(self.restartButton, 0, wx.RIGHT, 5)
        mainsizer.Add(sizer, 0, wx.GROW | wx.ALL, 5)
        panel.SetSizer(mainsizer)
        panel.SetAutoLayout(True)
        panel.SetupScrolling()
        return panel

    def updateStatus(self):
        if self.control is None:
            return
        inst = self.getDescription().getInstance()
        if inst is not None:
            status = inst.getStatus()
            self.stopButton.Enable(status == hardware.hardwaremanager.STATUS_RUNNING)
            self.startButton.Enable(status == hardware.hardwaremanager.STATUS_STOPPED)
            self.restartButton.Enable(status == hardware.hardwaremanager.STATUS_RUNNING)
        return

    def OnHardwareStatusChanged(self, hardware):
        self.updateStatus()

    def OnStop(self, event):
        self.shutdownHardware()

    def OnStart(self, event):
        self.initializeHardware()

    def OnRestart(self, event):
        self.shutdownHardware()
        self.initializeHardware()

    def shutdownHardware(self):
        instance = self.getDescription().getInstance()
        try:
            instance.shutdown()
        except Exception as msg:
            logger.exception(msg)
            return False

        return True

    def initializeHardware(self):
        instance = self.getDescription().getInstance()
        try:
            instance.initialize()
        except Exception as msg:
            logger.exception(msg)
            return False

        return True

    def OnContentChanged(self, event):
        event.Skip()
        self.setDirty(True)

    def getURL(self):
        return self.urlText.GetValue().strip()

    def getData(self, config):
        config.set('main', 'startupinit', 'true')
        config.set('main', 'requestinterval', '5')
        config.set('main', 'url', self.getURL())

    def setData(self, config):
        inst = self.getDescription().getInstance()
        try:
            self.urlText.SetValue(config.get('main', 'url'))
        except Exception as msg:
            logger.exception(msg)

        self.updateStatus()

    def testSuccess(self):
        self.showQuickMessage('Life is good!', 'Test Success', wx.OK | wx.ICON_INFORMATION)

    def showQuickMessage(self, title, msg, style):
        f = ui.invisibleFrame
        dlg = wx.MessageDialog(f, msg, title, style)
        dlg.ShowModal()
        dlg.Destroy()

    def testFailure(self, errorcode):
        msg = ''
        if errorcode == goosemonitor.ERROR_PARSING:
            msg = 'Error parsing the data'
        if errorcode == goosemonitor.ERROR_RETRIEVING:
            msg = 'Failed to retrieve data from goose'
        self.showQuickMessage('Failure!', msg, wx.OK | wx.ICON_ERROR)

    def applied(self):
        if not self.isDirty():
            return
        instance = self.getDescription().getInstance()
        wasOn = instance.getStatus() == hardware.hardwaremanager.STATUS_RUNNING
        if wasOn:
            if not self.shutdownHardware():
                self.showQuickMessage('Error!', 'Error trying to initialize', wx.OK | wx.ICON_ERROR)
                return
        if wasOn:
            self.initializeHardware()

    def OnTest(self, event):
        inst = self.getDescription().getInstance()
        if inst is not None:
            status = inst.getStatus()
            try:
                if status == hardware.hardwaremanager.STATUS_STOPPED:
                    if not self.initializeHardware():
                        self.showQuickMessage('Failure', 'Could not start the hardware', wx.OK | wx.ICON_ERROR)
                result = inst.getAndParseData(self.getURL())
                if result is not goosemonitor.ERROR_OK:
                    self.testFailure(result)
                else:
                    self.testSuccess()
            except Exception as msg:
                self.showQuickMessage('Failure', str(msg), wx.OK | wx.ICON_ERROR)

        return

    def createControl(self, parent):
        self.control = self.createConfigPanel(parent)
        return self.control

    def dispose(self):
        hardware.userinterface.configurator.ConfigurationPage.dispose(self)
        self.control.Destroy()
        self.control = None
        return


class LightWidget(wx.Window):
    __module__ = __name__

    def __init__(self, parent, onImage=None, offImage=None):
        wx.Window.__init__(self, parent, -1, size=(100, 50), style=wx.CLIP_CHILDREN)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.buffer = None
        self.currentValue = 0
        self.minVal = 0
        self.maxVal = 0
        self.isKnown = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.label = ''
        self.statusBitmap = None
        self.padding = 2
        self.defaultFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.fontWidth = -1
        self.fontHeight = -1
        self.imageWidth = images.getImage(images.ONOFF_DEVICE_STATUS_UNKNOWN).GetWidth()
        self.imageHeight = images.getImage(images.ONOFF_DEVICE_STATUS_UNKNOWN).GetHeight()
        self.lastError = goosemonitor.ERROR_OK
        self.lastStatus = hardware.hardwaremanager.STATUS_STOPPED
        self.GoDoIt()
        return

    def setCurrentValue(self, value):
        self.currentValue = value

    def setMinMax(self, minVal, maxVal):
        self.minVal = minVal
        self.maxVal = maxVal

    def invalidate(self):
        self.updateDrawing()

    def setKnown(self, known):
        self.isKnown = known

    def OnSize(self, event):
        event.Skip()
        self.GoDoIt()

    def GoDoIt(self):
        self.updateFontSizes()
        self.createBuffer()
        self.updateDrawing()

    def updateFontSizes(self):
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        dc.SetFont(self.defaultFont)
        (self.fontWidth, self.fontHeight) = dc.GetTextExtent('H')
        dc.EndDrawing()
        labelWidth = self.fontWidth * len(self.getLabel()) + self.imageWidth + self.padding
        size = self.GetClientSizeTuple()
        origsize = size
        size = [size[0], size[1]]
        if size[0] < labelWidth:
            size[0] = labelWidth
        if size[1] < max(self.fontHeight, self.imageHeight):
            size[1] = max(self.fontHeight, self.imageHeight)
        if size[0] == origsize[0] and size[1] == origsize[1]:
            return
        self.SetSize(size)
        self.SetSizeHints(size[0], size[1])
        print('updating ...')
        if self.GetParent().GetSizer() is not None:
            self.GetParent().GetSizer().Layout()
        return

    def setStatus(self, error, status):
        self.lastStatus = status
        self.lastError = error

    def setLabel(self, label):
        self.label = label

    def getLabel(self):
        return self.label

    def createBuffer(self):
        size = self.GetSize()
        if (size[0], size[1]) <= (0, 0):
            return
        self.buffer = wx.EmptyBitmap(size[0], size[1])

    def updateDrawing(self):
        if self.buffer is None:
            return
        dc = wx.BufferedDC(None, self.buffer)
        self.DoDrawing(dc)
        return

    def DoDrawing(self, dc):
        size = self.GetSize()
        x = self.padding
        y = 0
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.defaultFont)
        dc.SetTextForeground(goosemonitor.MONITOR_FOREGROUND_COLOR)
        drawVal = self.lastStatus and self.lastError == goosemonitor.ERROR_OK
        if self.isKnown and drawVal:
            x += self.imageWidth + self.padding
            y = (size[1] - self.fontHeight) / 2
            dc.DrawText(self.getLabel(), x, y)
            y = (size[1] - self.imageHeight) / 2
            if self.currentValue >= self.maxVal:
                dc.DrawBitmap(images.getImage(images.ONOFF_DEVICE_STATUS_ON), 0, y, True)
            else:
                dc.DrawBitmap(images.getImage(images.ONOFF_DEVICE_STATUS_OFF), 0, y, True)
        else:
            dc.DrawBitmap(images.getImage(images.ONOFF_DEVICE_STATUS_UNKNOWN), 0, y, True)
        dc.EndDrawing()

    def OnPaint(self, event):
        if self.buffer is not None:
            dc = wx.BufferedPaintDC(self, self.buffer)
        else:
            size = self.GetSize()
            if (size[0], size[1]) > (0, 0):
                self.createBuffer()
            event.Skip()
        return


MONITOR_TEMP_CURRENT_INDICATOR_COLOR = wx.Colour(0, 220, 0)
MONITOR_TEMP_FILL_COLOR = wx.Colour(220, 0, 0)

class TemperatureWidget(wx.Window):
    __module__ = __name__

    def __init__(self, parent, valueColor=MONITOR_TEMP_FILL_COLOR):
        wx.Window.__init__(self, parent, -1, size=(30, 100))
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.buffer = None
        self.currentValue = 0
        self.isKnown = False
        self.minTemp = 0
        self.maxTemp = 0
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.label = ''
        self.valueColor = valueColor
        self.xxx = 0
        self.padding = 2
        self.defaultFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.fontWidth = -1
        self.fontHeight = -1
        self.lastError = goosemonitor.ERROR_OK
        self.lastStatus = hardware.hardwaremanager.STATUS_STOPPED
        self.GoDoIt()
        return

    def setStatus(self, error, status):
        self.lastStatus = status
        self.lastError = error

    def setLabel(self, label):
        self.label = label

    def setCurrentValue(self, value):
        self.currentValue = value

    def setMinMax(self, minTemp, maxTemp):
        self.minTemp = minTemp
        self.maxTemp = maxTemp

    def invalidate(self):
        self.updateDrawing()

    def setKnown(self, known):
        self.isKnown = known

    def OnSize(self, event):
        event.Skip()
        self.GoDoIt()

    def GoDoIt(self):
        self.updateFontSizes()
        self.createBuffer()
        self.createMask()
        self.updateDrawing()

    def updateFontSizes(self):
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        dc.SetFont(self.defaultFont)
        (self.fontWidth, self.fontHeight) = dc.GetTextExtent('H')
        dc.EndDrawing()
        del dc
        labelWidth = self.fontWidth * len(self.getLabel())
        self.largestTempWidth = self.fontWidth * len('100.0')
        newwidth = self.padding + self.largestTempWidth + self.padding + 2 + self.padding + self.largestTempWidth + self.padding
        if labelWidth > newwidth:
            newwidth = labelWidth + self.padding * 2
        size = self.GetClientSizeTuple()
        if size[0] == newwidth:
            return
        self.SetSize((newwidth, size[1]))
        self.SetSizeHints(newwidth, size[1])
        if self.GetParent().GetSizer() is not None:
            self.GetParent().GetSizer().Layout()
        return

    def getThermoSize(self):
        """
        Return the prefered size of the thermometer.
        The width is a 3rd of the total size
        The height is the total height - the height of the font
        """
        theHeight = self.GetClientSizeTuple()[1] - self.fontHeight * 2 + self.padding
        return (self.largestTempWidth + (self.padding + 1) * 2, theHeight)

    def drawPill(self, dc, pen, brush):
        (width, height) = self.getThermoSize()
        dc.SetPen(pen)
        dc.SetBrush(brush)
        corner = width / 2
        dc.DrawRectangle(0, corner - 1, width, height - (corner - 1) * 2)
        dc.DrawEllipticArc(0, 0, width - 1, (corner - 1) * 2, 0, 180)
        dc.DrawEllipticArc(0, height - corner * 2, width - 1, (corner - 1) * 2, 180, 360)

    def createMask(self):
        (width, height) = self.GetClientSizeTuple()
        (width, height) = self.getThermoSize()
        self.bwMaskBitmap = wx.EmptyBitmap(width, height)
        bdc = wx.MemoryDC()
        bdc.SelectObject(self.bwMaskBitmap)
        bdc.BeginDrawing()
        bdc.SetBackground(wx.Brush(wx.BLACK))
        bdc.Clear()
        self.drawPill(bdc, wx.WHITE_PEN, wx.WHITE_BRUSH)
        bdc.EndDrawing()
        self.wbMaskBitmap = wx.EmptyBitmap(width, height)
        bdc = wx.MemoryDC()
        bdc.SelectObject(self.wbMaskBitmap)
        bdc.BeginDrawing()
        bdc.SetBackground(wx.Brush(wx.WHITE))
        bdc.Clear()
        self.drawPill(bdc, wx.BLACK_PEN, wx.BLACK_BRUSH)
        bdc.EndDrawing()

    def updateDrawing(self):
        if self.buffer is None:
            return
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DoDrawing(dc)
        return

    def createBuffer(self):
        size = self.GetSize()
        if (size[0], size[1]) <= (0, 0):
            return
        self.buffer = wx.EmptyBitmap(size[0], size[1])

    def DoDrawing(self, dc):
        global MONITOR_TEMP_CURRENT_INDICATOR_COLOR
        dc.BeginDrawing()
        self.xxx += 0.5
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        size = self.GetSize()
        (width, height) = (size[0], size[1])
        (width, height) = self.getThermoSize()
        x = self.padding
        y = self.fontHeight / 2
        dc.SetFont(self.defaultFont)
        dc.SetTextForeground(goosemonitor.MONITOR_FOREGROUND_COLOR)
        drawTemp = self.lastStatus and self.lastError == goosemonitor.ERROR_OK
        if self.isKnown and drawTemp:
            rng = self.maxTemp - self.minTemp
            scale = height / rng
            transformedValue = (self.currentValue - self.minTemp) * scale
            dc.SetPen(wx.Pen(self.valueColor))
            dc.SetBrush(wx.Brush(self.valueColor))
            dc.DrawRectangle(x, y + height - transformedValue, width, transformedValue)
            dc.SetPen(wx.Pen(goosemonitor.MONITOR_FOREGROUND_COLOR))
            dc.SetFont(self.defaultFont)
            dc.SetTextForeground(goosemonitor.MONITOR_FOREGROUND_COLOR)
            strVal = str(self.currentValue)
            extents = dc.GetFullTextExtent(strVal)
            dc.DrawText(strVal, x + (width - extents[0]) / 2, y + (height - transformedValue))
        memDC = wx.MemoryDC()
        tempBmp = wx.EmptyBitmap(width, height)
        memDC.SelectObject(tempBmp)
        memDC.BeginDrawing()
        memDC.Blit(0, 0, width, height, dc, x, y)
        twoDC = wx.MemoryDC()
        twoDC.SelectObject(self.bwMaskBitmap)
        memDC.Blit(0, 0, width, height, twoDC, 0, 0, wx.AND)
        memDC.EndDrawing()
        twoDC.SelectObject(self.wbMaskBitmap)
        dc.Clear()
        dc.Blit(x, y, width, height, twoDC, 0, 0, wx.AND)
        dc.Blit(x, y, width, height, memDC, 0, 0, wx.XOR)
        corner = width / 2
        dc.SetPen(wx.Pen(goosemonitor.MONITOR_FOREGROUND_COLOR))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawEllipticArc(x, y, width - 1, (corner - 1) * 2, 0, 180)
        dc.DrawEllipticArc(x, y + height - corner * 2, width - 1, (corner - 1) * 2, 180, 360)
        dc.DrawLine(x, y + corner, x, y + height - corner)
        dc.DrawLine(x + width - 1, y + corner, x + width - 1, y + height - corner)
        x = width + self.padding * 2
        if self.isKnown and drawTemp:
            y1 = y + (height - transformedValue)
            self.drawTriangle(dc, wx.TRANSPARENT_PEN, wx.Brush(MONITOR_TEMP_CURRENT_INDICATOR_COLOR), x, y1)
            dc.DrawText(str(self.currentValue), x + 5, y1 - 5)
            (totalWidth, totalHeight) = self.GetClientSizeTuple()
            dc.DrawText(self.getLabel(), totalWidth - len(self.getLabel()) * self.fontWidth, totalHeight - self.fontHeight)
        dc.DrawText(str(self.maxTemp), x, 0)
        dc.DrawText(str(self.minTemp), x, height)
        (width, height) = self.GetClientSizeTuple()
        if False:
            dc.DrawText('H', x, 0)
            dc.DrawLine(0, self.fontHeight / 2, 500, self.fontHeight / 2)
            dc.DrawLine(0, height - self.fontHeight / 2, 500, height - self.fontHeight / 2)
        dc.EndDrawing()

    def getLabel(self):
        return self.label

    def drawTriangle(self, dc, pen, brush, x, y):
        width = 5
        height = 10
        points = ((0, height / 2), (width, height), (width, 0))
        dc.SetPen(pen)
        dc.SetBrush(brush)
        dc.DrawPolygon(points, x, y - height / 2)

    def OnPaint(self, event):
        if self.buffer is not None:
            dc = wx.BufferedPaintDC(self, self.buffer)
        else:
            size = self.GetSize()
            if (size[0], size[1]) > (0, 0):
                self.createBuffer()
            event.Skip()
        return


class DeviceHandler(object):
    __module__ = __name__

    def __init__(self, deviceData):
        self.deviceData = copy.copy(deviceData)
        self.ctrl = None
        return

    def createControl(self, parent):
        self.ctrl = wx.Panel(parent, -1, size=(30, -1))
        self.ctrl.SetBackgroundColour(wx.RED)
        return self.ctrl

    def update(self, deviceData, error, status):
        pass


class WeatherDuckHandler(DeviceHandler):
    __module__ = __name__

    def __init__(self, data):
        DeviceHandler.__init__(self, data)
        self.items = {}

    def update(self, deviceData, error, status):
        for key in deviceData['fields'].keys():
            field = deviceData['fields'][key]
            if not key in self.items:
                continue
            item = self.items[key]
            item.setKnown(True)
            item.setStatus(error, status)
            item.setLabel(field['name'])
            if key in 'TempC':
                item.setCurrentValue(float(field['value']))
                item.setMinMax(float(field['min']), float(field['max']))
            elif key in ('IO1', 'IO2', 'IO3'):
                item.setCurrentValue(int(float(field['value'])))
                item.setMinMax(int(field['min']), int(field['max']))
            item.invalidate()

    def createControl(self, parent):
        global MONITOR_TEMP_FILL_COLOR
        self.ctrl = wx.Panel(parent, -1)
        self.ctrl.SetBackgroundColour(parent.GetBackgroundColour())
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        fields = self.deviceData['fields']
        for field in fields.keys():
            field = str(field)
            if field == 'TempC':
                item = TemperatureWidget(self.ctrl, MONITOR_TEMP_FILL_COLOR)
                self.items[field] = item
                self.sizer.Add(item, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
            elif field in ('IO1', 'IO2', 'IO3'):
                if not hasattr(self, 'ioSizer'):
                    self.ioSizer = wx.BoxSizer(wx.VERTICAL)
                    self.sizer.Add(self.ioSizer, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
                item = LightWidget(self.ctrl)
                self.items[field] = item
                self.ioSizer.Add(item, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)

        self.ctrl.SetSizer(self.sizer)
        self.ctrl.SetAutoLayout(1)
        self.sizer.Fit(self.ctrl)
        return self.ctrl


class AirFlowSensorHandler(DeviceHandler):
    __module__ = __name__

    def __init__(self, data):
        DeviceHandler.__init__(self, data)
        self.item = None
        self.ctrl = None
        return

    def update(self, deviceData, error, status):
        fields = deviceData['fields']
        if not 'AirFlow' in fields:
            return
        field = fields['AirFlow']
        item = self.item
        item.setKnown(True)
        item.setStatus(error, status)
        item.setLabel(field['name'])
        item.setCurrentValue(float(field['value']))
        item.setMinMax(float(field['min']), float(field['max']))
        item.invalidate()

    def createControl(self, parent):
        self.ctrl = wx.Panel(parent, -1, size=(-1, 600))
        self.ctrl.SetBackgroundColour(parent.GetBackgroundColour())
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        fields = self.deviceData['fields']
        if not 'AirFlow' in fields:
            return None
        item = TemperatureWidget(self.ctrl, wx.Color(115, 155, 240))
        self.item = item
        self.sizer.Add(item, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
        self.ctrl.SetSizer(self.sizer)
        self.ctrl.SetAutoLayout(1)
        self.sizer.Fit(self.ctrl)
        return self.ctrl
        return


class TempSensorHandler(DeviceHandler):
    __module__ = __name__

    def __init__(self, data):
        DeviceHandler.__init__(self, data)
        self.item = None
        return

    def update(self, deviceData, error, status):
        fields = deviceData['fields']
        if not 'TempC' in fields:
            return
        field = fields['TempC']
        item = self.item
        item.setKnown(True)
        item.setStatus(error, status)
        item.setLabel(field['name'])
        item.setCurrentValue(float(field['value']))
        item.setMinMax(float(field['min']), float(field['max']))
        item.invalidate()

    def createControl(self, parent):
        self.ctrl = wx.Panel(parent, -1, size=(-1, 600), style=wx.CLIP_CHILDREN)
        self.ctrl.SetBackgroundColour(parent.GetBackgroundColour())
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        fields = self.deviceData['fields']
        if not 'TempC' in fields:
            return None
        item = TemperatureWidget(self.ctrl)
        self.item = item
        self.sizer.Add(item, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
        self.ctrl.SetSizer(self.sizer)
        self.ctrl.SetAutoLayout(1)
        self.sizer.Fit(self.ctrl)
        return self.ctrl
        return


class MonitorWindowItem(object):
    __module__ = __name__

    def __init__(self, hardwareInstance):
        self.hardwareInstance = hardwareInstance
        self.hardwareInstance.addGooseListener(self)
        self.hardwareInstance.addHardwareStatusListener(self)
        wnd = goosemonitor.getDefault().getMonitorWindow()
        wnd.addItem(self)
        self.discovered = False
        self.fields = {}
        self.handlers = {}
        self.parentWindow = None
        self.lastError = goosemonitor.ERROR_OK
        return

    def gooseUpdate(self, goose, error, extra):
        self.lastError = error
        self.updateFields()

    def updateFields(self):
        self.fields = self.hardwareInstance.getFields()
        wx.CallAfter(self.internalUpdateFields)

    def internalUpdateFields(self):
        print('refresh')
        if not self.discovered:
            self.discoverDevices()
        status = self.hardwareInstance.getStatus()
        self.setStatusIndicator(self.lastError)
        devices = self.hardwareInstance.getDevices()
        keys = devices.keys()
        for did in keys:
            device = devices[did]
            if not did in self.handlers:
                continue
            self.handlers[did].update(device, self.lastError, status)

        self.ctrl.Refresh()

    def discoverDevices(self):
        devices = self.hardwareInstance.getDevices()
        if len(devices) == 0:
            return
        deviceHandlers = {'WeatherDuck': WeatherDuckHandler, 'AirFlowSensor': AirFlowSensorHandler, 'TempSensor': TempSensorHandler}
        keys = devices.keys()
        try:
            for did in keys:
                device = devices[did]
                if not device['type'] in deviceHandlers:
                    continue
                handler = deviceHandlers[device['type']](device)
                ctrl = handler.createControl(self.ctrl)
                if ctrl is None:
                    continue
                self.itemsSizer.Add(ctrl, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
                self.handlers[did] = handler

        except Exception as msg:
            logger.exception(msg)

        self.itemsSizer.Fit(self.ctrl)
        mysize = self.ctrl.GetSize()
        size = self.itemsSizer.GetMinSize()
        if size[1] < mysize[1]:
            size[1] = mysize[1]
        self.ctrl.SetSizeHints(size[0], size[1])
        self.itemsSizer.Layout()
        if self.parentWindow is not None:
            self.parentWindow.modifiedInternals()
        self.discovered = True
        return

    def discoverFields(self):
        """ sets everything up in the ui """
        self.tempItem = TemperatureWidget(self.ctrl)
        self.IO1Item = TemperatureWidget(self.ctrl)
        self.IO2Item = TemperatureWidget(self.ctrl)
        self.itemsSizer.Add(self.tempItem, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
        self.itemsSizer.Add(self.IO1Item, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
        self.itemsSizer.Add(self.IO2Item, 0, wx.GROW | wx.ALL | wx.FIXED_MINSIZE, 5)
        self.itemsSizer.Layout()
        self.discovered = True

    def setStatusIndicator(self, error):
        status = self.hardwareInstance.getStatus()
        icon = goosemonitor.images.STATUS_DEVICE_STATUS_NONE
        if status in (hardware.hardwaremanager.STATUS_STOPPED, hardware.hardwaremanager.STATUS_STOPPING):
            icon = goosemonitor.images.STATUS_DEVICE_STATUS_NONE
        elif error is not goosemonitor.ERROR_OK:
            icon = goosemonitor.images.STATUS_DEVICE_STATUS_ERROR
        else:
            icon = goosemonitor.images.STATUS_DEVICE_STATUS_NORMAL
        self.statusIcon.SetBitmap(goosemonitor.images.getImage(icon))

    def hardwareStatusChanged(self, inst):
        self.updateFields()

    def setDeviceName(self, name):
        self.labelDeviceName.SetLabel(name)

    def createControl(self, parent, window):
        self.parentWindow = window
        p = wx.Panel(parent, -1, size=(-1, 400))
        p.SetBackgroundColour(parent.GetBackgroundColour())
        self.statusPanel = wx.Panel(p, -1, size=(20, 20))
        self.statusPanel.SetBackgroundColour(goosemonitor.MONITOR_BACKGROUND_COLOR)
        self.labelDeviceName = wx.StaticText(self.statusPanel, -1, '')
        self.labelDeviceName.SetForegroundColour(goosemonitor.MONITOR_FOREGROUND_COLOR)
        self.labelDeviceName.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.statusIcon = wx.StaticBitmap(self.statusPanel, -1, goosemonitor.images.getImage(goosemonitor.images.STATUS_DEVICE_STATUS_NONE))
        statusSizer = wx.BoxSizer(wx.HORIZONTAL)
        statusSizer.Add(self.labelDeviceName, 1, wx.GROW | wx.ALL, 2)
        statusSizer.Add(self.statusIcon, 0, wx.ALL, 2)
        self.statusPanel.SetSizer(statusSizer)
        self.statusPanel.SetAutoLayout(1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.statusPanel, 0, wx.GROW | wx.ALL, 5)
        self.itemsSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.itemsSizer, 1, wx.GROW | wx.ALL, 5)
        p.SetSizer(sizer)
        p.SetAutoLayout(True)
        p.Bind(wx.EVT_PAINT, self.OnPaint, p)
        self.ctrl = p
        return p

    def OnPaint(self, event):
        event.Skip()
        (width, height) = self.ctrl.GetClientSizeTuple()
        dc = wx.PaintDC(self.ctrl)
        dc.BeginDrawing()
        dc.SetPen(wx.Pen(goosemonitor.MONITOR_FOREGROUND_COLOR))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, width - 1, height - 1)
        dc.EndDrawing()

    def getControl(self):
        return self.ctrl

    def dispose(self):
        if self.hardwareInstance is not None:
            self.hardwareInstance.removeHardwareStatusListener(self)
        self.ctrl.Destroy()
        return
