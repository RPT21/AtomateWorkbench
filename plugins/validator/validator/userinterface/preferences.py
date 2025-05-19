# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/validator/src/validator/userinterface/preferences.py
# Compiled at: 2004-09-24 02:23:05
import re, wx, logging, plugins.poi.poi.utils.staticwraptext as ui_staticwraptext
import plugins.ui.ui.dialog.preferences as dialog_preferences
import plugins.validator.validator.messages as messages
import plugins.validator.validator.constants as constants
import plugins.ui.ui as ui

logger = logging.getLogger('validator')


class PreferencesPage(dialog_preferences.PreferencesPage):
    __module__ = __name__

    def __init__(self, ps):
        dialog_preferences.PreferencesPage.__init__(self, ps)
        self.suppress = False

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.values = {}
        label = wx.StaticText(self.control, -1, messages.get(constants.MESSAGE_VALIDATION_DELAY_LABEL))
        self.validatorDelay = wx.TextCtrl(self.control, -1)
        self.validatorDelay.SetMaxLength(len('000000'))
        helplabel = ui_staticwraptext.StaticWrapText(self.control, -1, messages.get(constants.MESSAGE_VALIDATION_DELAY_HELP))
        fsizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 10)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.validatorDelay, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        fsizer.Add(hsizer, 0, wx.ALIGN_CENTRE_VERTICAL)
        defaultsButton = wx.Button(self.control, -1, messages.get(constants.MESSAGE_RESTORE_DEFAULTS_LABEL))
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(fsizer, 0, wx.EXPAND)
        mainsizer.Add(helplabel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        mainsizer.Add(defaultsButton, 0, wx.ALIGN_RIGHT | wx.TOP, 10)
        self.control.SetSizer(mainsizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_BUTTON, self.OnRestoreDefaults, defaultsButton)
        self.control.Bind(wx.EVT_TEXT, self.OnAutoSaveIntervalText, self.validatorDelay)
        return self.control

    def validateFields(self):
        text = self.validatorDelay.GetValue().strip()
        if len(text) == 0:
            self.setError(messages.get(constants.MESSAGE_ERROR_EMPTY_FIELD))
            self.setCanPressOK(False)
            self.update()
            return
        c = re.compile('\\d*\\D\\d*')
        m = c.match(text)
        self.setCanPressOK(m is None)
        if m:
            self.setError(messages.get(constants.MESSAGE_ERROR_NON_NUMERIC_FIELD))
        else:
            self.setError(None)
        self.update()
        return

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
        self.validatorDelay.SetValue(prefs.get('main', 'validatordelay'))
        self.suppress = False
        self.validateFields()
        return

    def handleRemove(self):
        self.values['validatordelay'] = self.validatorDelay.GetValue()
        ui.dialog.preferences.PreferencesPage.handleRemove(self)

    def getData(self, prefs):
        try:
            validatordelay = self.values['validatordelay']
            prefs.set('main', 'validatordelay', validatordelay)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to set preferences: '%s'" % msg)

    def getTitle(self):
        return messages.get(constants.MESSAGE_VALIDATOR_PREFERENCES_TITLE)

    def getPath(self):
        return 'validator'
