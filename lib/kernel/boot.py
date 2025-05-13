# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../lib/kernel/boot.py
# Compiled at: 2005-07-11 23:45:06
import threading
from lib.kernel.debug import DEBUG
import os, sys, configparser, lib.kernel, logging, logging.config, lib.kernel.logger, traceback, lib.kernel.pluginmanager as pluginmanager
PLUGIN_PROPERTIES_FILENAME = 'plugin.ini'
app = None
_pluginBootList = {}
bootSequenceListeners = []

class ContextBundle(object):
    """Configuration and startup directory of plugin, passed
    in during startup and shutdown"""
    __module__ = __name__

    def __init__(self, dirname, configuration):
        self.dirname = dirname
        self.configuration = configuration


def addBootSequenceListener(listener):
    """Add a listener to the boot lifecycle"""
    global bootSequenceListeners
    if not listener in bootSequenceListeners:
        bootSequenceListeners.append(listener)


def removeBootSequenceListener(listener):
    """Remove a listener from the boot lifecycle"""
    if listener in bootSequenceListeners:
        bootSequenceListeners.remove(listener)


def fireBootSequenceComplete():
    """Notify listeners that boot sequence is over"""
    for listener in bootSequenceListeners:
        listener.bootSequenceComplete()


def getPluginPath():
    """Returns path to the plugins"""
    return os.path.join(os.getcwd(), 'plugins')


def debugPrintPluginList(pluginList):
    print(('Num plugins:', len(pluginList)))
    for plugin in pluginList:
        print(('\t', plugin))


def oldbuildBootOrder(pluginList):
    """Rebuilds the plugin boot list based on the depends key.  Cyclic deps are not detected"""
    orderedList = []
    namesList = list(pluginList.keys())
    for name in list(pluginList.keys()):
        plugin = pluginList[name]
        pluginName = plugin.configuration.get('Plugin', 'name')
        dependencies = plugin.configuration.get('Plugin', 'depends').split(',')
        if len(dependencies[0].strip()) == 0:
            if not pluginName in orderedList:
                orderedList.append(pluginName)
            continue
        for depName in dependencies:
            if not depName in namesList:
                raise Exception("Unable to find dependent plugin '%s' for plugin '%s'" % (depName, pluginName))
            if not depName in orderedList:
                orderedList.append(depName)

        if not pluginName in orderedList:
            orderedList.append(pluginName)

    return orderedList


def recursiveBuildBootOrder(pluginList, name, orderedList):
    """Build the plugin boot order"""
    plugin = pluginList[name]
    try:
        pluginName = plugin.configuration.get('Plugin', 'name')
        dependencies = plugin.configuration.get('Plugin', 'depends').split(',')
    except Exception as msg:
        print(('*WARNING: ', msg))
        return

    for dep in dependencies:
        if dep == '':
            break
        if not dep in list(pluginList.keys()):
            raise Exception("Plugin '%s' is not available" % dep)
        if dep in orderedList:
            continue
        recursiveBuildBootOrder(pluginList, dep, orderedList)

    if not pluginName in orderedList:
        orderedList.append(pluginName)


def buildBootOrder(pluginList):
    """Rebuilds the plugin boot list based on the depends key.  Cyclic deps are not detected"""
    global logger
    orderedList = []
    namesList = list(pluginList.keys())
    for name in namesList:
        recursiveBuildBootOrder(pluginList, name, orderedList)

    lib.kernel.logger.rootLog.debug('Pluing Boot Order: %s' % str(orderedList))
    if True:
        return orderedList
    for name in list(pluginList.keys()):
        plugin = pluginList[name]
        pluginName = plugin.configuration.get('Plugin', 'name')
        dependencies = plugin.configuration.get('Plugin', 'depends').split(',')
        if len(dependencies[0].strip()) == 0:
            if not pluginName in orderedList:
                orderedList.append(pluginName)
            continue
        for depName in dependencies:
            if not depName in namesList:
                raise Exception("Unable to find dependent plugin '%s' for plugin '%s'" % (depName, pluginName))
            if not depName in orderedList:
                orderedList.append(depName)

        if not pluginName in orderedList:
            orderedList.append(pluginName)

    return orderedList


def getPluginContextBundle(propertiesPath):
    """Will throw a ConfigParser.ParsingError.  Returns the config object otherwise"""
    config = configparser.RawConfigParser()
    config.read([propertiesPath])
    return ContextBundle(os.path.dirname(propertiesPath), config)


def scanPluginsDirectory():
    """Scan the plugin directory and load the main"""
    global PLUGIN_PROPERTIES_FILENAME
    global _pluginBootList
    for dirname in os.listdir(getPluginPath()):
        fullpath = os.path.join(getPluginPath(), dirname)
        if not os.path.exists(os.path.join(fullpath, PLUGIN_PROPERTIES_FILENAME)):
            lib.kernel.logger.rootLog.warn('No %s defined for %s, skipping' % (PLUGIN_PROPERTIES_FILENAME, fullpath))
            continue
        try:
            ctx = getPluginContextBundle(os.path.join(fullpath, PLUGIN_PROPERTIES_FILENAME))
            _pluginBootList[ctx.configuration.get('Plugin', 'name')] = ctx
        except configparser.ParsingError as msg:
            lib.kernel.logger.rootLog.error("Unable to parse plugin description file '%s'-'%s'" % (fullpath, msg))
            lib.kernel.logger.rootLog.exception(msg)
            continue
        except configparser.NoSectionError as msg:
            lib.kernel.logger.rootLog.error("Unable to parse plugin description file '%s'-'%s'" % (fullpath, msg))
            lib.kernel.logger.rootLog.exception(msg)
            continue

    bootOrderList = buildBootOrder(_pluginBootList)
    bootPlugins(bootOrderList, _pluginBootList)


def bootPlugins(bootOrderList, plugins):
    """Boot up all plugins"""
    import lib.kernel.splash, wx
    lib.kernel.splash.bringup()
    lib.kernel.splash.increment('Scanning plugins ...')
    cleanGlobals = globals().copy()
    for pluginName in bootOrderList:
        wx.Yield()
        lib.kernel.logger.rootLog.debug("Booting plugin '%s'" % pluginName)
        ctx = plugins[pluginName]
        sourcePath = ctx.configuration.get('Plugin', 'source')
        pluginPath = ctx.dirname
        classPath = ctx.configuration.get('Plugin', 'class')
        sys.path.insert(0, os.path.join(getPluginPath(), pluginPath, sourcePath))
        className = classPath[classPath.rfind('.') + 1:]
        classNS = classPath[0:classPath.rfind('.')]
        try:
            module = __import__(f"plugins.{classNS}.{classNS}", globals(), locals(), ['*'])
        except Exception as msg:
            lib.kernel.logger.rootLog.exception(msg)
            lib.kernel.logger.rootLog.debug('Exiting with 12')
            sys.exit(12)

        clazz = getattr(module, className)
        inst = clazz()
        try:
            inst.startup(ctx)
            pluginmanager.addPlugin(pluginName, inst)
        except Exception as msg:
            lib.kernel.logger.rootLog.exception(msg)
            lib.kernel.logger.rootLog.debug('Exiting with 13')
            lib.kernel.splash.bringdown()
            sys.exit(13)

    fireBootSequenceComplete()


def initBaseLogger():
    lib.kernel.setAtomateGroupID()
    lib.kernel.logger.init()
    lib.kernel.logger.rootLog.info('Starting up')
    lib.kernel.resetUserGroupID()


def createApp():
    global app
    import wx

    class UIApp(wx.App):
        __module__ = __name__

        def OnInit(self):
            wx.InitAllImageHandlers()
            return True

    app = UIApp()


f = None

def startapp():
    global f
    import wx
    f = wx.Frame(None)
    wx.CallAfter(continueLoad)
    app.MainLoop()
    return


def continueLoad():
    print('continuing load')
    scanPluginsDirectory()
    f.Destroy()


def prepareOS():
    if sys.platform == 'linux2':
        logger.rootLog.debug('Preparing OS for libraries ...')
        paths = os.environ.get('LD_LIBRARY_PATH', '').split(os.pathsep)
        libpath = os.path.join(os.getcwd(), 'lib', 'python23')
        if not libpath in paths:
            paths.insert(0, libpath)
            os.environ['LD_LIBRARY_PATH'] = os.pathsep.join(paths)
            logger.rootLog.debug("New library path: '%s'" % os.environ['LD_LIBRARY_PATH'])


def prepareBuildInfo():
    buildinfoname = os.path.join(os.getcwd(), '.buildinfo')
    f = open(buildinfoname, 'r')
    num = -1
    try:
        num = int(f.readlines()[0])
        f.close()
    except Exception as msg:
        print(('ERROR READING BUILD NUMBER:', msg))

    lib.kernel.BUILD_INFO = tuple([num])


def initDebugger():
    f = open('trace.log', 'w')

    def tracer(frame, event, arg):
        f.write('f: %s:%s\n\r' % (frame.f_code, threading.currentThread()))

    threading.settrace(tracer)


def prepareSite():
    """Create workspace and log dirs if not exists and set proper perms"""
    if not os.path.exists('logs'):
        try:
            os.makedirs('logs')
        except Exception as msg:
            print("* ERROR: Unable to create logging folder 'logs'. Please check directory permissions")
            sys.exit(13)


def boot():
    global DEBUG
    if DEBUG:
        pass
    prepareSite()
    initBaseLogger()
    prepareOS()
    prepareBuildInfo()
    createApp()
    startapp()
