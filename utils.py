# Utility functions (e.g., windowing toold, file handling, conversions)

from PyQt6.QtCore import QPoint, QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QPen, QColor, QFontMetrics, QWheelEvent
from numpy import who

#   Custom Windowing Slider

class WindowingSlider(QWidget):

    wcEdited = pyqtSignal(int)
    wwEdited = pyqtSignal(int)

    def __init__(self, parent=None):

        super().__init__(parent)
        self.center = 0
        self.windowCenter = 0
        self.windowWidth = 200
        self.imageLoaded = False

        self.bgBarMin = -1000
        self.bgBarMax = +1000
        self.fgBarMin = - (self.windowWidth / 2)
        self.fgBarMax = self.windowWidth / 2

        self.bgColor = '#3b3e45'
        self.bgBarColor = '#7289da'
        self.fgBarColor = '#fff'
        self.knobColor = '#7289da' 
        
        self.stringMax = 'Max'
        self.stringMin = 'Min'
        self.stringZero = 'x'

        self.widthX = 277
        self.fltMin = 0
        self.fltMax = 0 
        self.avg = 0
        self.transRatio = 0
        
        self.halfWidth = 20
        self.centerX = 147 
        self.knobX = 147.0
        self.ellipsePos = 0

        self.wcField = 0
        self.wwField = 0

        self.setMinimumSize(200, 70)

    def sizeHint(self):
        return QSize(300, 70)

    #   Background Bar

    def paintEvent(self, event):
        #print(self.intMin, self.intMax, self.transRatio)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        #   Background
        #painter.fillRect(self.rect(), QColor(self.bgColor),)

        #   Background bar
        bgPen = QPen(QColor(self.bgBarColor))
        bgPen.setWidth(2)
        painter.setPen(bgPen)
        painter.drawLine(10, self.height() // 2, self.width() - 10, self.height() // 2)

        #   Draw foreground bar
        fgPen = QPen(QColor(self.fgBarColor))
        fgPen.setWidth(4)
        painter.setPen(fgPen)
        #halfWidth = (self.windowWidth // (self.bgBarMax - self.bgBarMin)) * (self.width() - 20) // 2
        painter.drawLine(int(self.knobX) - self.halfWidth, self.height() // 2, int(self.knobX) + self.halfWidth, self.height() // 2)

        #   Draw knob
        painter.setBrush(QColor(self.knobColor))
        painter.setPen(Qt.PenStyle.NoPen)
        #self.knobX = self.centerX + (self.windowCenter / (self.bgBarMax - self.bgBarMin)) * (self.width() - 20)
        painter.drawEllipse(int(self.knobX - 5), self.height() // 2 - 5, 10, 10)
        
        #   Draw text labels
        painter.setPen(fgPen)
        painter.drawText(QPoint(int(self.knobX - 5), self.height() // 2 - 10), self.stringZero)
        painter.drawText(QPoint(self.width() - 30, self.height() // 2 + 30), self.stringMax)
        painter.drawText(QPoint(10, self.height() // 2 + 30), self.stringMin)

        painter.end()


    def mousePressEvent(self, event: QMouseEvent):

        if event.button() == Qt.MouseButton.LeftButton:

            newX = event.position().x()

            if newX in range (self.halfWidth, self.width() - self.halfWidth):
                self.update()
                self.knobX = newX
                if self.imageLoaded:
                    self.updateKnobLocation(newX = newX)   
                self.update()


    def updateKnobLocation(self, newX):
        print('----------------------',newX, self.transRatio)
        self.newWc = (newX * self.transRatio) + self.fltMin
        if self.newWc >= self.avg:
            self.newWc = (newX * self.transRatio) + self.fltMin + 100
            self.newWc = int(self.newWc)
            self.wcEdited.emit(self.newWc)
            self.stringZero = str(self.newWc)
        elif self.newWc < self.avg:
            self.newWc = (newX * self.transRatio) + self.fltMin - 40
            self.newWc = int(self.newWc)
            self.wcEdited.emit(self.newWc)
            self.stringZero = str(self.newWc)

    def updateParams(self, fltMin, fltMax, tr):
        self.fltMin = fltMin
        self.fltMax = fltMax 
        self.avg = (self.fltMax + self.fltMin) / 2
        self.transRatio = tr
        self.stringZero = 'x'


    def reverseKnobLocationUpdate(self):
        #   converts writtenwc to x location for knob -> it returns self.knobX
        self.stringZero = str(self.wcField)
        newKnobX = ((self.wcField - 100 - self.fltMin) // self.transRatio) + 25
        print('new knobx: ', newKnobX)
        self.knobX = newKnobX
        if self.knobX > 272:
            self.knobX = 262

        elif self.knobX < 0:
            self.knobX = 0
        self.update()

    def reverseWheelEvent(self):
        #   converts writtenww to halfWidth for line -> it returns self.halfWidth
        tr = int(self.transRatio)
        newHalfWidth = (self.wwField // ((tr * 2.4)) ) 
        newHalfWidth = int(newHalfWidth)
        self.halfWidth = newHalfWidth
        self.update()

    def wheelEvent(self,event: QWheelEvent):
        self.update()

        if event.angleDelta().y() > 0 and (self.knobX + self.halfWidth) <= (self.width() - 20) and (self.knobX - self.halfWidth) >= 15: 
            self.halfWidth += 3
            self.newWw = 4 * self.halfWidth * self.transRatio * 0.73
            self.newWw = max(0, self.newWw)
            self.wwEdited.emit(self.newWw)
            self.update()
        else:
            if 0 < self.halfWidth:
                self.halfWidth -= 3
                self.newWw = 4 * self.halfWidth * self.transRatio * 0.73
                self.newWw = max(0, self.newWw)
                self.wwEdited.emit(self.newWw)
                self.update()

