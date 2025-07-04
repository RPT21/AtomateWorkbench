# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/versionsview.py
# Compiled at: 2004-11-12 00:42:06
import plugins.poi.poi.views, plugins.poi.poi.views.viewers, plugins.poi.poi.views.contentprovider
import plugins.resourcesui.resourcesui.messages as messages
import plugins.resourcesui.resourcesui.images as images
import plugins.poi.poi as poi
import plugins.resources.resources as resources

class VersionLabelProvider(poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        return images.getImage(images.VERSION_ICON)

    def getText(self, element):
        return '%d' % element.getNumber()

    def getToolTipText(self, element):
        return '%s' % element.getName()


class VersionContentProvider(poi.views.contentprovider.ContentProvider):
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
        return resources.getDefault().getWorkspace().getRecipeVersions(self.tinput)


class VersionsView(poi.views.StackedView):
    __module__ = __name__

    def __init__(self):
        poi.views.StackedView.__init__(self)

    def clear(self):
        """Clear all versions"""
        pass

    def showVersions(self, project):
        workspace = resources.getDefault().getWorkspace()
        self.viewer.setContentProvider(VersionContentProvider())
        self.viewer.setLabelProvider(VersionLabelProvider())
        self.viewer.setInput(project)

    def createBody(self, parent):
        self.viewer = poi.views.viewers.TableViewer(parent)
        control = self.viewer.getControl()
        control.InsertColumn(0, 'Number')
        self.setTitle(messages.get('views.versions.title'))

    def getViewer(self):
        return self.viewer
