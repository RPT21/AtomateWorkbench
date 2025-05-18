# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/preferences.py
# Compiled at: 2004-11-19 02:46:29
import re, wx, logging, plugins.ui.ui.dialog.preferences, wx.lib.colourselect as colourselect
import plugins.grideditor.grideditor.messages as messages
import plugins.grideditor.grideditor.constants as grideditor_constants

import plugins.ui.ui as ui

logger = logging.getLogger('grideditor')

class PreferencesPage(ui.dialog.preferences.PreferencesPage):
    __module__ = __name__

    def __init__(self, ps):
        ui.dialog.preferences.PreferencesPage.__init__(self, ps)
        self.suppress = False

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.values = {}
        label = wx.StaticText(self.control, -1, messages.get(grideditor_constants.MESSAGE_AUTOSAVE_INTERVAL_LABEL))
        self.autoSaveInterval = wx.TextCtrl(self.control, -1)
        self.autoSaveInterval.SetMaxLength(len('00000'))
        helplabel = wx.StaticText(self.control, -1, messages.get(grideditor_constants.MESSAGE_AUTOSAVE_INTERVAL_HELP))
        fsizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 10)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.autoSaveInterval, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        hsizer.Add(helplabel, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(hsizer, 0, wx.ALIGN_CENTRE_VERTICAL)
        self.tabAcquires = wx.CheckBox(self.control, -1, messages.get(grideditor_constants.MESSAGE_TAB_ACQUIRES_PREVIOUS_LABEL))
        fsizer.Add(wx.Panel(self.control, -1, size=wx.Size(1, 1)), 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.tabAcquires, 1, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(wx.StaticText(self.control, -1, messages.get(grideditor_constants.MESSAGE_SELECTION_COLOR)), 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        fsizer.Add(wx.Panel(self.control, -1, size=wx.Size(1, 1)), 0, wx.ALIGN_CENTRE_VERTICAL)
        self.gridCellColor = colourselect.ColourSelect(self.control, -1, size=wx.Size(60, 20))
        self.control.Bind(colourselect.EVT_COLOURSELECT, self.OnColorSelect)
        fsizer.Add(self.gridCellColor, 0, wx.ALIGN_CENTRE_VERTICAL)
        defaultsButton = wx.Button(self.control, -1, messages.get(grideditor_constants.MESSAGE_RESTORE_DEFAULTS_LABEL))
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(fsizer, 0, wx.EXPAND)
        mainsizer.Add(defaultsButton, 0, wx.ALIGN_RIGHT | wx.TOP, 10)
        self.control.SetSizer(mainsizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_BUTTON, self.OnRestoreDefaults, defaultsButton)
        self.control.Bind(wx.EVT_TEXT, self.OnAutoSaveIntervalText, self.autoSaveInterval)
        return self.control

    def validateFields(self):
        text = self.autoSaveInterval.GetValue().strip()
        if len(text) == 0:
            self.setError(messages.get(grideditor_constants.MESSAGE_ERROR_EMPTY_FIELD))
            self.setCanPressOK(False)
            self.update()
            return
        c = re.compile('\\d*\\D\\d*')
        m = c.match(text)
        self.setCanPressOK(m is None)
        if m:
            self.setError(messages.get(grideditor_constants.MESSAGE_ERROR_NON_NUMERIC_FIELD))
        else:
            self.setError(None)
        self.update()
        return

    def OnColorSelect(self, event):
        event.Skip()
        if self.suppress:
            return
        self.setDirty()

    def OnAutoSaveIntervalText(self, event):
        event.Skip()
        if self.suppress:
            return
        self.setDirty()
        self.validateFields()

    def OnRestoreDefaults(self, event):
        event.Skip()
        self.restoreDefaults()

    def restoreDefaults(self):
        self.setData(self.getPreferencesStore().getDefaultPreferences())
        self.setDirty()

    def setData(self, prefs):
        global logger
        if prefs is None:
            logger.debug('Preferences set as None!')
            return
        self.suppress = True
        self.autoSaveInterval.SetValue(prefs.get('editor', 'autosaveinterval'))
        try:
            self.gridCellColor.SetValue(self.parseColorStr(prefs.get('editor', 'colors.highlight')))
        except Exception as msg:
            logger.exception(msg)

        self.suppress = False
        self.validateFields()
        return

    def parseColorStr(self, colstr):
        try:
            return wx.Colour(*list(map((lambda s: int(s)), colstr.split(','))))
        except Exception as msg:
            logger.exception(msg)
            return wx.Colour(0, 0, 100)

    def colorToStr(self, color):
        return '%s,%s,%s' % (color.Red(), color.Green(), color.Blue())

    def handleRemove(self):
        self.values['autosaveinterval'] = self.autoSaveInterval.GetValue()
        self.values['colors.highlight'] = self.colorToStr(self.gridCellColor.GetValue())
        ui.dialog.preferences.PreferencesPage.handleRemove(self)

    def getData(self, prefs):
        try:
            autosaveinterval = self.values['autosaveinterval']
            prefs.set('editor', 'autosaveinterval', autosaveinterval)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to set preferences: '%s'" % msg)

        try:
            gridcellcolor = self.values['colors.highlight']
            prefs.set('editor', 'colors.highlight', gridcellcolor)
        except Exception as msg:
            logger.exception(msg)

    def getTitle(self):
        return messages.get(grideditor_constants.MESSAGE_EDITOR_PREFERENCES_TITLE)

    def getPath(self):
        return 'editor'
