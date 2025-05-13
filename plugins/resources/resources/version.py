# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resources/src/resources/version.py
# Compiled at: 2004-11-02 23:11:18
import lib.kernel, os, plugins.core.core.recipe, plugins.core.core.utils
from plugins.resources.resources.__init__ import *
RECIPE_METADATA_FILENAME = '.recipe'

def isRecipeVersion(fullpath):
    global RECIPE_METADATA_FILENAME
    files = os.listdir(fullpath)
    return RECIPE_METADATA_FILENAME in files


def loadRecipeVersionDirect(path):
    name = os.path.basename(path)
    version = RecipeVersion(name)
    version.setLocation(path)
    version.load()
    return version


def getVersionWithNumber(number):
    return 'version.%d' % number


def getNextVersionName(project):
    existingVersions = getDefault().getWorkspace().getRecipeVersions(project)
    number = 1
    if len(existingVersions) > 0:
        nextnum = existingVersions[0].getNumber() + 1
        if nextnum > number:
            number = nextnum
    return getVersionWithNumber(number)


class RecipeVersion(Resource):
    __module__ = __name__

    def __init__(self, name):
        Resource.__init__(self, name)
        self.parseDigits(name)
        self.buff = None
        return

    def getProject(self):
        return self.getParent()

    def getNumber(self):
        return self.nameDigits

    def parseDigits(self, name):
        self.nameDigits = 0
        if name.rfind('.') < 0:
            raise Exception("Recipe version name has no digit extension: '%s'" % name)
        digitsStr = name[name.rfind('.') + 1:]
        try:
            self.nameDigits = int(digitsStr)
        except Exception as msg:
            raise Exception("Unable to parse digits from recipe version name: '%s'" % msg)

    def create(self):
        lib.kernel.setAtomateGroupID()
        if self.exists():
            raise Exception("Recipe version '%s' already exists at '%s'" % (self.name, self.location))
        os.makedirs(self.location)
        Resource.create(self)
        self.createRecipeDataFile()
        lib.kernel.resetUserGroupID()
        getDefault().getWorkspace().fireWorkspaceChangeEvent(workspace.WorkspaceChangeEvent(workspace.TYPE_CREATE, self))

    def createRecipeDataFile(self):
        name = self.getRecipeDataFilename()
        try:
            f = open(name, 'w')
            recipe = plugins.core.core.recipe.Recipe()
            node = plugins.core.core.recipe.convertToNode(recipe)
            self.buff = node.tostring()
            f.write(self.buff)
            f.close()
        except Exception as msg:
            raise Exception("Unable to create recipe buffer version: '%s'-'%s'" % (name, msg))

    def exists(self):
        return os.path.exists(self.location) and os.path.exists(os.path.join(self.location, RECIPE_METADATA_FILENAME))

    def getRecipeDataFilename(self):
        return os.path.join(self.location, RECIPE_METADATA_FILENAME)

    def load(self):
        """Loads the buffer for the recipe"""
        Resource.load(self)
        try:
            f = open(self.getRecipeDataFilename(), 'r')
            self.buff = f.read()
            f.close()
        except Exception as msg:
            raise Exception("Unable to open recipe version: '%s'" % msg)

    def getBuffer(self):
        return self.buff

    def setBuffer(self, buff):
        self.buff = buff

    def writeBuffer(self):
        filename = self.getRecipeDataFilename()
        try:
            lib.kernel.setAtomateGroupID()
            f = open(filename, 'wU')
            f.write(self.buff)
            f.close()
            lib.kernel.resetUserGroupID()
        except Exception as msg:
            raise Exception("Unable to save recipe '%s':'%s'" % (filename, msg))
