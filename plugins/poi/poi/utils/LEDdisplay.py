# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/utils/LEDdisplay.py
# Compiled at: 2005-06-10 18:51:25
import wx
DISPLAY_RATIO = 34.0 / 91.0
LED_ONOFF_RATIO = 0.2
LINE1 = 1
LINE2 = 2
LINE3 = 4
LINE4 = 8
LINE5 = 16
LINE6 = 32
LINE7 = 64
LINE8 = 128
LINE9 = 256
ALLON = LINE1 | LINE2 | LINE3 | LINE4 | LINE5 | LINE6 | LINE7 | LINE8
CHARACTERS = {'0': (LINE1 | LINE2 | LINE3 | LINE5 | LINE6 | LINE7), '1': (LINE3 | LINE6), '2': (LINE1 | LINE3 | LINE4 | LINE5 | LINE7), '3': (LINE1 | LINE3 | LINE4 | LINE6 | LINE7), '4': (LINE2 | LINE3 | LINE4 | LINE6), '5': (LINE1 | LINE2 | LINE4 | LINE6 | LINE7), '6': (LINE1 | LINE2 | LINE4 | LINE5 | LINE6 | LINE7), '7': (LINE1 | LINE3 | LINE6), '8': (LINE1 | LINE2 | LINE3 | LINE4 | LINE5 | LINE6 | LINE7), '9': (LINE1 | LINE2 | LINE3 | LINE4 | LINE6 | LINE7), '.': LINE8, '-': LINE4, 'E': (LINE1 | LINE2 | LINE4 | LINE5 | LINE7), 'O': (LINE1 | LINE2 | LINE3 | LINE5 | LINE6 | LINE7), 'F': (LINE1 | LINE2 | LINE4 | LINE5), 'L': (LINE5 | LINE7 | LINE2)}

class LEDDisplay(wx.Window):
    __module__ = __name__

    def __init__(self, parent, id, position=wx.DefaultPosition, size=wx.DefaultSize, style=0, windowName=wx.PanelNameStr):
        wx.Window.__init__(self, parent, id, position, size)
        self.SetBackgroundColour(wx.BLACK)
        self.LEDPen = wx.Pen(wx.Colour(255, 255, 255))
        self.LEDOffPen = wx.Pen(wx.Colour(51, 51, 51))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.defineLEDComponents(size)
        self.value = ''
        self.Refresh()

    def defineLEDComponents(self, size):
        self.w = float(size[0])
        self.h = float(size[1])
        if self.h > DISPLAY_RATIO * self.w:
            self.h = DISPLAY_RATIO * self.w
        elif self.h < DISPLAY_RATIO * self.w:
            self.w = self.h / DISPLAY_RATIO
        self.cellSpacing = wx.Point(self.w / 4, 0.0)
        line1 = (
         wx.Point(0.122 * self.w, 0.088 * self.h), wx.Point(0.196 * self.w, 0.088 * self.h))
        line2 = (wx.Point(0.096 * self.w, 0.146 * self.h), wx.Point(0.072 * self.w, 0.443 * self.h))
        line3 = (wx.Point(0.214 * self.w, 0.146 * self.h), wx.Point(0.19 * self.w, 0.443 * self.h))
        line4 = (wx.Point(0.089 * self.w, 0.5 * self.h), wx.Point(0.164 * self.w, 0.5 * self.h))
        line5 = (wx.Point(0.063 * self.w, 0.557 * self.h), wx.Point(0.039 * self.w, 0.854 * self.h))
        line6 = (wx.Point(0.181 * self.w, 0.557 * self.h), wx.Point(0.157 * self.w, 0.854 * self.h))
        line7 = (wx.Point(0.056 * self.w, 0.912 * self.h), wx.Point(0.131 * self.w, 0.912 * self.h))
        line8 = (wx.Point(0.218 * self.w, 0.912 * self.h), wx.Point(0.218 * self.w, 0.912 * self.h))
        self.LEDSegments = {LINE1: line1, LINE2: line2, LINE3: line3, LINE4: line4, LINE5: line5, LINE6: line6, LINE7: line7, LINE8: line8}
        self.LEDPen.SetWidth(0.044 * self.w)
        self.LEDOffPen.SetWidth(0.037 * self.w)

    def drawDisplay(self, dc):
        offset = wx.Point(0.0, 0.0)
        for character in self.getCharacters():
            for (displaySegment, points) in self.LEDSegments.items():
                if displaySegment & character:
                    dc.SetPen(self.LEDPen)
                else:
                    dc.SetPen(self.LEDOffPen)
                dc.DrawLine(offset[0] + points[0][0], offset[1] + points[0][1], offset[0] + points[1][0], offset[1] + points[1][1])

            offset = offset + self.cellSpacing

    def getCharacters(self):
        characterList = []
        for letter in self.value:
            if letter.isalpha():
                letter = letter.upper()
            if not CHARACTERS.has_key(letter):
                continue
            if letter == '.':
                characterList[-1] = characterList[-1] | CHARACTERS[letter]
            else:
                characterList.append(CHARACTERS[letter])

        while len(characterList) < 4:
            characterList.insert(0, 0)

        return characterList

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.drawDisplay(dc)

    def OnSize(self, event):
        self.defineLEDComponents(self.GetSize())
        self.Refresh()

    def setValue(self, value):
        self.value = str(value)
        self.Refresh()

    def SetValue(self, value):
        self.value = str(value)
        self.Refresh()

    def getValue(self):
        return self.value

    def GetValue(self):
        return self.value

    def setLEDColor(self, red, green, blue):
        self.LEDPen.SetColour(wx.Colour(red, green, blue))
        bgColor = self.GetBackgroundColour()
        offPenRed = bgColor.Red() + LED_ONOFF_RATIO * (red - bgColor.Red())
        offPenGreen = bgColor.Green() + LED_ONOFF_RATIO * (green - bgColor.Green())
        offPenBlue = bgColor.Blue() + LED_ONOFF_RATIO * (blue - bgColor.Blue())

    def setBackgroundColor(self, red, green, blue):
        self.SetBackgroundColour(wx.Colour(red, green, blue))
        penColor = self.LEDPen.GetColour()
        self.LEDOffPen.SetColour(wx.Colour(red, green, blue))


if __name__ == '__main__':

    class SomeApp(wx.App):
        __module__ = __name__

        def OnInit(self):
            f = wx.Frame(None, -1, 'Test LED', size=(400, 400))
            led = LEDDisplay(f, -1)
            led.setValue('00e0')
            f.Show()
            return True
            return


    app = SomeApp(redirect=None)
    app.MainLoop()
