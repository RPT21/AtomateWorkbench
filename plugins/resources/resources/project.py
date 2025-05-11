# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resources/src/resources/project.py
# Compiled at: 2004-12-17 20:47:14
import lib.kernel, os, configparser, __init__
import plugins.resources.resources.version as version_lib
from plugins.resources.resources.__init__ import *


class ProjectDescription(object):
    __module__ = __name__

    def __init__(self):
        self.comment = None
        return

    def getComment(self):
        return self.comment

    def create(self, location):
        cfg = configparser.RawConfigParser()
        cfg.add_section('description')
        cfg.set('description', 'comment', self.getComment())
        f = open(self.getMetadataFilename(location), 'w')
        cfg.write(f)
        f.close()

    def getMetadataFilename(self, location):
        global PROJECT_METADATA_FILENAME
        return os.path.join(location, PROJECT_METADATA_FILENAME)

    def parse(self, location):
        f = open(self.getMetadataFilename(location), 'r')
        cfg = configparser.RawConfigParser()
        cfg.read_file(f)
        f.close()
        try:
            self.comment = cfg.get('description', 'comment')
        except Exception as msg:
            print(('* WARNING:', Exception, msg))
            self.comment = ''


PROJECT_METADATA_FILENAME = '.project'

def isProject(fullpath):
    files = os.listdir(fullpath)
    return PROJECT_METADATA_FILENAME in files


class Project(Resource):
    __module__ = __name__

    def __init__(self, name):
        Resource.__init__(self, name)
        self.description = ProjectDescription()

    def promoteVersion(self, src):
        nextname = version_lib.getNextVersionName(self)
        workspace = version_lib.getDefault().getWorkspace()
        dest = workspace.getRecipeVersion(self, nextname)
        dest.create()
        return dest

    def create(self):
        if self.exists():
            raise Exception("Project '%s' already exists at '%s'" % (self.name, self.location))
        lib.kernel.setAtomateGroupID()
        os.makedirs(self.location)
        self.description.create(self.location)
        __init__.Resource.create(self)
        lib.kernel.resetUserGroupID()

    def exists(self):
        return os.path.exists(self.location) and os.path.exists(os.path.join(self.location, PROJECT_METADATA_FILENAME))

    def load(self):
        self.description = ProjectDescription()
        self.description.parse(self.location)
        __init__.Resource.load(self)

    def getDescription(self):
        return self.description
