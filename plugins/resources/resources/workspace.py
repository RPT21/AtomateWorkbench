# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resources/src/resources/workspace.py
# Compiled at: 2004-12-17 20:47:12
import os, sys, shutil, lib.kernel, logging
import plugins.resources.resources.project as project_lib
import plugins.resources.resources.version as version_lib
import plugins.resources.resources.utils as utils_lib
import plugins.resources.resources.runlog as runlog_lib
import plugins.resources.resources as resources
logger = logging.getLogger('resources')
WORKSPACE_DIRNAME = 'workspace'
suppress = False
workspaceChangeListeners = []
TYPE_MODIFY = 1
TYPE_REMOVE = 2
TYPE_CREATE = 3
WCE2STR = {TYPE_MODIFY: 'modify', TYPE_REMOVE: 'remove', TYPE_CREATE: 'create'}

class WorkspaceChangeEvent(object):
    __module__ = __name__

    def __init__(self, etype, root):
        self.etype = etype
        self.root = root

    def getType(self):
        return self.etype

    def getTypeStr(self):
        global WCE2STR
        return WCE2STR[self.etype]

    def getRoot(self):
        return self.root

    def __repr__(self):
        return "[WorkspaceChangeEvent: type='%s'/root='%s'" % (self.getTypeStr(), self.getRoot())


def addWorkspaceChangeListener(listener):
    global workspaceChangeListeners
    if not listener in workspaceChangeListeners:
        workspaceChangeListeners.append(listener)


def removeWorkspaceChangeListener(listener):
    if listener in workspaceChangeListeners:
        workspaceChangeListeners.remove(listener)


def fireWorkspaceChangeEvent(event):
    global suppress
    if suppress:
        return list(map((lambda listener: listener.workspaceChanged(event)), workspaceChangeListeners))


def suppressWorkspaceChangeEvents(doit):
    global suppress
    suppress = doit


def init():
    setLocalPrefix(None)
    if not os.path.exists(getSharedLocation()):
        try:
            lib.kernel.setNiceMask()
            os.makedirs(getSharedLocation())
        except Exception as msg:
            logger.exception(msg)
            logger.error("* ERROR: Cannot initialize shared workspace at '%s':" % getSharedLocation())
            sys.exit(13)

    if not os.path.exists(getLocalLocation()):
        try:
            lib.kernel.setNiceMask()
            os.makedirs(getLocalLocation())
        except Exception as msg:
            logger.exception(msg)
            logger.error("* ERROR: Cannot initialize local workspace at '%s':" % getLocalLocation())
            sys.exit(13)

    logger.debug("Local workspace initialized at: '%s'" % getLocalLocation())
    logger.debug("Shared workspace initialized at: '%s'" % getSharedLocation())


def getProjects(shared=False, onlyShared=False):
    projects = []
    if not onlyShared:
        projects = getLocalProjects()
    if shared:
        projects.extend(getSharedProjects())
    return projects


def getLocalProjects():
    location = getLocalLocation()
    return getProjectsAtPath(location)


def getProjectsAtPath(location):
    shared = location.find(getSharedLocation()) >= 0
    projects = []
    for filename in os.listdir(location):
        if filename in ['.', '..']:
            continue
        fullpath = os.path.join(location, filename)
        if not os.path.isdir(fullpath):
            continue
        if not project_lib.isProject(fullpath):
            continue
        project = getProject(filename, shared)
        try:
            project.load()
        except Exception as msg:
            logger.exception(msg)
            logger.warning("Could not load project '%s': '%s'" % (filename, msg))

        projects.append(project)

    return projects


def getSharedProjects():
    location = getSharedLocation()
    return getProjectsAtPath(location)


def getVersionLogs(version):
    location = version.getLocation()
    results = []
    return results


def cmpOnNumber(x, y):
    return y.getNumber() - x.getNumber()


def getRecipeVersions(project):
    location = project.getLocation()
    results = []
    for filename in os.listdir(location):
        fullpath = os.path.join(location, filename)
        if not os.path.isdir(fullpath):
            continue
        if not version_lib.isRecipeVersion(fullpath):
            continue
        version = version_lib.RecipeVersion(filename)
        version.internal_setParent(project)
        version.setLocation(fullpath)
        version.load()
        results.append(version)

    results.sort(cmpOnNumber)
    return results


def cmpOnModDates(x, y):
    return y.getModificationDate() - x.getModificationDate()


def getRunLogs(version):
    location = version.getLocation()
    results = []
    for filename in os.listdir(location):
        fullpath = os.path.join(location, filename)
        if not os.path.isfile(fullpath):
            continue
        if not runlog_lib.isRunLog(fullpath):
            continue
        runlog = runlog_lib.RunLog(os.path.splitext(filename)[0])
        runlog.internal_setParent(version)
        runlog.setLocation(fullpath)
        runlog.load()
        results.append(runlog)

    results.sort(cmpOnModDates)
    return results


def getRecipeVersion(project, name):
    location = project.getLocation()
    newversion = version_lib.RecipeVersion(name)
    newversion.setLocation(os.path.join(location, name))
    newversion.internal_setParent(project)
    return newversion


def getRunLog(recipeVersion, runVersion):
    newRunLog = runlog_lib.RunLog(str(runVersion))
    newRunLog.setLocation(recipeVersion.getLocation())
    return newRunLog


def getLocalLocation():
    global WORKSPACE_DIRNAME
    return os.path.join(localprefix, WORKSPACE_DIRNAME)


def setLocalPrefix(prefix):
    global localprefix
    if prefix is None:
        localprefix = utils_lib.getUsersDirectory()
    else:
        localprefix = prefix


def getSharedLocation():
    return os.path.join(lib.kernel.getSite(), WORKSPACE_DIRNAME)


def remove(resource):
    global TYPE_REMOVE
    resource.remove()
    shutil.rmtree(resource.getLocation())
    fireWorkspaceChangeEvent(WorkspaceChangeEvent(TYPE_REMOVE, resource))


def getProject(name, shared=False):
    """Creates only a handle.  Creation must be done with the create function from the project"""
    if shared:
        location = getSharedLocation()
    else:
        location = getLocalLocation()
    location = os.path.join(location, name)
    project = project_lib.Project(name)
    project.setLocation(location)
    project.internal_setParent(resources.getDefault().getWorkspace())  # getWorkspace() pertany a la classe ResourcesPlugin, i workspace és el mòdul workspace.py, internal_setParent pertany a la classe Resource de __init__
    return project


def moveProject(project, destPath):
    """Move the project from its place to the destPath location"""
    srcLoc = project.getLocation()
    name = os.path.basename(srcLoc)
    if not os.path.exists(destPath):
        raise Exception("The path '%s' does not exist." % destPath)
    fpDest = os.path.join(destPath, name)
    if os.path.exists(fpDest):
        raise Exception("The path '%s' already exists." % fpDest)
    try:
        shutil.move(srcLoc, fpDest)
        fireWorkspaceChangeEvent(WorkspaceChangeEvent(TYPE_MODIFY, project))
    except Exception as msg:
        logger.exception(msg)
        raise Exception("Unable to move resource: '%s'" % msg)
