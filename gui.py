#   Main GUI setup and window management

#   Imports
import os
import numpy as np
from matplotlib import pyplot as plt
from annotation import AnnotatableImageDisplay, LabelCard 
from utils import WindowingSlider
from image_loader import DicomLoader 
from save_manager import DicomSaver
from PyQt6.QtCore import QSize, Qt, QRect, QPoint, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QMouseEvent, QPixmap, QImage, QPainter, QPen, QColor
from PyQt6.QtWidgets import (QSlider, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QToolButton,
    QVBoxLayout, QWidget, QSizePolicy, QStatusBar, QDialogButtonBox, QPushButton, QColorDialog, QComboBox, QMessageBox)

#   Main Window

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        #   Title & Size
        self.setWindowTitle('Ligma Annotate')
        self.setFixedSize(QSize(1300, 600))
        self.fileLoadedFlag = False
        self.dicomLoader = None
        self.dicomSaver = DicomSaver()
        self.fltMin = 0
        self.fltMax = 0
        
        #   Menu Bar
        menu = self.menuBar()
        fileMenu = menu.addMenu('&File')

        #   Open Button
        openButton = QAction('&Open Medical Image', self)
        openButton.setStatusTip('Open a file')
        openButton.triggered.connect(self.openFile)
        fileMenu.addAction(openButton)
        fileMenu.addSeparator()

        #   Save Button
        saveButton = QAction('&Export Annotation Mask', self)
        saveButton.setStatusTip('Save a file')
        saveButton.triggered.connect(self.saveFile)
        fileMenu.addAction(saveButton)
        fileMenu.addSeparator()
        
        #   Exit Button
        exitButton = QAction('&Exit', self)
        exitButton.setStatusTip('Exit')
        exitButton.triggered.connect(self.exitProgram)
        fileMenu.addAction(exitButton)

        #   Edit Button
        editMenu = menu.addMenu('&Edit')
        
        #   Help Button
        helpMenu = menu.addMenu('&Help')

        #   Doc Button
        docButton = QAction('&About', self)
        docButton.setStatusTip('About')
        docButton.triggered.connect(self.documentation)
        helpMenu.addAction(docButton)

        #   Layouts

        #   Main Layout

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout()
        centralWidget.setLayout(mainLayout)
        centralWidget.setStyleSheet('background-color: #23272a')
        
        #   Left-side panel
        self.leftSidePanel = QWidget()
        self.leftLayout = QVBoxLayout()
        self.leftSidePanel.setLayout(self.leftLayout)

        #   Tools Section
        toolsContainer = QWidget()
        toolsLayout = QVBoxLayout(toolsContainer) 
        toolsContainer.setStyleSheet('''
        background-color: #2c2f33;
        border-radius: 25px;
        padding: 10px;
        ''')

        #   Select button
        selectButton = QToolButton()
        selectButton.setText('Move')
        selectButton.clicked.connect(self.enableSelectionMode)
        selectButton.setStyleSheet('''
        QToolButton {
            background-color: #2c2f33;
            border: 2px solid #7289da;
            border-radius: 13px;
            padding: 10px;
            color: #ffffff;
        }
        QToolButton:hover {
            background-color: #3b3e45;
            border: 2px solid #99aab5;
        }
        QToolButton:pressed {
            background-color: #23272a;
            border: 2px solid #7289da;
        }
        ''')

        #   Rect button
        rectButton = QToolButton()
        rectButton.setText('Rectangle')
        rectButton.clicked.connect(self.enableRectMode)
        rectButton.setStyleSheet('''
        QToolButton {
            background-color: #2c2f33;
            border: 2px solid #7289da;
            border-radius: 13px;
            padding: 10px;
            color: #ffffff;
        }
        QToolButton:hover {
            background-color: #3b3e45;
            border: 2px solid #99aab5;
        }
        QToolButton:pressed {
            background-color: #23272a;
            border: 2px solid #7289da;
        }
        ''')

        #   Polygon button
        polyButton = QToolButton()
        polyButton.setText('Polygon')
        polyButton.clicked.connect(self.enablePlgMode)
        polyButton.setStyleSheet('''
        QToolButton {
            background-color: #2c2f33;
            border: 2px solid #7289da;
            border-radius: 13px;
            padding: 10px;
            color: #ffffff;
        }
        QToolButton:hover {
            background-color: #3b3e45;
            border: 2px solid #99aab5;
        }
        QToolButton:pressed {
            background-color: #23272a;
            border: 2px solid #7289da;
        }
        ''')

        #   Paint button
        paintButton = QToolButton()
        paintButton.setText('Brush')
        paintButton.clicked.connect(self.enablePaintMode)
        paintButton.setStyleSheet('''
        QToolButton {
            background-color: #2c2f33;
            border: 2px solid #7289da;
            border-radius: 13px;
            padding: 10px;
            color: #ffffff;
        }
        QToolButton:hover {
            background-color: #3b3e45;
            border: 2px solid #99aab5;
        }
        QToolButton:pressed {
            background-color: #23272a;
            border: 2px solid #7289da;
        }
        ''')

        #   Clear button
        clearButton = QToolButton()
        clearButton.setText('Clear')
        clearButton.clicked.connect(self.enableClearMode)
        clearButton.clicked.connect(self.clearLabelContainer)
        clearButton.setStyleSheet('''
        QToolButton {
            background-color: #2c2f33;
            border: 2px solid #7289da;
            border-radius: 13px;
            padding: 10px;
            color: #ffffff;
        }
        QToolButton:hover {
            background-color: #3b3e45;
            border: 2px solid #99aab5;
        }
        QToolButton:pressed {
            background-color: #23272a;
            border: 2px solid #7289da;
        }
        ''')
        toolsLayout.addWidget(selectButton)
        toolsLayout.addWidget(rectButton)
        toolsLayout.addWidget(polyButton)
        toolsLayout.addWidget(paintButton)
        toolsLayout.addWidget(clearButton)
        self.leftLayout.addWidget(toolsContainer)
        self.leftLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.leftSidePanel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        mainLayout.addWidget(self.leftSidePanel)

        #   Middle Panel (image)

        #   Image Section Title
        self.imageString = 'Image Section'
        self.imageTitle = QLabel(self.imageString)
        self.imageTitle.setStyleSheet('''
            background-color:  #3b3e45;
            border-bottom: 2px solid #7289da;
            border-radius: 10px;
            color: #ffffff;
            padding: 5px;
        ''')

        #   Image placeholder

        self.imageDisplay = AnnotatableImageDisplay('Image Placeholder')
        self.imageDisplay.labelDialog.labelAdded.connect(self.updateLabelContainer)
        self.imageDisplay.setSelectionMode()
        self.imageDisplay.setStyleSheet('''
        background-color: #2c2f33;
        border-radius: 25px;
        ''')
        self.imageDisplay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageDisplay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.imageLayout = QVBoxLayout()
        self.imageLayout.addWidget(self.imageTitle)
        self.imageLayout.addWidget(self.imageDisplay)

        #   Labels container 

        self.labelContainer = QWidget()
        self.labelContainer.setStyleSheet('''
            background-color: #2c2f33;
            border-radius: 25px;
        ''')
        self.labelContainer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        #   Vertical layout for labelCard stack
        self.labelTitleLayout = QVBoxLayout(self.labelContainer) 

        self.labelContainerString= 'Labels'
        self.labelContainerTitle= QLabel(self.labelContainerString)
        self.labelContainerTitle.setFixedHeight(50)
        self.labelContainerTitle.setStyleSheet('''
            background-color:  #3b3e45;
            border-bottom: 2px solid #7289da;
            border-radius: 10px;
            color: #ffffff;
            padding: 15px;
        ''')
        self.labelTitleLayout.addWidget(self.labelContainerTitle)
        self.labelTitleLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 

        self.labelLayout = QVBoxLayout()
        self.labelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.labelTitleLayout.addLayout(self.labelLayout)

        imageSection = QWidget()
        imageSection.setLayout(self.imageLayout)

        mainLayout.addWidget(imageSection)
        mainLayout.addWidget(self.labelContainer)

        #   Right Panel

        #   Tools Section
        
        self.rightPanel = QWidget()
        self.rightLayout = QVBoxLayout()
        self.rightPanel.setLayout(self.rightLayout)
        self.rightPanel.setStyleSheet('''
            background-color: #2c2f33;
            border-radius: 10px;
        ''')
        self.rightPanel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #   Fields

        self.fieldsLayout = QVBoxLayout()

        self.fieldsString = 'Windowing Tools'
        self.fieldsTitle = QLabel(self.fieldsString)
        self.fieldsTitle.setStyleSheet('''
            background-color: #3b3e45;
            border-bottom: 2px solid #7289da;
            border-radius: 10px;
            color: #ffffff;
            padding: 15px;
        ''')

        self.fieldsContainer = QWidget()
        self.fieldsContainer.setFixedHeight(50)
        self.fieldsContainer.setStyleSheet('''
            background-color: #3b3e45;
            border-radius: 10px;

        ''')

        self.fieldsContainerLayout = QHBoxLayout()
        self.fieldsContainerLayout.setContentsMargins(10, 10, 10, 10)

        field_style = '''
                    QLineEdit {
                        background-color: #ffffff;
                        border: 2px solid #7289da;
                        border-radius: 10px;
                        padding: 5px;
                        font-size: 10px;
                        color: #2c2f33;
                    }
                    QLineEdit:focus {
                        border-color: #99aab5;
                    }
                '''


        # Window Center Field
        self.wcLabel = QLabel("Window Center:")
        self.wcLabel.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.wcField = QLineEdit()
        self.wc = self.wcField.text()
        self.wcField.editingFinished.connect(self.updateActualWC)
        self.wcField.setFixedSize(100, 30)
        self.wcField.setStyleSheet(field_style)
        self.wcField.setPlaceholderText("Window Center")

        # Window Width Field
        self.wwLabel = QLabel("Window Width:")
        self.wwLabel.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.wwField = QLineEdit()
        self.ww = self.wcField.text()
        self.wwField.editingFinished.connect(self.wwFieldUpdatesSlider)
        self.wwField.setFixedSize(100, 30)
        self.wwField.setStyleSheet(field_style)
        self.wwField.setPlaceholderText("Window Width")

        self.fieldsContainerLayout.addWidget(self.wcField)
        self.fieldsContainerLayout.addWidget(self.wwField)
        self.fieldsContainer.setLayout(self.fieldsContainerLayout)

        self.fieldsLayout.addWidget(self.fieldsTitle)
        self.fieldsLayout.addWidget(self.fieldsContainer)

        self.rightLayout.addLayout(self.fieldsLayout)
        self.rightLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        #   Window Slider

        self.sliderWidget = QWidget()
        self.sliderLayout = QVBoxLayout()
        self.sliderWidget.setLayout(self.sliderLayout)
        self.sliderWidget.setStyleSheet('''
            background-color: #3b3e45;
            border-radius: 10px;
        ''')
        self.windowSlider = WindowingSlider()
        self.windowSlider.setStyleSheet('''
            border-bottom: 2px solid #7289da;
            border-radius: 10px;
            padding: 15px;
        ''')
        self.windowSlider.wcEdited.connect(self.updateWCSlider)
        self.windowSlider.wwEdited.connect(self.updateWWSlider)

        self.sliderLayout.addWidget(self.windowSlider)
        self.rightLayout.addWidget(self.sliderWidget)

        #   Windowing Presets

        self.presetWidget = QWidget()
        self.presetWidget.setStyleSheet('''
            background-color: #3b3e45;
            border-radius = 10px;
        ''')
        self.presetLayout = QVBoxLayout()
        self.presetWidget.setLayout(self.presetLayout)

        self.presetLabel = QLabel('Preset:', self)
        self.presetLabel.setStyleSheet('''
            color: #ffffff;
        ''')
        self.presetLayout.addWidget(self.presetLabel)

        self.presetComboBox = QComboBox(self)
        self.presetComboBox.setStyleSheet('''
            color: #ffffff;
            border: 2px solid #7289da;
            font-weight: bold;
            border-radius: 5px;
        ''')

        self.presetComboBox.addItem('Head & Neck: Brain')
        self.presetComboBox.addItem('Head & Neck: Subdural')
        self.presetComboBox.addItem('Head & Neck: Temporal Bones')
        self.presetComboBox.addItem('Head & Neck: Soft Tissues')
        self.presetComboBox.addItem('Head & Neck: Stroke')
        self.presetComboBox.addItem('Chest: Lung')
        self.presetComboBox.addItem('Chest: Mediastinum')
        self.presetComboBox.addItem('Abdomen: Soft Tissues')
        self.presetComboBox.addItem('Abdomen: Liver')
        self.presetComboBox.addItem('Spine: Soft Tissues')
        self.presetComboBox.addItem('Spine: Bone')

        self.presetComboBox.currentIndexChanged.connect(self.presetChanged)

        self.presetLayout.addWidget(self.presetComboBox)
        self.rightLayout.addWidget(self.presetWidget)

        mainLayout.addWidget(self.rightPanel)

        #   Portions

        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(1, 3)
        mainLayout.setStretch(2, 2)
        mainLayout.setStretch(3, 2)

        #   Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet('''
            background-color: #2c2f33;
            border-top: 2px solid #7289da;
            color: #ffffff;
            padding: 5px;
        ''')
        self.statusBar.showMessage('Created by Alireza Jalouli - Summer 2024')

        #   Spacing

        mainLayout.setSpacing(20)
        mainLayout.setContentsMargins(10, 10, 10, 10)

    def displayImage(self, imageArray):

        fig, ax = plt.subplots(figsize = (5, 5))
        
        ax.imshow(imageArray, cmap='gray', aspect='auto')
        
        ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        fig.canvas.draw()
        
        width, height = fig.canvas.get_width_height()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8').reshape(height, width, 3)
        qImage = QImage(image.data, width, height, QImage.Format.Format_RGB888)
        
        qPixmap = QPixmap.fromImage(qImage)
        
        #   Scale QPixmap if necessary: for save we need this ratio
        labelHeight = self.imageDisplay.height()
        scaledPixmap = qPixmap.scaledToHeight(labelHeight, Qt.TransformationMode.SmoothTransformation)
        imgW = scaledPixmap.width()
        self.dicomSaver.dspImgW= imgW
        
        self.imageDisplay.setPixmap(scaledPixmap)
        
        plt.close(fig)

    def openFile(self):

        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, 'Open Medical File', '', 'DICOM Files (*.dcm);;NIfTI Files (*.nii);;JPEG Files (*.jpg);;All Files (*)')

        self.loadPath = filePath
        if filePath:
            self.fileLoadedFlag = True
            _, fileExtension = os.path.splitext(filePath)
            if fileExtension.lower() == '.dcm':

                self.dicomLoader = DicomLoader()
                self.imageArray, dicomData, wc, ww = self.dicomLoader.di2num(filePath = filePath)
                imageArray = self.dicomLoader.display(data = self.imageArray)

                if wc is not None and ww is not None:
                    self.updateWs(wc, ww)

                if imageArray is not None:
                    self.displayImage(imageArray)
                    self.dicomSaver.actImgW = self.imageArray.shape[0]
                    self.dicomSaver.updateTr()

                #elif fileExtension.lower() == '.nii':
                #    print('This is a NIfTI file.')

                #    imageArray, niiData = ni2num(filePath)

                #    if imageArray is not None:
                #        self.displayImage(imageArray)


        self.imageString = os.path.basename(filePath)
        self.imageTitle.setText(self.imageString)
        self.fltMin = self.dicomLoader.dataMin
        self.fltMax = self.dicomLoader.dataMax
        self.windowSlider.imageLoaded = True
        self.translateRatio = self.translateRatioFinder(self.fltMin, self.fltMax)
        self.windowSlider.stringMax = str(f'{self.dicomLoader.dataMax:.1f}')
        self.windowSlider.stringMin = str(f'{self.dicomLoader.dataMin:.1f}')

    def translateRatioFinder(self, fltMin, fltMax):
        tr = float((fltMax - fltMin) // 277)
        self.windowSlider.updateParams(fltMin, fltMax, tr)
        return tr

    def updateWs(self, wc, ww):
        self.loadedWc = wc
        self.loadedWw = ww
        self.wcField.setText(str(wc))
        self.wwField.setText(str(ww))
        self.update()

    def updateActualWC(self):
        if self.dicomLoader is not None:
            wc = int(self.wcField.text())
            if wc < self.fltMin or wc > self.fltMax:
                QMessageBox.warning(self, 'Input Error', "Window Center is not in DICOM file's data range.", QMessageBox.StandardButton.Ok)
                wc = self.loadedWc
                self.wcField.setText(str(wc))

            #   TODO: tomorrow fix this shit!
            self.dicomLoader.firstLoadFlag = False
            if type(wc) == int and self.dicomLoader is not None:
                self.windowSlider.wcField = wc
                self.windowSlider.reverseKnobLocationUpdate()
                if self.dicomLoader.dataMin < wc < self.dicomLoader.dataMax:
                    newData = self.dicomLoader.setWC(to = wc)
                    newImgArr = self.dicomLoader.display(newData)
                    print(newImgArr)
                    self.displayImage(newImgArr)
                else:
                    wc = self.dicomLoader.wc
                    self.update()


    def updateWCSlider(self):
        if self.dicomLoader is not None:
            wc = self.windowSlider.newWc
            wc = int(wc)
            print('new wc is:', wc)
            self.wcField.setText(str(wc))
            self.dicomLoader.firstLoadFlag = False
            self.updateActualWC()

    def updateWWSlider(self):
        if self.dicomLoader is not None:
            ww = self.windowSlider.newWw
            ww = int(ww)
            self.wwField.setText(str(ww))
            self.dicomLoader.firstLoadFlag = False
            self.updateActualWW()
                
    def wwFieldUpdatesSlider(self):
        if self.dicomLoader is not None:
            ww = int(self.wwField.text())
            if ww > 6000:
                QMessageBox.warning(self, 'Input Error', "Window width is out of DICOM file's data range.", QMessageBox.StandardButton.Ok)
                ww = self.loadedWw
                self.wcField.setText(str(ww))
            self.windowSlider.wwField = ww
            self.windowSlider.reverseWheelEvent()
            self.updateActualWW()

    def updateActualWW(self):
        ww = int(self.wwField.text())
        self.dicomLoader.firstLoadFlag = False
        if type(ww) == int and self.dicomLoader is not None:
            if self.dicomLoader.dataMin < ww < self.dicomLoader.dataMax:
                newData = self.dicomLoader.setWW(to = ww)
                newImgArr = self.dicomLoader.display(newData)
                print(newImgArr)
                self.displayImage(newImgArr)
            else:
                wc = self.dicomLoader.wc
                self.update()

    def presetChanged(self):

        selectedOption = self.presetComboBox.currentText()
        if self.fileLoadedFlag:
            if selectedOption == 'Head & Neck: Brain':
                self.wcField.setText('40')
                self.wwField.setText('80')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Head & Neck: Subdural':
                self.wcField.setText('75')
                self.wwField.setText('215')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Head & Neck: Temporal Bones':
                self.wcField.setText('600')
                self.wwField.setText('2800')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Head & Neck: Soft Tissues':
                self.wcField.setText('50')
                self.wwField.setText('350')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Head & Neck: Stroke':
                self.wcField.setText('40')
                self.wwField.setText('40')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Chest: Lung':
                self.wcField.setText('-600')
                self.wwField.setText('1500')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Chest: Mediastinum':
                self.wcField.setText('50')
                self.wwField.setText('350')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Abdomen: Soft Tissues':
                self.wcField.setText('50')
                self.wwField.setText('400')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Abdomen: Liver':
                self.wcField.setText('70')
                self.wwField.setText('150')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Spine: Soft Tissues':
                self.wcField.setText('50')
                self.wwField.setText('250')
                self.updateActualWC()
                self.updateActualWW()
            elif selectedOption == 'Spine: Bone':
                self.wcField.setText('400')
                self.wwField.setText('1800')
                self.updateActualWC()
                self.updateActualWW()

    def updateLabelContainer(self, labelName, labelColor):
        #   Makes a new label card
        labelCard = LabelCard(labelName, labelColor)
        labelCard.labelDeleted.connect(self.imageDisplay.removeAnnotation)
        labelCard.labelDeleted.connect(self.imageDisplay.removePolyGs)
        labelCard.labelDeleted.connect(self.imageDisplay.removePainting)
        labelCard.labelEdited.connect(self.imageDisplay.renameAnnotation)
        labelCard.labelColorEdited.connect(lambda name, card: self.imageDisplay.recolorAnnotation(name, card))
        self.labelLayout.addWidget(labelCard)
        self.labelLayout.update()

    def clearLabelContainer(self):
        while self.labelLayout.count():
            item = self.labelLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def saveFile(self):
        if self.fileLoadedFlag: 
            fileDialog = QFileDialog()
            filePath, t = fileDialog.getSaveFileName(self, 'Save File', '', 'Numpy File (Masks) (*.npy);;NIfTI File(Masks) (*.nii.gz);;CSV File (Masks) (*.csv);;JSON File(COCO Formatting) (*.json)')
            if not self.imageDisplay.isEmpty:
                if t == 'Numpy File (Masks) (*.npy)':
                    if self.imageDisplay.shape == 'rectangle':
                        self.dicomSaver.rect2npy(filePath, self.imageArray, self.imageDisplay.annotations)
                    elif self.imageDisplay.shape == 'polygon':
                        self.dicomSaver.poly2npy(filePath, self.imageArray, self.imageDisplay.polygonPoints, self.imageDisplay.currentLabelName)
                    elif self.imageDisplay.shape == 'paint':
                        self.dicomSaver.paint2npy(filePath, self.imageArray, self.imageDisplay.paintLayers)

                elif t == 'CSV File (Masks) (*.csv)':
                    if self.imageDisplay.shape == 'rectangle':
                        self.dicomSaver.rect2csv(filePath, self.imageArray, self.imageDisplay.annotations, self.loadPath)
                    elif self.imageDisplay.shape == 'polygon':
                        self.dicomSaver.poly2csv(filePath, self.imageArray, self.imageDisplay.polygonPoints,
                                                 self.imageDisplay.currentLabelName, self.loadPath)
                    elif self.imageDisplay.shape == 'paint':
                        QMessageBox.warning(self, 'Save Error', "CSV export for paint is not available.", QMessageBox.StandardButton.Ok)

                elif t == 'JSON File(COCO Formatting) (*.json)':
                    if self.imageDisplay.shape == 'rectangle':
                        self.dicomSaver.rect2json(filePath, self.imageArray, self.imageDisplay.annotations, self.loadPath)
                    elif self.imageDisplay.shape == 'polygon':
                        self.dicomSaver.poly2json(filePath, self.imageArray, self.imageDisplay.polygonPoints,
                                                  self.imageDisplay.currentLabelName, self.loadPath)
                    elif self.imageDisplay.shape == 'paint':
                        QMessageBox.warning(self, 'Save Error', "JSON export for paint is not available.", QMessageBox.StandardButton.Ok)
                elif t == 'NIfTI File(Masks) (*.nii.gz)':
                    if self.imageDisplay.shape == 'rectangle':
                        self.dicomSaver.rect2nii(filePath, self.imageArray, self.imageDisplay.annotations)
                    elif self.imageDisplay.shape == 'polygon':
                        self.dicomSaver.poly2nii(filePath, self.imageArray, self.imageDisplay.polygonPoints,
                                                  self.imageDisplay.currentLabelName)
                    elif self.imageDisplay.shape == 'paint':
                        self.dicomSaver.paint2nii(filePath, self.imageArray, self.imageDisplay.paintLayers)


    def documentation(self):
        QMessageBox.information(self, 'About', "This piece of software was written in python by Alireza Jalouli in Summer 2024 (1403)\nGitHub: @itsalirezajalouli", QMessageBox.StandardButton.Ok)

    def enableSelectionMode(self):
        self.imageDisplay.setSelectionMode()

    def enableRectMode(self):
        self.imageDisplay.setRectMode()

    def enablePlgMode(self):
        self.imageDisplay.setPolygonMode()

    def enablePaintMode(self):
        self.imageDisplay.setPaintMode()

    def enableClearMode(self):
        self.imageDisplay.setClearMode()

    def exitProgram(self):
        self.close()
