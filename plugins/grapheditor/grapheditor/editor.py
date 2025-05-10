# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grapheditor/src/grapheditor/editor.py
# Compiled at: 2004-11-19 02:57:36
"""
Manages the graphs and its contribution on the editor.

it uses a buffered drawing method
"""
import random, wx, time, poi.views, copy
random.seed()
import grapheditor, grapheditor.images as images, grapheditor.messages as messages, logging
logger = logging.getLogger('grapheditor.editor')
DEFAULT_SB_WIDTH = 18
ZOOMCONTROL_WIDTH = 100
LABEL_COLUMN_WIDTH = 40

class TimelineEvent(object):
    __module__ = __name__

    def __init__(self, duration):
        self.id = '%d.%d' % (time.time(), random.random())
        self.duration = duration


class EditorViewer(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.itemContributors = []
        self._Buffer = None
        self.scrolledX = 0
        self.scrolledY = 0
        self.millisPerPixel = 1000 / 3.0
        self.horizontalScale = 2.0
        self.defaultZoomPosition = 10
        self.zoomRange = 400
        self.mouseListeners = []
        self.cachedIntervalEvents = []
        self.currentCachedInterval = None
        self.currentHoveredItem = None
        self.events = []
        self.cursorResizeWE = None
        self.cursorNormal = None
        self.selectedEvent = None
        self.trackingContributionItem = None
        self.colors = {'normal-event': (wx.Colour(200, 200, 200))}
        self.cachedDuration = 0
        self.minimumGapMillis = 60 * 1000
        self.deviceToContribution = {}
        self.selectedIndex = 0
        return

    def setEditor(self, editor):
        self.editor = editor
        self.editor.addInputChangedListener(self)
        self.editor.addSelectionChangedListener(self)
        self.inputChanged(None, self.editor.getInput())
        return

    def handleSelectionChanged(self, selection):
        step = None
        if len(selection) > 0:
            step = selection[0]
        if step is None:
            return
        self.ensureEventVisible(step)
        return

    def calcZoomRange(self):
        width = self.getWidth()
        r = self.getDuration() / self.millisPerPixel
        newFullFactor = r / width * 100
        self.zoomRange = int(newFullFactor)

    def dispose(self):
        self.disposeContributors()
        self.editor.removeInputChangedListener(self)
        self.editor.removeSelectionChangedListener(self)

    def inputChanged(self, oldInput, newInput):
        if oldInput == newInput:
            return
        if newInput is None:
            self.disposeContributors()
            return
        model = newInput
        model.addModifyListener(self)
        self.loadGraphItemContributions()
        self.updateVisibleEvents()
        return

    def disposeContributors(self):
        for contributor in self.itemContributors:
            contributor.dispose()

    def recipeModelChanged(self, event):
        if event.getEventType() == event.ADD_DEVICE:
            self.addGraphItemContributionForDevice(event.getDevice())
        elif event.getEventType() == event.REMOVE_DEVICE:
            contrib = self.getContributionForDevice(event.getDevice())
            if contrib is None:
                return
            del self.deviceToContribution[event.getDevice()]
            self.removeItemContributor(contrib)
        elif event.getEventType() == event.CHANGE:
            self.updateVisibleEvents()
        elif event.getEventType() == event.REMOVE:
            self.updateVisibleEvents()
        elif event.getEventType() == event.ADD:
            self.updateVisibleEvents()
        for contributor in self.itemContributors:
            contributor.recipeModelChanged(event)

        return

    def updateVisibleEvents(self):
        self.events = []
        recipe = self.editor.getInput().getRecipe()
        lastDuration = 0
        for event in recipe.getSteps():
            lastDuration = int(event.getDuration() * 1000)
            self.events.append(TimelineEvent(lastDuration))

        self.calculateDuration()
        self.calcZoomRange()
        wx.CallAfter(self.refresh)

    def getContributionForDevice(self, device):
        if not self.deviceToContribution.has_key(device):
            return None
        return self.deviceToContribution[device]
        return

    def loadGraphItemContributions(self):
        recipe = self.editor.getInput()
        for device in recipe.getDevices():
            self.addGraphItemContributionForDevice(device)

    def addGraphItemContributionForDevice(self, device):
        factory = grapheditor.getGraphContributionFactory(device.getType())
        logger.debug('Contributing to graph factory: %s- %s' % (factory, device))
        if factory is None:
            return
        contribution = factory.getInstance(device.getType())
        self.addItemContributor(contribution)
        contribution.setDevice(device)
        self.deviceToContribution[device] = contribution
        return

    def calculateDuration(self):
        total = 0
        for event in self.events:
            total += event.duration

        self.cachedDuration = total

    def addMouseListeners(self, listener):
        if not listener in self.mouseListeners:
            self.mouseListeners.append(listener)

    def removeMouseListener(self, listener):
        if listener in self.mouseListeners:
            self.mouseListeners.remove(listener)

    def fireMouseOver(self, pos):
        pass

    def getVisibleInterval(self):
        width = self.getWidth() + self.scrolledX
        return (self.pixelToMillis(self.scrolledX), self.pixelToMillis(width))

    def millisToPixels(self, millis):
        return int(millis / (self.horizontalScale * self.millisPerPixel))

    def clientToCanvasMillis(self, millis):
        lt = self.getTitleColumnWidth()
        return int(millis / (self.horizontalScale * self.millisPerPixel)) + lt - self.scrolledX

    def eventToCanvasX(self, event):
        return self.clientToCanvasMillis(self.getDurationUpTo(event))

    def pixelToMillis(self, pixel):
        return pixel * (self.horizontalScale * self.millisPerPixel)

    def getDuration(self):
        """Returns the time in milliseconds"""
        return self.cachedDuration

    def updateBuffer(self):
        global DEFAULT_SB_WIDTH
        size = self.control.GetClientSize()
        if size[0] < DEFAULT_SB_WIDTH:
            size[0] = DEFAULT_SB_WIDTH + 5
        if size[1] < DEFAULT_SB_WIDTH:
            size[1] = DEFAULT_SB_WIDTH + 5
        self._Buffer = wx.EmptyBitmap(size[0] - DEFAULT_SB_WIDTH, size[1] - DEFAULT_SB_WIDTH)
        self.updateDrawing()

    def addItemContributor(self, contributor):
        if contributor not in self.itemContributors:
            self.itemContributors.append(contributor)
            contributor.prepareItem(self, self.editor.getInput())
        self.refresh()

    def updateItem(self, item):
        self.updateDrawing()
        self.updateScrollbars()

    def refresh(self):
        self.updateDrawing()
        self.updateScrollbars()

    def removeItemContributor(self, contributor):
        if contributor in self.itemContributors:
            self.itemContributors.remove(contributor)
        self.refresh()

    def rearrangeContributor(self, fromIndex, toIndex):
        if self.fromIndex > len(self.itemContributors):
            return
        if toIndex > len(self.itemContributors):
            toIndex = len(self.itemContributors)
        (self.itemContributors[toIndex], self.itemContributors[fromIndex]) = (self.itemContributors[fromIndex], self.itemContributors[toIndex])
        self.refresh()

    def paintUpperRightSquare(self, dc):
        size = self.control.GetClientSize()
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
        dc.DrawRectangle(size[0] - DEFAULT_SB_WIDTH, 0, DEFAULT_SB_WIDTH, self.timelineHeader.getHeight())
        dc.SetBrush(wx.NullBrush)

    def paintLowerLeftSquare(self, dc):
        size = self.control.GetClientSize()
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
        dc.DrawRectangle(0, size[1] - DEFAULT_SB_WIDTH, self.getTitleColumnWidth(), DEFAULT_SB_WIDTH)
        dc.SetBrush(wx.NullBrush)

    def paintLowerRightSquare(self, dc):
        size = self.control.GetClientSize()
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
        dc.DrawRectangle(size[0] - DEFAULT_SB_WIDTH, size[1] - DEFAULT_SB_WIDTH, DEFAULT_SB_WIDTH, DEFAULT_SB_WIDTH)
        dc.SetBrush(wx.NullBrush)

    def paintDecorations(self):
        dc = wx.ClientDC(self.control)
        self.paintUpperRightSquare(dc)
        self.paintLowerLeftSquare(dc)
        self.paintLowerRightSquare(dc)

    def cacheEventsInInterval(self, interval):
        self.currentCachedInterval = interval
        self.cachedIntervalEvents = []
        for event in self.events:
            d = self.getDurationUpTo(event)
            if d < interval[0]:
                continue
            if d > interval[1]:
                break
            if interval[0] <= d <= interval[1]:
                self.cachedIntervalEvents.append(event)

    def getCachedIntervalEvents(self):
        return self.cachedIntervalEvents

    def ensureEventVisible(self, step):
        recipe = self.editor.getInput().getRecipe()
        index = recipe.getStepIndex(step)
        self.selectedIndex = index
        width = self.getWidth() - self.getTitleColumnWidth()
        duration = self.getDurationUntil(index)
        sep = width / 2 - self.getTitleColumnWidth()
        x = self.millisToPixels(duration) - sep
        if x < 0:
            x = 0
        size = self.millisToPixels(self.getDuration()) + 100
        if x + width > size:
            x = size - width
        self.scrollCanvasHorizontal(x)
        self.horizSB.SetThumbPosition(x)

    def getDurationUntil(self, index):
        goal = min(len(self.events), index)
        duration = 0
        for i in range(goal):
            duration += self.events[i].duration

        return duration

    def ensureDeviceVisible(self, device):
        pass

    def update(self, dc, interval):
        lt = self.getTitleColumnWidth()
        self.cacheEventsInInterval(interval)
        contentLeft = self.getTitleColumnWidth()
        contentTop = self.timelineHeader.getHeight()
        contentHeight = self.getHeight()
        contentWidth = self.getWidth()
        pixelInterval = (
         lt + self.millisToPixels(interval[0]) - self.scrolledX, lt + self.millisToPixels(interval[1]) - self.scrolledX)
        if False:
            dc.SetPen(wx.Pen(wx.WHITE, wx.TRANSPARENT))
            dc.DrawRectangle(pixelInterval[0], 0, pixelInterval[1], self.getHeight())
            dc.SetPen(wx.NullPen)
        self.paintDecorations()
        self.timelineHeader.update(dc, interval, pixelInterval)
        dc.SetClippingRegion(0, self.timelineHeader.getHeight(), self.getWidth() + self.getTitleColumnWidth(), self.getHeight())
        atX = self.getTitleColumnWidth()
        atY = self.timelineHeader.getHeight() + self.scrolledY
        if True:
            for contributor in self.itemContributors:
                dc.SetPen(wx.Pen(self.hilitecolor))
                dc.DrawLine(atX, atY, atX + contentWidth, atY)
                dc.SetPen(wx.NullPen)
                atY += 1
                contributor.update(dc, (atX - self.scrolledX, atY), interval, pixelInterval, self.cachedIntervalEvents, self)
                contributor.updateTitle(dc, (0, atY), interval, self.getTitleColumnWidth())
                atY += contributor.getHeight() + 1
                dc.SetPen(wx.Pen(self.shadowcolor))
                dc.DrawLine(atX, atY, atX + contentWidth, atY)
                dc.SetPen(wx.NullPen)
                atY += 1

        dc.DestroyClippingRegion()
        self.paintEvents(dc, interval)
        dc.SetPen(wx.GREY_PEN)
        dc.DrawLine(contentLeft, contentTop, contentLeft, contentHeight)
        dc.SetPen(wx.NullPen)
        if False:
            lt = self.getTitleColumnWidth()
            dc.SetPen(wx.Pen(wx.GREEN))
            (left, right) = (lt + self.millisToPixels(interval[0]) - self.scrolledX, self.scrolledX + lt + self.millisToPixels(interval[1]) - self.scrolledX)
            dc.DrawLine((left, 0), (left, self.getHeight()))
            dc.DrawLine((right, 0), (right, self.getHeight()))
            dc.SetPen(wx.NullPen)
        if False:
            size = self.control.GetClientSize()
            for i in range(0, size[0], 25):
                dc.DrawText('%d' % i, (i, 0))

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self.control, self._Buffer)

    def updateDrawing(self):
        then = time.time()
        dc = wx.BufferedDC(wx.ClientDC(self.control), self._Buffer)
        interval = (
         self.pixelToMillis(self.scrolledX), self.pixelToMillis(self.getWidth() + self.scrolledX))
        dc.BeginDrawing()
        dc.Clear()
        self.update(dc, interval)
        dc.EndDrawing()
        now = time.time()

    def OnSize(self, event):
        event.Skip()
        self.updateScrollbars()
        self.positionScrollbars()
        self.positionZoomControl()
        self.updateBuffer()
        self.updateDrawing()

    def updateScrollbars(self):
        width = self.getWidth()
        size = self.millisToPixels(self.getDuration()) + 100
        thumbsize = width
        if width > size:
            self.horizSB.Disable()
            if not self.scrolledX == 0:
                self.scrolledX = 0
                self.refresh()
        elif not self.horizSB.IsEnabled():
            self.horizSB.Enable()
        self.horizSB.SetScrollbar(self.scrolledX, thumbsize, size, thumbsize, True)
        height = self.getHeight()
        size = self.getTotalItemHeights() + 30
        thumbsize = height
        if height > size:
            self.vertSB.Disable()
            if not self.scrolledY == 0:
                self.scrolledY = 0
                self.refresh()
        elif not self.vertSB.IsEnabled():
            self.vertSB.Enable(True)
        self.vertSB.SetScrollbar(-1 * self.scrolledY, thumbsize, size, thumbsize, True)

    def getHeight(self):
        size = self.control.GetClientSize()
        return size[1] - (self.timelineHeader.getHeight() + DEFAULT_SB_WIDTH)

    def getTotalItemHeights(self):
        total = 0
        for item in self.itemContributors:
            total += item.getHeight()

        return total

    def updateColors(self):
        self.hilitecolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT)
        self.shadowcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW)

    def createControl(self, parent):
        self.updateColors()
        self.view = poi.views.StackedView()
        self.view.createControl(parent)
        self.control = wx.Window(self.view.getContent(), -1)
        self.calculateDuration()
        self.createCursors()
        self.createScrollbars()
        self.createZoomControl()
        self.createTimelineHeader()
        self.setZoomControl(self.horizontalScale)
        self.updateBuffer()
        self.control.Bind(wx.EVT_PAINT, self.OnPaint, self.control)
        self.control.Bind(wx.EVT_SIZE, self.OnSize, self.control)
        self.control.Bind(wx.EVT_MOTION, self.OnMouseMotion, self.control)
        self.control.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown, self.control)
        self.control.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp, self.control)
        self.viewcontrol = self.view.getControl()
        self.view.setTitle(messages.get('view.title'))
        self.view.setTitleImage(images.getImage(images.VIEW_ICON))
        return self.viewcontrol

    def OnMouseLeftUp(self, event):
        event.Skip()
        if self.trackingContributionItem is not None:
            self.trackingContributionItem.onMouseLeftUp()
            return
        if self.selectedEvent is None:
            return
        self.selectedEvent = None
        if self.control.HasCapture():
            self.control.ReleaseMouse()
            self.refresh()
        event.Skip()
        return

    def OnMouseLeftDown(self, event):
        event.Skip()
        if self.trackingContributionItem is not None:
            self.trackingContributionItem.onMouseLeftDown()
            return
        (pos, ignored) = self.transformMousePos(event.GetPosition())
        event = self.getEventAtX(pos[0])
        if self.posInTimeline(pos):
            if event is not None:
                d = self.getDurationUpTo(event)
                self.downAtX = self.millisToPixels(d) + self.getTitleColumnWidth()
                self.selectedEvent = event
                self.control.CaptureMouse()
        return

    def createCursors(self):
        self.cursorNormal = wx.StockCursor(wx.CURSOR_ARROW)
        try:
            image = wx.ImageFromBitmap(images.getImage(images.RESIZE_WE))
            image.SetMaskColour(255, 0, 0)
            image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, image.GetWidth() / 2)
            image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, image.GetHeight() / 2)
            self.cursorResizeWE = wx.CursorFromImage(image)
        except Exception, msg:
            logger.exception(msg)
            self.cursorResizeWE = wx.StockCursor(wx.CURSOR_SIZEWE)

    def paintEvents(self, dc, interval):
        """Draw events from interval to interval only"""
        tonow = 0
        lt = self.getTitleColumnWidth()
        height = self.getHeight()
        dottedPen = wx.Pen(wx.RED, style=wx.DOT)
        currentPen = wx.Pen(wx.RED, 2, style=wx.SOLID)
        idx = 0
        for event in self.events:
            if self.selectedIndex == idx:
                dc.SetPen(currentPen)
            else:
                dc.SetPen(dottedPen)
            idx += 1
            tonow += event.duration
            if tonow < interval[0]:
                continue
            if tonow > interval[1]:
                break
            x = lt + int(self.millisToPixels(tonow)) - self.scrolledX
            dc.DrawLine(x, 0, x, height)

        dc.SetPen(wx.NullPen)

    def transformMousePos(self, pos):
        """Converts a raw mouse position to a position relative to the 
            scrolledX and to the size of the title column width.
            And a converted position from pixels to millis
        """
        pos = (
         pos[0] - self.getTitleColumnWidth() + self.scrolledX, pos[1])
        convertedPos = (self.pixelToMillis(pos[0]), pos[1])
        return (
         pos, convertedPos)

    def getDurationUpTo(self, target):
        total = 0
        i = 0
        for event in self.events:
            i += 1
            total += event.duration
            if id(event) == id(target):
                break

        return total

    def handleEventMotion(self, position, transformedPosition):
        durationToEvent = self.getDurationUpTo(self.selectedEvent)
        previousDuration = 0
        lastTime = 0
        eidx = self.events.index(self.selectedEvent)
        durationToEvent = self.getDurationUpTo(self.selectedEvent)
        if eidx > 0:
            prevE = self.events[eidx - 1]
            previousDuration = self.getDurationUpTo(prevE)
        now = transformedPosition[0]
        minGap = self.millisToPixels(self.minimumGapMillis)
        if previousDuration + minGap > now:
            return
        oldDuration = self.selectedEvent.duration
        oldPos = int(self.millisToPixels(durationToEvent))
        newPos = position[0]
        lt = self.getTitleColumnWidth()
        delta = lt + position[0] - self.downAtX
        self.downAtX = lt + position[0]
        if delta == 0:
            return
        self.selectedEvent.duration = now - previousDuration
        dc = wx.BufferedDC(wx.ClientDC(self.control), self._Buffer)
        dc.BeginDrawing()
        y = self.timelineHeader.getHeight()
        if delta < 0:
            srcX = lt + (position[0] - delta) - self.scrolledX
            width = lt + self.getWidth() - srcX
            destX = position[0] + lt - self.scrolledX
            if True:
                dc.Blit((destX, y), (
                 width, self.getHeight()), dc, (
                 srcX, y))
            if False:
                dc.SetBrush(wx.Brush(wx.WHITE, wx.TRANSPARENT))
                dc.SetPen(wx.Pen(wx.BLUE))
                dc.DrawRectangle((srcX, y), (width, self.getHeight()))
                dc.SetPen(wx.NullPen)
                dc.SetBrush(wx.NullBrush)
            left = destX - lt + self.scrolledX + width
            right = left + -1 * delta
            if True:
                self.update(dc, (self.pixelToMillis(left), self.pixelToMillis(right)))
            if False:
                dc.SetPen(wx.Pen(wx.GREEN))
                dc.DrawRectangle((left + lt - self.scrolledX, y), (right - left, self.getHeight()))
                dc.SetPen(wx.NullPen)
            left = self.millisToPixels(previousDuration)
            right = destX - lt + self.scrolledX
            if True:
                self.update(dc, (self.pixelToMillis(left), self.pixelToMillis(right)))
            if False:
                dc.SetPen(wx.Pen(wx.GREEN))
                dc.DrawRectangle((left + lt - self.scrolledX, y), (
                 right - left, self.getHeight()))
                dc.SetPen(wx.NullPen)
        else:
            srcX = lt + (position[0] - delta) - self.scrolledX
            width = self.getWidth() - (srcX - lt)
            destX = position[0] + lt - self.scrolledX
            if False:
                dc.SetPen(wx.Pen(wx.GREEN))
                dc.DrawRectangle((srcX, y), (width, self.getHeight()))
                dc.SetPen(wx.NullPen)
            if True:
                dc.Blit((destX, y), (width, self.getHeight()), dc, (srcX, y))
            left = self.millisToPixels(durationToEvent)
            right = destX - lt + self.scrolledX
            if True:
                self.update(dc, (self.pixelToMillis(left), self.pixelToMillis(right)))
            if False:
                print 'UPDATE:', left, right
                dc.SetPen(wx.Pen(wx.GREEN))
                dc.DrawRectangle((left + lt - self.scrolledX, y), (
                 right - left - self.scrolledX, self.getHeight()))
                dc.SetPen(wx.NullPen)
        dc.EndDrawing()
        self.calculateDuration()
        self.updateScrollbars()

    def OnMouseMotion(self, event):
        event.Skip()
        if True:
            return
        (pos, transormedPos) = self.transformMousePos(event.GetPosition())
        if self.trackingContributionItem is not None:
            self.trackingContributionItem.onMouseMotion(pos, transormedPos)
            return
        if self.selectedEvent:
            self.handleEventMotion(pos, transormedPos)
            return
        event = self.getEventAtX(pos[0])
        if self.posInTimeline(pos):
            if event is not None:
                self.control.SetCursor(self.cursorResizeWE)
            else:
                self.control.SetCursor(self.cursorNormal)
        else:
            item = self.findItemAtPos(pos)
            (x, y) = self.canvasToItem(pos)
            if item != self.currentHoveredItem:
                if item is not None:
                    item.onMouseEnter((x, y))
                if self.currentHoveredItem is not None:
                    self.currentHoveredItem.onMouseLeave()
                self.currentHoveredItem = item
            if item is not None:
                item.onMouseMotion((x, y))
        return

    def getYOffsetOfItem(self, item):
        atY = self.scrolledY + self.timelineHeader.getHeight()
        for i in self.itemContributors:
            if i == item:
                return atY
            atY += i.getHeight()

        return 0

    def canvasToItem(self, pos):
        """Convert x,y from the canvas to the client internal"""
        x = pos[0] + self.scrolledX
        y = pos[1] - self.timelineHeader.getHeight() - self.scrolledY
        return (
         x, y)

    def findItemAtPos(self, pos):
        atY = self.timelineHeader.getHeight() - self.scrolledY
        y = self.scrolledY + pos[1]
        for item in self.itemContributors:
            if atY < 0:
                continue
            if atY > self.getHeight() - self.scrolledY:
                break
            if atY <= y <= atY + item.getHeight():
                return item
            atY += item.getHeight()

        return None
        return

    def posInTimeline(self, pos):
        return 0 < pos[1] < self.timelineHeader.getHeight()

    def getEventAtX(self, x):
        time = self.pixelToMillis(x)
        timerange = (self.pixelToMillis(x - 3), self.pixelToMillis(x + 3))
        atwhat = 0
        for event in self.events:
            atwhat += event.duration
            if timerange[0] < atwhat < timerange[1]:
                return event

        return None
        return

    def createTimelineHeader(self):
        self.timelineHeader = TimelineHeader(self)

    def createZoomControl(self):
        self.zoomControl = wx.Slider(self.control, -1, self.defaultZoomPosition, 1, 100)
        self.zoomControl.SetToolTipString('Adjust the horizontal scale of the timeline')
        self.zoomSmallLeft = wx.StaticBitmap(self.control, -1, images.getImage(images.ZOOM_SMALL))
        self.zoomSmallRight = wx.StaticBitmap(self.control, -1, images.getImage(images.ZOOM_LARGE))
        self.control.Bind(wx.EVT_SCROLL, self.OnZoomControl, self.zoomControl)

    def setZoomControl(self, scale):
        pos = scale * 100.0 / float(self.zoomRange) * 100.0
        self.zoomControl.SetValue(pos)

    def OnZoomControl(self, event):
        actualZoom = float(event.GetPosition() / 100.0) * self.zoomRange / 100.0
        self.horizontalScale = actualZoom
        self.refresh()
        self.updateScrollbars()
        event.Skip()

    def positionZoomControl(self):
        global ZOOMCONTROL_WIDTH
        size = self.control.GetClientSize()
        (left, right) = (
         self.zoomSmallLeft.GetSize(), self.zoomSmallRight.GetSize())
        ypos = size[1] - DEFAULT_SB_WIDTH
        self.zoomSmallLeft.SetPosition((self.getTitleColumnWidth(), ypos))
        self.zoomSmallRight.SetPosition((self.getTitleColumnWidth() + (ZOOMCONTROL_WIDTH - right[0]), ypos))
        self.zoomControl.SetPosition((self.getTitleColumnWidth() + left[0], ypos))
        self.zoomControl.SetSize((ZOOMCONTROL_WIDTH - (left[0] + right[0]), DEFAULT_SB_WIDTH))

    def positionScrollbars(self):
        global LABEL_COLUMN_WIDTH
        size = self.control.GetClientSize()
        size = (size[0] - self.getTitleColumnWidth(), size[1])
        self.horizSB.SetPosition((LABEL_COLUMN_WIDTH + ZOOMCONTROL_WIDTH, size[1] - DEFAULT_SB_WIDTH))
        self.horizSB.SetSize((size[0] - (ZOOMCONTROL_WIDTH + DEFAULT_SB_WIDTH), DEFAULT_SB_WIDTH))
        self.vertSB.SetPosition((self.getTitleColumnWidth() + (size[0] - DEFAULT_SB_WIDTH), self.timelineHeader.getHeight()))
        self.vertSB.SetSize((DEFAULT_SB_WIDTH, size[1] - (DEFAULT_SB_WIDTH + self.timelineHeader.getHeight())))

    def createScrollbars(self):
        self.horizSB = wx.ScrollBar(self.control, -1)
        self.vertSB = wx.ScrollBar(self.control, -1, style=wx.SB_VERTICAL)
        self.control.Bind(wx.EVT_SCROLL, self.OnHorizScroll, self.horizSB)
        self.control.Bind(wx.EVT_SCROLL, self.OnVertScroll, self.vertSB)

    def scrollCanvasHorizontal(self, pos):
        self.scrolledX = pos
        self.refresh()

    def scrollCanvasVertical(self, pos):
        self.scrolledY = -pos
        self.refresh()

    def OnHorizScroll(self, event):
        self.scrollCanvasHorizontal(event.GetPosition())
        event.Skip()

    def OnVertScroll(self, event):
        self.scrollCanvasVertical(event.GetPosition())
        event.Skip()

    def setFocus(self, focused):
        self.view.setFocus(focused)

    def getControl(self):
        return self.viewcontrol

    def getTitleColumnWidth(self):
        return LABEL_COLUMN_WIDTH

    def getWidth(self):
        return self.control.GetSize()[0] - (DEFAULT_SB_WIDTH + self.getTitleColumnWidth())


class TimelineHeader(object):
    __module__ = __name__

    def __init__(self, owner):
        self.owner = owner
        self.height = 20
        self.radius = 4
        self.outlinecolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW)
        self.hilitecolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT)
        self.facecolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        self.minimumNumberInterval = 100
        self.currentIntervalUnit = 1000
        self.currentIntervalUnitString = 's'
        self.currentPixelsInterval = self.minimumNumberInterval
        self.lastRange = -1
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.cachedTextHeight = -1
        self.cachedValues = False

    def calcCachedValues(self, dc):
        oldfont = dc.GetFont()
        dc.SetFont(self.font)
        self.cachedTextHeight = dc.GetTextExtent('H')[1]
        dc.SetFont(oldfont)
        self.cachedValues = True

    def calcCurrentIntervalUnit(self):
        currRange = self.currentIntervalUnit
        rangeSkip = 1000
        max = 80
        min = 30
        kpixels = min
        px = self.owner.millisToPixels(currRange)
        if min < px < max:
            return
        while px < min:
            currRange += rangeSkip
            px = self.owner.millisToPixels(currRange)
            self.currentIntervalUnit = currRange

        while px < max:
            currRange += rangeSkip
            px = self.owner.millisToPixels(currRange)
            self.currentIntervalUnit = currRange

        if False:
            if px < min:
                self.currentIntervalUnit = self.owner.pixelToMillis(min)
            px = self.owner.millisToPixels(currRange)
            if px > max:
                self.currentIntervalUnit = self.owner.pixelToMillis(max)

    def calcIntervalString(self):
        """Calculates what the interval string should be based on the currIntervalUnit"""
        units = {1000: 's', (1000 * 60): 'm', (1000 * 60 * 60): 'h'}
        values = [
         1000, 1000 * 60, 1000 * 60 * 60]
        values.reverse()
        str = 's'
        for value in values:
            m = self.currentIntervalUnit / value
            str = units[value]
            if m > 0:
                break

        self.currentIntervalUnitString = str

    def calcVisibleEvents(self, interval):
        """Calculates the fully visible and partially visible events inside the interval"""
        duration = 0
        visible = []
        for event in self.owner.events:
            duration += event.duration
            if duration < interval[0]:
                continue
            visible.append(event)
            if duration > interval[1]:
                break

        return visible

    def update(self, dc, interval, pixelInterval):
        if not self.cachedValues:
            self.calcCachedValues(dc)
        lt = self.owner.getTitleColumnWidth()
        width = self.owner.getWidth()
        left = pixelInterval[0]
        width = pixelInterval[1]
        height = self.getHeight()
        top = 0
        dc.SetClippingRegion(left, top, width, height)
        if False:
            dc.SetPen(wx.Pen(self.outlinecolor))
            dc.SetBrush(wx.Brush(self.facecolor))
            dc.SetClippingRegion(left, top, width, height)
            dc.DrawRoundedRectangle(left, top, width + self.radius, height + self.radius, self.radius)
            dc.DestroyClippingRegion()
            dc.SetPen(wx.NullPen)
        numberbarheight = self.getHeight() - top
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.facecolor))
        dc.DrawRectangle(left + 1, top, width - 1, numberbarheight)
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)
        dc.SetPen(wx.Pen(self.hilitecolor))
        dc.DrawLine(left, top, width, top)
        dc.DrawLine(left, top, left, numberbarheight)
        dc.SetPen(wx.Pen(self.outlinecolor))
        dc.DrawLine(left + width, top, left + width, numberbarheight)
        dc.DrawLine(left, top + numberbarheight - 1, width, top + numberbarheight - 1)
        interval = self.owner.getVisibleInterval()
        duration = self.owner.getDuration()
        if self.lastRange != self.owner.horizontalScale:
            self.lastRange = self.owner.horizontalScale
            self.calcCurrentIntervalUnit()
            self.calcIntervalString()
        dc.SetPen(wx.Pen(wx.RED))
        dc.SetFont(self.font)
        dc.SetTextBackground(self.facecolor)
        numtop = self.calcCenter(self.cachedTextHeight, height)
        visibleEvents = self.calcVisibleEvents(interval)
        if False:
            print 'drawing:', interval[0], interval[1], self.currentIntervalUnit
            for i in range(interval[0], interval[1], self.currentIntervalUnit):
                if i < interval[0]:
                    continue
                if i > interval[1]:
                    break
                x = self.owner.millisToPixels(i) - self.owner.scrolledX
                print '\twhat what>', x
                dc.DrawLine(x, top, x, top + numberbarheight)
                text = self.getTextForValue(i)
                strw = dc.GetTextExtent(text)[0]
                offset = strw / 2
                dc.DrawText(text, left + x - offset, numtop)

        dc.SetPen(wx.NullPen)
        dc.DestroyClippingRegion()

    def calcCenter(self, itemHeight, height):
        return (height - itemHeight) / 2

    def getTextForValue(self, value):
        num = value / self.currentIntervalUnit
        unit = self.currentIntervalUnitString
        return '%0.2d%s' % (num, unit)

    def drawNavigator(self, dc):
        lt = self.owner.getTitleColumnWidth()
        width = self.owner.getWidth()
        durationInPixels = self.owner.millisToPixels(self.owner.getDuration())
        interval = (self.owner.scrolledX, self.owner.getWidth())
        dc.SetPen(wx.Pen(wx.BLUE))
        dc.DrawRectangle(lt + 0, 0, width, 4)
        dc.SetPen(wx.Pen(wx.RED))
        dc.SetBrush(wx.Brush(wx.RED))
        compx = self.owner.scrolledX / float(width)
        compwidth = width / durationInPixels
        dc.DrawRectangle(lt + compx * width, 0, compwidth * width, 4)
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)

    def getHeight(self):
        return self.height
