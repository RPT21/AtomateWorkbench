# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/recipesview.py
# Compiled at: 2004-11-05 00:50:54
import wx, lib.kernel, plugins.resources.resources, plugins.poi.poi.views, plugins.poi.poi.views.viewers, plugins.poi.poi.views.contentprovider
import plugins.resourcesui.resourcesui.messages as messages, plugins.resourcesui.resourcesui.images as images

class RecipeLabelProvider(plugins.poi.poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        if element.isShared():
            return images.getImage(images.SHARED_ICON)
        else:
            return images.getImage(images.PROJECT_ICON)

    def getText(self, element):
        return element.getName()

    def getToolTipText(self, element):
        comment = element.getDescription().getComment()
        tt = '%s' % element.getName()
        if comment is not None:
            if len(comment) > 0:
                tt += '\n%s' % comment
        return tt


class RecipeContentProvider(plugins.poi.poi.views.contentprovider.ContentProvider):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.views.contentprovider.ContentProvider.__init__(self)
        self.tinput = None
        return

    def inputChanged(self, viewer, oldInput, newInput):
        if self.tinput != newInput and newInput != None:
            self.tinput = newInput
        if viewer != None:
            viewer.refresh()
        return

    def getElements(self, inputElement):
        return self.tinput.getProjects(True)


class RecipesView(plugins.poi.poi.views.StackedView):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.views.StackedView.__init__(self)
        self.viewer = None
        return

    def createBody(self, parent):
        self.viewer = plugins.poi.poi.views.viewers.TableViewer(parent)
        control = self.viewer.getControl()
        control.InsertColumn(0, 'Name')
        self.viewer.setContentProvider(RecipeContentProvider())
        self.viewer.setLabelProvider(RecipeLabelProvider())
        self.setTitle(messages.get('views.recipes.title'))

    def getViewer(self):
        return self.viewer
