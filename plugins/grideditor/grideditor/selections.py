# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/selections.py
# Compiled at: 2004-07-28 01:20:37
"""
import client.ui.events

NO_SELECTION = []

class SelectionEvent(client.ui.events.EventObject):
        def __init__(self, source, selection):
                client.ui.events.EventObject.__init__(self, source)
                self.selection = selection

        def getSelection(self):
                return self.selection

class SelectionChangeListener(object):
        def selectionChanged(self, event):
                raise Exception("Not implemented")

class SelectionProvider(object):
        def __init__(self):
                self.selectionChangeListeners = []

        def addSelectionChangeListener(self, listener):
                if listener not in self.selectionChangeListeners:
                        self.selectionChangeListeners.append(listener)

        def removeSelectionChangeListener(self, listener):
                if listener in self.selectionChangeListeners:
                        del self.selectionChangeListeners[ self.selectionChangeListeners.index(listener) ]

        def fireSelectionChanged(self, event):
                for listener in self.selectionChangeListeners:
                        listener.selectionChanged(event)
                        
"""
pass
