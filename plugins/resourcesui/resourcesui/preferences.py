# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/preferences.py
# Compiled at: 2004-11-19 02:47:50
import os, sys, wx, ui, wx.html, wx.lib.wxpTag, ui.dialog.preferences, resourcesui.messages as messages, resourcesui, logging
logger = logging.getLogger('resources.userinterface')

class PreferencesPage(ui.dialog.preferences.PreferencesPage):
    __module__ = __name__

    def __init__(self, ps):
        ui.dialog.preferences.PreferencesPage.__init__(self, ps)

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 3, 3, 3)
        fsizer.AddGrowableCol(1)
        self.localWorkspaceField = wx.TextCtrl(self.control, -1)
        localWorkspaceButton = wx.Button(self.control, -1, messages.get('preferences.browse.label'))
        fsizer.Add(wx.StaticText(self.control, -1, messages.get('preferences.localworkspace.label')), 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.localWorkspaceField, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(localWorkspaceButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        mainsizer.Add(fsizer, 0, wx.GROW | wx.ALL, 5)
        localWorkspaceButton.Bind(wx.EVT_BUTTON, self.OnBrowseLocalWorkspace)
        self.control.SetSizer(mainsizer)
        self.control.SetAutoLayout(True)
        return self.control

    def OnBrowseLocalWorkspace(self, event):
        prefs = self.getPreferencesStore().getPreferences()
        dlg = wx.DirDialog(ui.getDefault().getMainFrame().getControl(), messages.get('preferences.localworkspace.browse.title'), prefs.get('workspace', 'localworkspace.path'), style=wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.localWorkspaceField.SetValue(path)

    def getTitle(self):
        return messages.get('preferences.title')

    def getPath(self):
        return 'run'

    def handleRemove(self):
        self.saveChanges()

    def setData(self, prefs):
        self.suppress = True
        self.localWorkspaceField.SetValue(prefs.get('workspace', 'localworkspace.path'))
        self.suppress = False

    def sanityCheck(self, path):
        path = path.strip()
        if len(path) == 0:
            raise Exception('Path cannot be empty, defaulting to system')
        if not os.path.exists(path):
            raise Exception("Path does not exist '%s'" % path)
        if not os.path.isdir(path):
            raise Exception('Path is not a real path. Maybe a file? %s' % path)
        if not os.access(path, os.R_OK | os.W_OK):
            raise Exception('Cannot read or write to path %s' % path)

    def handleClosing(self, id):
        pass

    def saveChanges(self):
        store = self.getPreferencesStore()
        prefs = store.getPreferences()
        path = self.localWorkspaceField.GetValue()
        try:
            self.sanityCheck(path)
            prefs.set('workspace', 'localworkspace.path', path)
        except Exception, msg:
            logger.exception(msg)
            return

        store.commit()

    def getOrder(self):
        return 1
