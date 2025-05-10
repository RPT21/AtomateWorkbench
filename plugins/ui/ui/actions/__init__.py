# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/actions/__init__.py
# Compiled at: 2004-10-08 00:40:06
import plugins.ui.ui, plugins.poi.poi.actions, plugins.ui.ui.messages as messages
import plugins.ui.ui.images as images, plugins.ui.ui.dialog.preferences, plugins.ui.ui.splash, wx

class ExitAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('filemenu.exit'), messages.get('filemenu.exit.tip'), messages.get('filemenu.exit.tip'))

    def run(self):
        ui.getDefault().exit()


class HideSectorsAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Show Run Perspective', '', '')

    def run(self):
        ui.getDefault().getMainFrame().showPerspective('run')


class ShowSectorsAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Show Edit Perspective', '', '')

    def run(self):
        ui.getDefault().getMainFrame().showPerspective('edit')


class PreferencesAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('toolsmenu.preferences'), messages.get('toolsmenu.preferences.tip'), messages.get('toolsmenu.preferences.tip'))

    def run(self):
        dlg = ui.dialog.preferences.PreferencesDialog()
        dlg.createControl(ui.getDefault().getMainFrame().getControl())
        if dlg.showModal() == wx.ID_OK:
            pass
        dlg.dispose()


class AboutAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('helpmenu.about'), messages.get('helpmenu.about.tip'), messages.get('helpmenu.about.tip'))

    def run(self):
        splash = ui.splash.SplashPage(ui.getDefault().getMainFrame().getControl(), False)
        splash.show()


class HelpContentsAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('helpmenu.help'), messages.get('helpmenu.help.tip'), messages.get('helpmenu.help.tip'))

    def run(self):
        print('Help Contents')

class ToggleGraphEditorView(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('viewmenu.grapheditor'), messages.get('viewmenu.grapheditor.tip'), messages.get('viewmenu.grapheditor.tip'))

    def run(self):
        print('viewmenu.grapheditor')


class ToggleExtendedEditorView(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('viewmenu.extendededitor'), messages.get('viewmenu.extendededitor.tip'), messages.get('viewmenu.extendededitor.tip'))

    def run(self):
        print('viewmenu.extended')
