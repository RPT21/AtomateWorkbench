# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/widgets.py
# Compiled at: 2004-10-20 22:52:47
import wx, logging
logger = logging.getLogger('mfc.widgets.setpoint')

class PurgetSetpointCtrl(wx.TextCtrl):
    __module__ = __name__

    def __init__(self, parent, max=1000.0):
        wx.TextCtrl.__init__(self, parent)
        self.max = max
        self.suppress = False
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnLeaveField)

    def setMax(self, max):
        self.max = max
        wx.CallAfter(self.validate)

    def validate(self):
        if not self.isValid():
            self.SetBackgroundColour(wx.RED)
        else:
            self.SetBackgroundColour(wx.WHITE)

    def OnLeaveField(self, event):
        """Normalize the value in the text field"""
        self.suppress = True
        self.SetValue(self.formatValue(self.getFloatValue()))
        self.suppress = False

    def OnText(self, event):
        if self.suppress:
            event.Skip()
            return
        logger.debug('On text')
        event.Skip()
        self.validate()

    def isValid(self):
        value = int(self.getFloatValue() * 1000.0)
        max = self.max
        max *= 1000
        max = int(max)
        if 0 <= value <= max:
            return True
        return False

    def formatValue(self, value):
        mantisaSize = 4
        fullSize = 5
        r = len(str(self.max))
        mantisaSize = fullSize - r
        if mantisaSize < 0:
            mantisaSize = 0
        frmt = '%%0.0%df' % mantisaSize
        return frmt % value

    def getFloatValue(self):
        value = self.GetValue()
        try:
            value = float(value)
        except Exception, msg:
            value = 0.0

        return value
