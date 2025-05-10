# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/utils/numericcelleditor.py
# Compiled at: 2004-10-13 02:16:12
import wx, re, grideditor.tablecolumn, logging
logger = logging.getLogger('grideditor.utils')

class NumericChangeHandler(wx.EvtHandler):
    __module__ = __name__

    def __init__(self, owner):
        wx.EvtHandler.__init__(self)
        self.owner = owner
        self.Bind(wx.EVT_TEXT, self.OnTextUpdate)

    def OnTextUpdate(self, event):
        event.Skip()
        self.owner.controlUpdate()


class NumericCellEditor(grideditor.tablecolumn.TextCellEditor):
    __module__ = __name__

    def __init__(self, column, as_type=int):
        grideditor.tablecolumn.TextCellEditor.__init__(self, column)
        self.oldValue = None
        self.as_type = as_type
        self.acceptedStartKeys = [wx.WXK_SPACE, ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]
        return

    def setType(self, ttype):
        self.as_type = ttype

    def isStartingKey(self, keycode):
        return keycode in self.acceptedStartKeys

    def createControl(self, parent):
        self.control = grideditor.tablecolumn.TextCellEditor.createControl(self, parent)
        self.control.PushEventHandler(NumericChangeHandler(self))
        return self.control

    def setValue(self, value):
        self.oldValue = value
        grideditor.tablecolumn.TextCellEditor.setValue(self, str(value))

    def controlUpdate(self):
        value = self.getValue()
        self.column.cellValueChanged(self.getStepIndex(), value)

    def convertValue(self, value):
        try:
            return self.as_type(value)
        except Exception, msg:
            logger.warn("Unable to convert value '%s':%s" % (value, msg))
            return self.as_type(0)

    def getValue(self):
        value = grideditor.tablecolumn.TextCellEditor.getValue(self)
        return self.convertValue(self.formatValue(value))

    def formatValue(self, value):
        return value

    def beginEdit(self):
        grideditor.tablecolumn.TextCellEditor.beginEdit(self)
        self.control.SetSelection(0, self.control.GetLastPosition())
