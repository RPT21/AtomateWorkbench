# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/runlogsview.py
# Compiled at: 2004-11-20 00:15:21
import poi.views, wx, kernel, resources, resourcesui.messages as messages, time, poi.views, poi.views.viewers, poi.views.contentprovider

class RunlogLabelProvider(poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        return None
        return

    def getText(self, element):
        return time.strftime('%m/%d/%Y - %I:%M:%S %p', time.localtime(element.getModificationDate()))

    def getToolTipText(self, element):
        text = element.getName()
        return text


class RunlogContentProvider(poi.views.contentprovider.ContentProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.ContentProvider.__init__(self)
        self.tinput = None
        return

    def inputChanged(self, viewer, oldInput, newInput):
        if self.tinput != newInput and newInput != None:
            self.tinput = newInput
        if viewer != None:
            viewer.refresh()
        return

    def getElements(self, inputElement):
        return resources.getDefault().getWorkspace().getRunLogs(self.tinput)


class RunLogsView(poi.views.StackedView):
    __module__ = __name__

    def __init__(self):
        poi.views.StackedView.__init__(self)

    def createBody(self, parent):
        self.viewer = poi.views.viewers.TableViewer(parent)
        control = self.viewer.getControl()
        control.InsertColumn(0, 'Date')
        self.setTitle(messages.get('views.runlogs.title'))

    def getViewer(self):
        return self.viewer

    def showRunLogs(self, version):
        self.viewer.setContentProvider(RunlogContentProvider())
        self.viewer.setLabelProvider(RunlogLabelProvider())
        self.viewer.setInput(version)
