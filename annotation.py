#   Annotation logic (e.g., mask creation, segmentation)

#   Imports
import os
import json
import uuid
from PyQt6.QtCore import QSize, Qt, QRect, QPoint, pyqtSignal, pyqtSlot 
from PyQt6.QtGui import QAction, QIcon, QPixmap, QImage, QPainter, QPen, QColor, QFontMetrics, QPolygon
from PyQt6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QToolButton,
    QVBoxLayout, QWidget, QSizePolicy, QStatusBar, QDialogButtonBox, QPushButton, QColorDialog, QComboBox, QMessageBox)

#   Label Card

class LabelCard(QWidget):

    labelEdited = pyqtSignal(str, str)
    labelDeleted = pyqtSignal(str)
    labelColorEdited = pyqtSignal(str, QWidget)

    def __init__(self, labelName, labelColor, parent=None):
        super().__init__(parent)

        self.originalName = labelName

        #    Background Layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 5, 10)
        self.layout.setSpacing(10)

        # Circle Button
        self.circleButton = QPushButton(self)
        self.circleButton.setFixedSize(30, 30)
        self.circleColor = labelColor.name()
        self.circleButton.setStyleSheet(f'''
            background-color: {self.circleColor};
            border: 2px solid #7289da;
            border-radius: 15px;
        ''')
        self.circleButton.clicked.connect(self.onColorEdit)

        #   Label 
        self.label = QLineEdit(self.originalName, self)
        self.label.setStyleSheet('''
            background-color: #ffffff;
            border-radius: 6px;
            padding-left: 5px;
        ''')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        self.label.editingFinished.connect(self.onLabelEdit)

        #   Delete Button

        deleteButton = QPushButton('Delete', self)
        deleteButton.setStyleSheet('''
            background-color: #7289da;
            border-radius: 6px;
            padding: 5px 10px;
            color: #ffffff;
        ''')
        deleteButton.clicked.connect(self.selfDestruct)

        self.layout.addWidget(self.circleButton)
        self.layout.addWidget(self.label)
        self.layout.addWidget(deleteButton)
        self.layout.addStretch()

        self.setStyleSheet('''
            background-color: #2c2f33;
            border: 2px solid #7289da;
            border-radius: 15px;
        ''')

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(50)

    def onLabelEdit(self):
        newLabel = self.label.text()
        if newLabel != self.originalName:
            if newLabel == '':
                QMessageBox.warning(self, 'Input Error', "Label name can't be empty.", QMessageBox.StandardButton.Ok)
                newLabel = self.originalName
            self.labelEdited.emit(self.originalName, newLabel)
            self.originalName = newLabel


    def selfDestruct(self):
        
        labelName = self.label.text()
        self.labelDeleted.emit(labelName)
        layout = self.layout

        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)  
            if item:
                widget = item.widget() 
                if widget:
                    widget.deleteLater()  

        layout.deleteLater()

    def onColorEdit(self):
        self.labelColorEdited.emit(self.originalName, self)

    def changeColorButton(self, color):
        self.circleColor = color
        self.circleButton.setStyleSheet(f'''
            background-color: {self.circleColor};
            border: 2px solid #7289da;
            border-radius: 15px;
        ''')
        self.update()


#   Label editor

presetFile = 'labelPresets.json'

class LabelEditDialog(QDialog):

    labelDataSelected = pyqtSignal(str, QColor)
    labelAdded = pyqtSignal(str, QColor)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle('Add Label')

        #   Presets
        self.presetLabels = self.loadPresets()
        self.labelDropdown = QComboBox(self)
        self.updateDropdown()

        # Input fields
        self.nameInput = QLineEdit(self)
        self.nameInput.setPlaceholderText("Enter label's name...")
        
        self.colorButton = QPushButton('Select Color')
        self.colorButton.clicked.connect(self.chooseColor)
        
        self.selectedColor = QColor('red')  # Default color
        
        # Buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        #   Save preset 
        self.saveButton = QPushButton('Save as Preset')
        self.saveButton.clicked.connect(self.savePreset)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Label Name: '))
        layout.addWidget(self.nameInput)
        layout.addWidget(self.colorButton)
        layout.addWidget(self.saveButton)
        layout.addWidget(QLabel('Or choose a preset label: '))
        layout.addWidget(self.labelDropdown)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def loadPresets(self):
            if os.path.exists(presetFile):
                try:
                    with open(presetFile, 'r') as file:
                        return json.load(file)
                except json.JSONDecodeError:
                    print("Error reading preset file. File might be corrupted.")
                    return []
            else:
                return []

    def savePreset2File(self):
            try:
                with open(presetFile, 'w') as file:
                    json.dump(self.presetLabels, file)
            except IOError:
                print("Error writing to preset file.")

    def updateDropdown(self):
        self.labelDropdown.clear()
        self.labelDropdown.addItems([label['name'] for label in self.presetLabels])

    def onPresetLabelSelected(self, idx):
        #   Handles selected preset
        selectedLabel = self.presetLabels[index]
        self.nameInput.setText(selectedLabel['name'])
        self.selectedColor = QColor(selectedLabel['color'])

    def savePreset(self):
        labelName = self.nameInput.text()
        if not labelName:
            return
        newPreset = {'name': labelName, 'color': self.selectedColor.name()}
        if newPreset not in self.presetLabels:
            self.presetLabels.append(newPreset)
            self.savePreset2File()
            self.updateDropdown()
        else:
            print("This preset already exists.")


    def chooseColor(self):
        color = QColorDialog.getColor(self.selectedColor, self, 'Choose label color')
        if color.isValid():
            self.selectedColor = color
            self.colorButton.setStyleSheet(f'background-color: {color.name()}')


    def getLabelData(self):
        return self.nameInput.text(), self.selectedColor.name()

    def accept(self):
        labelName = self.nameInput.text()
        selectedColor = self.selectedColor
        if labelName:
            self.labelDataSelected.emit(labelName, selectedColor)
            self.labelAdded.emit(labelName, selectedColor)
            super().accept()
        else:
            QMessageBox.warning(self, 'Input Error', 'Please enter a label name.', QMessageBox.StandardButton.Ok)

#   Paint layer for painting

class PaintLayer:
    def __init__(self, label, color):
        self.id = str(uuid.uuid4())
        self.label = label
        self.color = color
        self.pixmap = QPixmap()

    def initialize(self, size):
        self.pixmap = QPixmap(size)
        self.pixmap.fill(Qt.GlobalColor.transparent)

#   Annotatable image display

class AnnotatableImageDisplay(QLabel):

    labelColorChanged = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.currentLabelName = ''
        self.currentLabelColor = QColor('red')
        self.startPoint = None
        self.endPoint = None
        self.drawing = False
        self.image = None
        self.annotations = []   #   Stores label, colors and bounding box coordinates for saving
        self.mode = 'Select'
        self.shape = 'rectangle'
        self.polygonPoints = []
        self.currentRectangle = None
        self.labelDialog = LabelEditDialog(self)
        self.lastX = None
        self.lastY = None
        self.newX = None
        self.newY = None
        self.paintLayers = []
        self.currentPaintLayer = None
        self.selectedRectangle = None
        self.polygonSelected = False
        self.isEmpty = True

    def resizeEvent(self, event):
        #   Makes image placeholder square
        size = min(self.width(), self.height())
        self.setFixedSize(QSize(size, size))
        super().resizeEvent(event)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == 'Annotate':
                if self.shape == 'rectangle':
                    self.startPoint = self.constrainPoint(event.pos())
                    self.endPoint = self.startPoint
                    self.drawing = True
                    self.currentRectangle = (self.startPoint, self.endPoint)

                elif self.shape == 'polygon':
                    self.addPoint2Polygon(event.pos())

                elif self.shape == 'paint':
                    self.drawing = True
                    self.tempPixmap = QPixmap(self.size())
                    self.tempPixmap.fill(Qt.GlobalColor.transparent)

            elif self.mode == 'Select':
                if self.shape == 'rectangle':
                    self.dragStartX = event.pos().x()
                    self.dragStartY = event.pos().y()
                    for annotation in self.annotations:
                        x1, y1, x2, y2 = annotation['bbox']
                        if x1 > x2:
                            x1, x2 = x2, x1
                        if y1 > y2:
                            y1, y2 = y2, y1
                        if x1 <= event.pos().x() <= x2:
                            if y1 <= event.pos().y() <= y2:
                                self.selectedRectangle = annotation['label']
                                break
                elif self.shape == 'polygon':
                    self.dragStartX = event.pos().x()
                    self.dragStartY = event.pos().y()
                    xPoints = []
                    yPoints = []
                    for point in self.polygonPoints:
                        x = point.x()
                        y = point.y()
                        xPoints.append(x)
                        yPoints.append(y)
                    if min(xPoints) <= event.pos().x() <= max(xPoints):
                        if min(yPoints) <= event.pos().y() <= max(yPoints):
                            self.polygonSelected = True

        if event.button() == Qt.MouseButton.RightButton:
            if self.shape == 'polygon':
                self.clearPolygon()
            elif self.shape == 'rectangle':
                self.clearRectangle()



    def mouseMoveEvent(self, event):
        if self.drawing:
            if self.shape == 'rectangle':
                self.endPoint = self.constrainPoint(event.pos())
                self.currentRectangle = (self.startPoint, self.endPoint)
                self.update()

            elif self.shape == 'paint':
                if self.lastX is None:
                    self.lastX, self.lastY = event.pos().x(), event.pos().y()
                    return

                self.newX, self.newY = event.pos().x(), event.pos().y()
                
                painter = QPainter(self.currentPaintLayer.pixmap)
                try:
                    pen = QPen(self.currentPaintLayer.color, 20)
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                    painter.drawLine(self.lastX, self.lastY, self.newX, self.newY)
                finally:
                    painter.end()

                self.lastX, self.lastY = self.newX, self.newY
                self.update()           

        if self.mode == 'Select':
            if self.shape == 'rectangle':
                if self.selectedRectangle is not None:
                    for annotation in self.annotations:
                        if annotation['label'] == self.selectedRectangle:
                            draggingX, draggingY = event.pos().x(), event.pos().y()
                            diffX, diffY = self.dragStartX - draggingX, self.dragStartY - draggingY
                            x1, y1, x2, y2 = annotation['bbox']
                            if x1 > x2:
                                x1, x2 = x2, x1
                            if y1 > y2:
                                y1, y2 = y2, y1
                            if 0 < x1 - diffX < self.width()  and 0 < x2 - diffX < self.width():
                                if 0 < y1 - diffY < self.height()  and 0 < y2 - diffY < self.height():
                                    annotation['bbox'] = x1 - diffX, y1 - diffY, x2 - diffX, y2 - diffY
                            self.dragStartX = draggingX
                            self.dragStartY = draggingY
                            self.update()

            elif self.shape == 'polygon':
                if self.polygonSelected:
                    newPointList = []
                    draggingX, draggingY = event.pos().x(), event.pos().y()
                    for point in self.polygonPoints:
                        x = point.x()
                        y = point.y()
                        diffX, diffY = self.dragStartX - draggingX, self.dragStartY - draggingY
                        x = x - diffX
                        y = y - diffY
                        point = QPoint(x, y)
                        newPointList.append(point)
                    self.polygonPoints.clear()
                    self.polygonPoints = newPointList
                    self.dragStartX = draggingX
                    self.dragStartY = draggingY
                    self.update()


    def mouseReleaseEvent(self, event):
        self.selectedRectangle = None
        self.polygonSelected = False
        if event.button() == Qt.MouseButton.LeftButton and self.drawing and self.mode == 'Annotate':
            # self.endPoint = self.constrainPoint(event.pos())
            if self.shape != 'paint':
                self.drawing = False

            if self.shape == 'paint':
                self.lastX = None
                self.lastY = None
                self.newX = None
                self.newY = None
                self.drawing = False

                # Merge tempPixmap with the main image or annotations
                if not hasattr(self, 'paintAnnotations'):
                    self.paintAnnotations = QPixmap(self.size())
                    self.paintAnnotations.fill(Qt.GlobalColor.transparent)
                
                if hasattr(self, 'tempPixmap') and self.tempPixmap is not None:
                    painter = QPainter(self.paintAnnotations)
                    painter.setOpacity(0.4)
                    painter.drawPixmap(0, 0, self.tempPixmap)
                    painter.end()
                
                self.tempPixmap = None
            
            # Finalize the rectangle
            if self.startPoint and self.endPoint:
                if self.shape == 'rectangle':
                    x1, y1 = self.startPoint.x(), self.startPoint.y()
                    x2, y2 = self.endPoint.x(), self.endPoint.y()

                    self.annotations.append({
                        'label': self.currentLabelName,
                        'color': self.currentLabelColor.name(),
                        'bbox': (x1, y1, x2, y2)
                    })

            # Clear temporary rectangle
            self.startPoint = None
            self.endPoint = None
            self.currentRectangle = None
            self.mode = 'Select'
            self.update()


    @pyqtSlot(str, QColor)
    def setLabelData(self, labelName, color):
        self.currentLabelName = labelName
        self.currentLabelColor = color

    def constrainPoint(self, point):
        if self.image:
            x = max(0, min(point.x(), self.image.width() - 2))
            y = max(0, min(point.y(), self.image.height() - 1))
        else:
            x = max(0, min(point.x(), self.width() - 1))
            y = max(0, min(point.y(), self.height() - 1))

        return QPoint(x, y)

    def createNewPaintLayer(self):
        newLayer = PaintLayer(self.currentLabelName, self.currentLabelColor)
        newLayer.initialize(self.size())
        self.paintLayers.append(newLayer)
        self.currentPaintLayer = newLayer

    def setRectMode(self):
        self.mode = 'Annotate'
        self.shape = 'rectangle'
        self.polygonPoints.clear()
        self.labelDialog.labelDataSelected.connect(self.setLabelData)
        self.labelDialog.exec() 
        self.update()

    def setPolygonMode(self):
        self.mode = 'Annotate'
        self.shape = 'polygon'
        self.polygonPoints.clear()
        self.labelDialog.labelDataSelected.connect(self.setLabelData)
        self.labelDialog.exec() 
        self.update()

    def setPaintMode(self):
        self.mode = 'Annotate'
        self.shape = 'paint'
        self.polygonPoints.clear()
        self.labelDialog.labelDataSelected.connect(self.setLabelData)
        self.labelDialog.exec() 
        self.createNewPaintLayer()
        self.update()

    def setSelectionMode(self):
        self.mode = 'Select'
        self.update()

    def setClearMode(self):
        self.isEmpty = True
        self.mode = 'Clear'
        self.currentRectangle = None
        self.annotations.clear()
        self.polygonPoints.clear()
        self.paintLayers.clear()
        self.clearPainting()
        self.update()

    def setShape2Rect(self):
        self.shape = 'rectangle'
        self.update()

    def setShape2Polygon(self):
        self.shape = 'polygon'
        self.update()

    def addPoint2Polygon(self, point):
        self.polygonPoints.append(point)
        self.update()

    def clearPolygon(self):
        self.isEmpty = True
        self.polygonPoints.clear()
        self.update()

    def clearRectangle(self):
        self.isEmpty = True
        self.currentRectangle = None
        self.annotations.clear()
        self.update()

    def clearPainting(self):
        self.isEmpty = True
        if hasattr(self, 'paintAnnotations'):
            self.paintAnnotations = QPixmap(self.size())
            self.paintAnnotations.fill(Qt.GlobalColor.transparent)
        
        if hasattr(self, 'tempPixmap') and self.tempPixmap is not None:
            self.tempPixmap.fill(Qt.GlobalColor.transparent)
        
        self.update()

    def renameAnnotation(self, label2Remove, newLabel):
        if self.shape == 'rectangle':
            for annotation in self.annotations:
                if annotation['label'] == label2Remove:
                    annotation['label'] = newLabel
                    if self.currentLabelName == annotation['label']:
                        self.currentLabelName = newLabel

                    break

        elif self.shape == 'polygon':
            self.currentLabelName = newLabel
            self.update()

        elif self.shape == 'paint':
            for layer in self.paintLayers:
                if layer.label == label2Remove:
                    layer.label = newLabel
                    if self.currentPaintLayer and self.currentPaintLayer.label == label2Remove:
                        self.currentPaintLayer.label = newLabel
                    break

        self.update()

    def removeAnnotation(self, label2Remove):
        
        for annotation in self.annotations:
            if annotation['label'] == label2Remove:
                self.annotations.remove(annotation)
                break
        
        self.update()

    def removePolyGs(self, label2Remove):
        if self.shape == 'polygon':
            if self.currentLabelName == label2Remove:
                self.polygonPoints.clear()
                self.update()
        
        self.update()

    def removePainting(self, label2Remove):
        self.paintLayers = [layer for layer in self.paintLayers if layer.label != label2Remove]
        self.update()


    def updatePaintAnnotationsColor(self, oldColor, newColor):
        if hasattr(self, 'paintAnnotations') and self.paintAnnotations is not None:
            image = self.paintAnnotations.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    if image.pixelColor(x, y).name() == oldColor.name():
                        image.setPixelColor(x, y, newColor)
            self.paintAnnotations = QPixmap.fromImage(image)

    def updatePaintLayerColor(self, layer, oldColor, newColor):
        image = layer.pixmap.toImage()
        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixelColor(x, y).name() == oldColor.name():
                    image.setPixelColor(x, y, newColor)
        layer.pixmap = QPixmap.fromImage(image)

    def recolorAnnotation(self, label2Recolor, card):
        if self.shape == 'rectangle':
            for annotation in self.annotations:
                    if annotation['label'] == label2Recolor:
                        originalColor = QColor(annotation['color'])
                        color = QColorDialog.getColor(originalColor, self, 'Choose label color')
                        if color.isValid():
                            annotation['color'] = color.name()
                            newColor = annotation['color'] 
                            card.changeColorButton(newColor)
                            self.update()
        elif self.shape in ['polygon', 'paint']:
            originalColor = self.currentLabelColor
            color = QColorDialog.getColor(originalColor, self, 'Choose label color')
            if color.isValid():
                self.currentLabelColor = color
                newColor = color.name()
                card.changeColorButton(newColor)

                if self.shape == 'paint':
                    for layer in self.paintLayers:
                        if layer.label == label2Recolor:
                            originalColor = layer.color
                            if color.isValid():
                                layer.color = color
                                card.changeColorButton(color.name())
                                self.updatePaintLayerColor(layer, originalColor, color)
                self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.isEmpty = False
        self.painter = QPainter(self)
        try:
            if self.shape == 'rectangle':
                #   Draw all rectangles
                for annotation in self.annotations:
                    label, color, bbox = annotation['label'], annotation['color'], annotation['bbox']
                    rect = QRect(QPoint(bbox[0], bbox[1]), QPoint(bbox[2], bbox[3]))
                    pen = QPen(QColor(color), 2, Qt.PenStyle.DashLine)
                    self.painter.setPen(pen)

                    #   Draw text labels
                    fontMetrics = QFontMetrics(self.painter.font())
                    textRect = fontMetrics.boundingRect(label)
                    textX = rect.center().x() - textRect.width() // 2
                    textY = rect.center().y() - textRect.height() // 2 
                    self.painter.drawRect(rect)
                    self.painter.setPen(pen)
                    self.painter.drawText(QPoint(textX, textY + 10 ), label)

                if self.currentRectangle:
                    #   Current active rectangle
                    start, end = self.currentRectangle
                    pen = QPen(self.currentLabelColor, 2, Qt.PenStyle.DashLine)
                    self.painter.setPen(pen)
                    rect = QRect(start, end)
                    self.painter.drawRect(rect)

                    #   Draw text labels
                    fontMetrics = QFontMetrics(self.painter.font())
                    textRect = fontMetrics.boundingRect(self.currentLabelName)
                    textX = rect.center().x() - textRect.width() // 2
                    textY = rect.center().y() - textRect.height() // 2 
                    self.painter.drawRect(rect)
                    self.painter.setPen(pen)
                    self.painter.drawText(QPoint(textX, textY + 10 ),self.currentLabelName)

            elif self.shape == 'polygon':
                if len(self.polygonPoints) >= 1 :
                    for i in range(len(self.polygonPoints)):
                        pen = QPen(self.currentLabelColor, 2, Qt.PenStyle.DashLine)
                        self.painter.setPen(pen)
                        point = self.polygonPoints[i]
                        x, y = point.x(), point.y()
                        self.painter.drawEllipse(x, y, 3, 3)
                    if len(self.polygonPoints) >= 3 :
                        pen = QPen(self.currentLabelColor, 2, Qt.PenStyle.DashLine)
                        self.painter.setPen(pen)
                        plg = QPolygon(self.polygonPoints)
                        self.painter.drawPolygon(plg)
                        self.painter.setPen(pen)
                        boundingRect4Plg = plg.boundingRect()
                        fontMetrics = QFontMetrics(self.painter.font())
                        textRect = fontMetrics.boundingRect(self.currentLabelName)

                        textX = boundingRect4Plg.center().x() - textRect.width() // 2
                        textY = boundingRect4Plg.center().y() - textRect.height() // 2 
                        self.painter.setPen(pen)
                        self.painter.drawText(QPoint(textX, textY + 10),self.currentLabelName)

            if hasattr(self, 'paintAnnotations'):
                # Draw all paint layers
                for layer in self.paintLayers:
                    self.painter.setOpacity(0.4)
                    self.painter.drawPixmap(0, 0, layer.pixmap)
                    
                    # Draw label for each layer
                    pen = QPen(layer.color, 2, Qt.PenStyle.DashLine)
                    self.painter.setPen(pen)
                    # boundingRect = layer.pixmap.rect()
                    # textX = boundingRect.center().x()
                    # textY = boundingRect.center().y() 
                    # self.painter.drawText(QPoint(textX, textY + 10), layer.label)

            if hasattr(self, 'tempPixmap') and self.tempPixmap is not None:
                # Draw all paint layers
                for layer in self.paintLayers:
                    self.painter.setOpacity(0.4)
                    self.painter.drawPixmap(0, 0, layer.pixmap)
                    
                    # Draw label for each layer
                    pen = QPen(layer.color, 2, Qt.PenStyle.DashLine)
                    self.painter.setPen(pen)
                    # boundingRect = layer.pixmap.rect()
                    # textX = boundingRect.center().x()
                    # textY = boundingRect.center().y() 
                    # self.painter.drawText(QPoint(textX, textY + 10), layer.label)

        finally:
            self.painter.end()
