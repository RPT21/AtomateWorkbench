# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/undomanager.py
# Compiled at: 2004-08-12 08:30:22
import plugins.poi.poi.actions as actions, plugins.ui.ui.images as images
DEBUG = False

class UndoableAction(object):
    __module__ = __name__

    def __init__(self, description, redoDescription):
        self.description = description
        self.redodescription = redoDescription

    def undo(self):
        pass

    def redo(self):
        pass

    def getRedoDescription(self):
        return self.redodescription

    def getDescription(self):
        return self.description


undostack = []
pointer = -1
undoListeners = []
DEFAULT_UNDOLEVEL = 10

def addUndoManagerListener(listener):
    global undoListeners
    if not listener in undoListeners:
        undoListeners.append(listener)


def removeUndoManagerListener(listener):
    if listener in undoListeners:
        undoListeners.remove(listener)


def fireUndoManagerModified():
    for listener in undoListeners:
        listener.undoManagerModified()


def getUndoLevel():
    return DEFAULT_UNDOLEVEL


def addUndoableAction(action):
    global pointer
    global undostack
    undostack.insert(pointer + 1, action)
    if len(undostack) >= getUndoLevel():
        undostack = undostack[1:]
    else:
        pointer += 1
    fireUndoManagerModified()
    printStack()


def printStack():
    global DEBUG
    if not DEBUG:
        return
    print('---[UNDOSTACK]---')
    print(('Contains:%d actions' % len(undostack)))
    print(('Pointer at:%d' % pointer))
    buff = ''
    spc = ''
    idx = 0
    for action in undostack:
        buff += '#'
        if idx == pointer:
            spc += '^'
        else:
            spc += ' '
        idx += 1

    print(buff)
    print(spc)
    print('')
    idx = 0
    for action in undostack:
        sel = ''
        if idx == pointer:
            sel = '***'
        print(('\t', sel, action))
        idx += 1

    print('---[ENDUNDOSTACK]---')


def undo():
    global pointer
    if pointer < 0:
        return
    current = undostack[pointer]
    pointer -= 1
    current.undo()
    fireUndoManagerModified()
    printStack()


def redo():
    global pointer
    if pointer >= len(undostack):
        return
    current = undostack[pointer + 1]
    pointer += 1
    current.redo()
    fireUndoManagerModified()
    printStack()


def canRedo():
    if len(undostack) == 0:
        return False
    if pointer >= len(undostack) - 1:
        return False
    return True


def canUndo():
    if pointer < 0:
        return False
    return True


def getUndoableAction():
    if pointer >= 0:
        return undostack[pointer]
    return None


def getRedoableAction():
    if pointer < len(undostack):
        return undostack[pointer + 1]
    return None


def getUndoableActionTuple():
    """
    Returns a tuple with the previous item if available or None if not,
    and the current item
    """
    tup = [None, None]
    if pointer > 0:
        tup[0] = undostack[pointer - 1]
    tup[1] = undostack[pointer]
    return tup


class UndoAction(actions.Action):
    __module__ = __name__

    def __init__(self):
        actions.Action.__init__(self, 'Undo\tCtrl+Z', 'Undo action', 'Undo Action')
        addUndoManagerListener(self)
        self.setImage(images.getImage(images.ENABLED_EDIT_UNDO))
        self.setDisabledImage(images.getImage(images.DISABLED_EDIT_UNDO))

    def undoManagerModified(self):
        if not canUndo():
            self.setText('Undo')
        else:
            action = getUndoableAction()
            self.setText(action.getDescription())

    def isEnabled(self):
        return canUndo()

    def run(self):
        undo()


class RedoAction(actions.Action):
    __module__ = __name__

    def __init__(self):
        actions.Action.__init__(self, 'Redo\tCtrl+Y', 'Redo action', 'Redo Action')
        addUndoManagerListener(self)
        self.setImage(images.getImage(images.ENABLED_EDIT_REDO))
        self.setDisabledImage(images.getImage(images.DISABLED_EDIT_REDO))

    def undoManagerModified(self):
        if not canRedo():
            self.setText('Redo')
        else:
            action = getRedoableAction()
            self.setText(action.getRedoDescription())

    def isEnabled(self):
        return canRedo()

    def run(self):
        redo()


def init():
    global REDO_ACTION
    global UNDO_ACTION
    UNDO_ACTION = UndoAction()
    REDO_ACTION = RedoAction()
