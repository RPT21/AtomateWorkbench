# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/actions/__init__.py
# Compiled at: 2005-06-10 18:51:25
import wx, plugins.poi.poi.actions.acceleratortable, plugins.poi.poi.images as images
statusBarFrames = {}
from wx import Menu, MenuItem, MenuBar, NewId, EvtHandler, ToolBar, NullBitmap, EVT_MENU, ITEM_NORMAL, ITEM_CHECK, ITEM_RADIO, EVT_TOOL
str2flags = {'alt': (wx.ACCEL_ALT), 'shift': (wx.ACCEL_SHIFT), 'ctrl': (wx.ACCEL_CTRL)}
STR2KEYCODE = {'DELETE': (wx.WXK_DELETE), 'F1': (wx.WXK_F1), 'F2': (wx.WXK_F2), 'F3': (wx.WXK_F3), 'F4': (wx.WXK_F4), 'F5': (wx.WXK_F5), 'F6': (wx.WXK_F6), 'F7': (wx.WXK_F7), 'F8': (wx.WXK_F8), 'F9': (wx.WXK_F9), 'F10': (wx.WXK_F10), 'F11': (wx.WXK_F11), 'F12': (wx.WXK_F12)}
globalActionHandlers = {}

def setGlobalActionHandler(sid, action):
    global globalActionHandlers
    globalActionHandlers[sid] = action


def removeGlobalActionHandler(sid):
    if globalActionHandlers.has_key(sid):
        del globalActionHandlers[sid]


def clearGlobalActionHandlers():
    globalActionHandlers.clear()


def getGlobalActionHandler(sid):
    if globalActionHandlers.has_key(sid):
        return globalActionHandlers[sid]
    return None
    return


AS_PUSH_BUTTON = 1
AS_CHECK_BOX = 2
AS_RADIO_BUTTON = 8

class Action(object):
    __module__ = __name__

    def __init__(self, text='', description='', toolTipText='', style=AS_PUSH_BUTTON):
        self.style = style
        (self.text, self.acceleratorStr, self.accelerator) = self.parseTitle(text)
        self.description = description
        self.toolTipText = toolTipText
        self.enabled = True
        self.checked = False
        self.image = None
        self.disabledImage = None
        return

    def setText(self, text):
        self.text = text

    def setImage(self, image):
        self.image = image

    def setDisabledImage(self, image):
        self.disabledImage = image

    def getImage(self):
        return self.image

    def getDisabledImage(self):
        return self.disabledImage

    def parseTitle(self, text):
        """Takes out accelerator if present"""
        tokens = text.split('\\t')
        if len(tokens) == 1:
            tokens = text.split('\t')
        if len(tokens) == 1:
            return (
             text, None, None)
        return (tokens[0], tokens[1], self.parseAcceleratorSequence(tokens[1]))
        return

    def parseAcceleratorSequence(self, accelStr):
        global STR2KEYCODE
        global str2flags
        tokens = accelStr.split('+')
        flagStrs = []
        flags = 0
        i = 0
        for token in tokens:
            if i >= len(tokens) - 1:
                break
            i += 1
            flagStrs.append(token)

        for flagStr in flagStrs:
            flagStr = flagStr.lower()
            if not flagStr in str2flags.keys():
                logger.warn("unknown flag string for accelerator '%s'" % flagStr)
                continue
            flags |= str2flags[flagStr]

        if len(flagStrs) == 0:
            flags = wx.ACCEL_NORMAL
        keyStr = tokens[len(tokens) - 1].upper()
        if keyStr in STR2KEYCODE.keys():
            keyCode = STR2KEYCODE[keyStr]
        else:
            keyCode = ord(keyStr[0])
        return (flags, keyCode, self)

    def getAcceleratorSequence(self):
        return self.accelerator

    def getAccelerator(self):
        return self.acceleratorStr

    def isEnabled(self):
        return self.enabled

    def setEnabled(self, enabled):
        self.enabled = enabled

    def getStyle(self):
        return self.style

    def setChecked(self, checked):
        self.checked = checked

    def isChecked(self):
        return self.checked

    def getText(self):
        return self.text

    def getDescription(self):
        return self.description

    def getToolTipText(self):
        return self.toolTipText

    def run(self):
        raise Exception('Action not implemented for %s' % self)


class ContributionItem(object):
    __module__ = __name__

    def __init__(self, sid):
        self.sid = sid

    def fillMenu(self, parent):
        pass

    def fillToolBar(self, parent):
        pass

    def dispose(self):
        pass

    def isEnabled(self):
        return False

    def isGroupMarker(self):
        return False

    def isSeparator(self):
        return False

    def update(self):
        pass

    def getId(self):
        return self.sid

    def isDirty(self):
        return False


class ContributionManager(object):
    __module__ = __name__

    def __init__(self):
        self.items = []
        self.dirty = False
        self.globalActionHandlers = {}

    def isDirty(self):
        return self.dirty

    def markDirty(self, dirty):
        self.dirty = dirty

    def addAction(self, action):
        pass

    def addItem(self, item):
        self.items.append(item)
        self.markDirty(True)

    def appendToGroup(self, groupName, item):
        idx = self.internalFindIndexOfGroup(groupName)
        if idx == -1:
            raise Exception("No groupName titled '%s' was found" % groupName)
        self.items.insert(idx + 1, item)
        self.markDirty(True)

    def find(self, sid):
        for item in self.items:
            if item.getId() == sid:
                return item

        return None
        return

    def findByPath(self, path):
        current = self
        tokens = path.split('/')
        found = False
        for token in tokens:
            for item in current.items:
                if item.getId() == token:
                    current = item
                    found = True
                    break

            if found:
                continue
            return None

        return current
        return

    def internalFindIndexOfGroup(self, groupName):
        idx = -1
        for item in self.items:
            idx += 1
            if not item.isGroupMarker():
                continue
            if item.getId() == groupName:
                return idx

        return -1

    def insert(self, index, item):
        pass

    def insertAfter(self, sid, item):
        founditem = self.find(sid)
        idx = len(self.items)
        if founditem is None:
            print("* ERROR: No such item '%s' found.  Append to end(%s)" % item)
        else:
            idx = self.items.index(founditem) + 1
        self.items.insert(idx, item)
        return

    def insertBefore(self, sid, item):
        pass

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
            self.dirty = True

    def removeAll(self):
        pass

    def update(self):
        pass


class ActionContributionItem(ContributionItem):
    __module__ = __name__

    def __init__(self, action, sid=None):
        ContributionItem.__init__(self, sid)
        self.action = action

    def __repr__(self):
        return '[ActionContributionItem %s]' % self.action

    def isEnabled(self):
        return self.action.isEnabled()

    def fillToolBar(self, toolbar):
        if not isinstance(toolbar, ToolBar):
            raise Exception('Parent of actioncontributionitem is not a menu: %s' % toolbar)
        label = self.action.getText()
        image = self.action.getImage()
        toolTipText = self.action.getToolTipText()
        extendedText = self.action.getDescription()
        if image is None:
            image = NullBitmap
        try:
            self.widget = toolbar.AddLabelTool(NewId(), label, image, shortHelp=toolTipText, longHelp=extendedText)
            toolbar.EnableTool(self.widget.GetId(), self.action.isEnabled())
        except Exception as msg:
            print("* ERROR: Unable to create tool for toolbar('%s'):'%s'" % (self.action, msg))
            return

        class SelectionEvtHandler(EvtHandler):
            __module__ = __name__

            def __init__(innerself):
                EvtHandler.__init__(innerself)
                innerself.Bind(EVT_TOOL, self.OnItemSelected, id=self.widget.GetId())

        toolbar.PushEventHandler(SelectionEvtHandler())
        return

    def fillMenu(self, parent):
        if not isinstance(parent, Menu):
            raise Exception('Parent of actioncontributionitem is not a menu: %s' % parent)
        label = self.action.getText()
        if self.action.getAccelerator() is not None:
            label += '\t' + self.action.getAccelerator()
        style = ITEM_NORMAL
        if self.action.getStyle() & AS_CHECK_BOX != 0:
            style = ITEM_CHECK
        elif self.action.getStyle() & AS_RADIO_BUTTON != 0:
            style = ITEM_RADIO
        self.widget = MenuItem(parent, NewId(), label, kind=style)
        image = self.action.getImage()
        if not self.action.isEnabled():
            image = self.action.getDisabledImage()
        if image is not None:
            self.widget.SetBitmap(image)
        parent.AppendItem(self.widget)
        parent.Enable(self.widget.GetId(), self.action.isEnabled())
        if not poi.actions.acceleratortable.frames.has_key(parent.shell):
            poi.actions.acceleratortable.AcceleratorTable(parent.shell)
        seq = self.action.getAcceleratorSequence()
        if seq is not None:
            accelTable = poi.actions.acceleratortable.frames[parent.shell]
            accelTable.addEntry((seq[0], seq[1], self.widget.GetId()))
        if style & ITEM_CHECK != 0:
            parent.Check(self.widget.GetId(), self.action.isChecked())

        class SelectionEvtHandler(EvtHandler):
            __module__ = __name__

            def __init__(innerself):
                EvtHandler.__init__(innerself)
                innerself.Bind(EVT_MENU, self.OnItemSelected, id=self.widget.GetId())
                innerself.Bind(wx.EVT_MENU_HIGHLIGHT, self.OnMenuHighlighted, id=self.widget.GetId())

        self.shell = parent.shell
        parent.shell.PushEventHandler(SelectionEvtHandler())
        return

    def OnMenuHighlighted(self, event):
        global statusBarFrames
        event.Skip()
        if self.action is None:
            return
        if not statusBarFrames.has_key(self.shell):
            return
        statusbarmanager = statusBarFrames[self.shell]
        statusbarmanager.setText(self.action.getDescription())
        wx.CallAfter(statusbarmanager.update)
        return

    def OnItemSelected(self, event):
        event.Skip()
        if self.action.isEnabled():
            self.action.run()


class GlobalActionContributionItem(ActionContributionItem):
    __module__ = __name__

    def __init__(self, sid, text, description=None, toolTipText=None, enabledImage=None, disabledImage=None):
        ActionContributionItem.__init__(self, None, sid)

        class GlobalAction(Action):
            __module__ = __name__

            def __init__(innerself):
                Action.__init__(innerself, text, description, toolTipText)

            def run(self):
                pass

        self.globalAction = GlobalAction()
        self.globalAction.setEnabled(False)
        self.globalAction.setImage(enabledImage)
        self.globalAction.setDisabledImage(disabledImage)
        return

    def OnItemSelected(self, event):
        event.Skip()
        action = getGlobalActionHandler(self.getId())
        if action is not None:
            action.run()
        return

    def fillMenu(self, parent):
        self.action = getGlobalActionHandler(self.getId())
        if self.action == None:
            self.action = self.globalAction
        elif self.action.getAccelerator() is None:
            self.action.acceleratorStr = self.globalAction.getAccelerator()
        image = self.globalAction.getImage()
        if not self.action.isEnabled():
            image = self.globalAction.getDisabledImage()
        if image is not None:
            if self.action.isEnabled():
                self.action.setImage(image)
            else:
                self.action.setDisabledImage(image)
        ActionContributionItem.fillMenu(self, parent)
        self.action = None
        return


class AbstractGroupMarker(ContributionItem):
    __module__ = __name__

    def __init__(self, sid):
        ContributionItem.__init__(self, sid)

    def getGroupName(self):
        return self.sid

    def isGroupMarker(self):
        return True

    def isSeparator(self):
        return True


class StatusLineContributionItem(ContributionItem):
    __module__ = __name__

    def __init__(self, sid):
        ContributionItem.__init__(self, sid)

    def fillStatusBar(self, statusbar, pos):
        pass

    def getStatusWidth(self):
        return -1


class MessageStatusBarContributionItem(StatusLineContributionItem):
    __module__ = __name__

    def __init__(self, sid, defaultText=''):
        StatusLineContributionItem.__init__(self, sid)
        self.text = ''
        self.defaultText = ''

    def setText(self, text):
        if text is None:
            text = ''
        self.text = text
        return

    def fillStatusBar(self, statusbar, pos):
        statusbar.SetStatusText(self.text, pos)


class GroupMarker(AbstractGroupMarker):
    __module__ = __name__

    def __init__(self, sid):
        AbstractGroupMarker.__init__(self, sid)

    def isGroupMarker(self):
        return True

    def isVisible(self):
        return False


class Separator(AbstractGroupMarker):
    __module__ = __name__

    def __init__(self, sid=None):
        AbstractGroupMarker.__init__(self, sid)

    def isSeparator(self):
        return True

    def fillMenu(self, parent):
        if isinstance(parent, Menu):
            parent.AppendSeparator()

    def fillToolBar(self, parent):
        self.widget = wx.StaticBitmap(parent, -1, GetSeparatorBitmap())
        parent.AddControl(self.widget)


import pickle, zlib

def GetSeparatorData():
    return pickle.loads(zlib.decompress(b'x\xda\xd3\xc8)0\xe4\nV74P02T0R0T\xe7J\x0cV\xd7SHVPvs3\x00\x020_\x01\xc8\xf7\xcb\xcfK\x85r\x14\x14\xf4\xf4@\xe4(\x97$\xae\x1e\x00S\xca=4'))


def GetSeparatorBitmap():
    return images.getImage(images.TOOLBAR_SEPARATOR_IMAGE)
