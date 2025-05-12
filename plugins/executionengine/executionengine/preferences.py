# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/preferences.py
# Compiled at: 2004-12-07 11:25:23
import wx, plugins.ui.ui.dialog.preferences, plugins.executionengine.executionengine.messages as messages, logging, plugins.executionengine.executionengine
logger = logging.getLogger('executionengine.preferences')

class PreferencesPage(plugins.ui.ui.dialog.preferences.PreferencesPage):
    __module__ = __name__

    def __init__(self, ps):
        plugins.ui.ui.dialog.preferences.PreferencesPage.__init__(self, ps)
        self.values = {}

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        label = wx.StaticText(self.control, -1, messages.get('preferences.data.resolution'))
        self.dataResolution = wx.TextCtrl(self.control, -1, '')
        sizer = wx.FlexGridSizer(0, 3, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.dataResolution, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.EXPAND)
        sizer.Add(wx.StaticText(self.control, -1, messages.get('preferences.data.resolution.units')), 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_TEXT, self.OnModification, self.dataResolution)
        return self.control

    def OnModification(self, event):
        event.Skip()
        self.setDirty()
        data = self.dataResolution.GetValue()
        valid = False
        data = data.strip()
        if len(data) == 0:
            valid = False
        try:
            valid = float(data) >= executionengine.DEFAULT_RESOLUTION
        except Exception as msg:
            valid = False

        self.setCanPressOK(valid)
        self.update()

    def getTitle(self):
        return 'Run'

    def getPath(self):
        return 'run'

    def handleRemove(self):
        self.values['dataResolution'] = self.dataResolution.GetValue()
        ui.dialog.preferences.PreferencesPage.handleRemove(self)

    def getOrder(self):
        return 1

    def setData(self, prefs):
        global logger
        if prefs is None:
            logger.debug('Preferences set as None!')
            return
        res = executionengine.DEFAULT_RESOLUTION
        try:
            res = float(prefs.get('execution', 'dataResolution'))
        except Exception as msg:
            logger.exception(msg)
            logger.debug('Error getting data acquisition resolution, defaulting to %f second' % executionengine.DEFAULT_RESOLUTION)

        self.dataResolution.SetValue(str(res))
        return

    def getData(self, prefs):
        if not prefs.has_section('execution'):
            prefs.add_section('execution')
        val = self.values['dataResolution']
        res = str(executionengine.DEFAULT_RESOLUTION)
        try:
            res = str(float(val))
        except Exception as msg:
            logger.debug("Bad value '%s' for data resolution, defaulting to %s second" % (val, executionengine.DEFAULT_RESOLUTION))

        logger.debug('Setting data resolution value to %s' % res)
        prefs.set('execution', 'dataResolution', res)
