# Functions for loading DICOM and NIfTI images

import cv2
import copy
import pydicom
import numpy as np
import nibabel as nib
from PyQt6.QtWidgets import QFileDialog
from pydicom.pixel_data_handlers.util import apply_voi_lut
from scipy import ndimage

class DicomLoader:
    def __init__(self):
        self.wc = None
        self.ww = None
        self.filePath = None
        self.data = None
        self.dataMax = None
        self.dataMin = None
        self.firstLoadFlag = True

    def di2num(self, filePath):
        dicom = pydicom.read_file(filePath)
        self.wc = dicom.WindowCenter
        self.ww = dicom.WindowWidth

        if isinstance(self.wc, pydicom.multival.MultiValue):
            self.wc = int(str(self.wc[0]).lstrip('0'))
        if isinstance(self.ww, pydicom.multival.MultiValue):
            self.ww = int(str(self.ww[0]).lstrip('0'))

        self.data = apply_voi_lut(dicom.pixel_array, dicom)
        return self.data, dicom, self.wc, self.ww

    def applyWindowing(self, data):
        dataMin = self.wc - self.ww / 2
        dataMax = self.wc + self.ww / 2

        if self.firstLoadFlag:
            dataMin = self.dataMin
            dataMax = self.dataMax

        return np.clip(data, dataMin, dataMax)

    def normalize(self, data):
        return ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)

    def applyClahe(self, data, clipLimit=2.0, tileGridSize=(8, 8)):
        clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
        return clahe.apply(data)

    def adaptiveGammaCorrection(self, data):
        mean = np.mean(data)
        gamma = np.log(mean) / np.log(128)
        return np.power(data, gamma).astype(np.uint8)

    def bilateralFilter(self, data, d=9, sigmaColor=75, sigmaSpace=75):
        return cv2.bilateralFilter(data, d, sigmaColor, sigmaSpace)

    def guidedFilter(self, data, radius=5, eps=0.1):
        meanI = cv2.boxFilter(data, -1, (radius, radius))
        meanP = cv2.boxFilter(data, -1, (radius, radius))
        corrI = cv2.boxFilter(data * data, -1, (radius, radius))
        varI = corrI - meanI * meanI
        a = varI / (varI + eps)
        b = meanP - a * meanI
        meanA = cv2.boxFilter(a, -1, (radius, radius))
        meanB = cv2.boxFilter(b, -1, (radius, radius))
        q = meanA * data + meanB

    def display(self, data):
        self.dataMax = np.max(self.data)
        self.dataMin = np.min(self.data)
        dataClone = copy.deepcopy(self.data)

        dataClone = self.applyWindowing(dataClone)
        dataClone = self.normalize(dataClone)
        dataClone = self.bilateralFilter(dataClone)
        dataClone = self.adaptiveGammaCorrection(dataClone)
        dataClone = self.applyClahe(dataClone)

        return dataClone

    def setWC(self, to: int):
        self.wc = to
        return self.data

    def setWW(self, to: int):
        self.ww = to
        return self.data

#   TODO: nifti doesn't work, it's shit

