# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/actions/acceleratortable.py
# Compiled at: 2005-06-10 18:51:25
import wx
frames = {}

class AcceleratorTable(object):
    """Attach an accelerator table to a shell"""
    __module__ = __name__

    def __init__(self, shell):
        global frames
        self.shell = shell
        self.entries = {}
        self.keys = []
        frames[self.shell] = self

    def addEntry(self, entry):
        keycomp = (
         entry[0], entry[1])
        self.entries[keycomp] = entry[2]
        self.updateShell()

    def removeEntry(self, entry):
        keycomp = (
         entry[0], entry[1])
        if keycomp in self.entries:
            del self.entries[keycomp]

    def updateShell(self):
        entries = []
        for (key, val) in list(self.entries.items()):
            entries.append((key[0], key[1], val))

        self.shell.SetAcceleratorTable(wx.AcceleratorTable(entries))
