# Logic for saving annotations & exporting data

import os
import math
import numpy as np
import pandas as pd
import nibabel.nifti1 as nib
from PyQt6.QtGui import QImage
from matplotlib.path import Path
from skimage.transform import resize

class DicomSaver:

    def __init__(self) -> None:
        self.dspImgW = None
        self.actImgW = None
        self.tr = None

    def rect2npy(self, path: str, arr: np.ndarray, annotations: list) -> None:

        for annotation in annotations:
            maskName = annotation['label']
            maskPath = path + '_' + maskName + '_mask' 
            bbox = annotation['bbox']
            newBbox = [math.floor(i * self.tr) for i in bbox]
            x1, y1, x2, y2 = newBbox
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            mask = np.zeros_like(arr)
            for i in range(len(mask)):
                for j in range(len(mask[i])):
                    if y1 <= i <= y2:
                        if x1 <= j <= x2:
                            mask[i][j] = 1
            np.save(maskPath, mask)

        # mainPath = path + '_main'
        # np.save(mainPath, arr)


    def rect2csv(self, path: str, arr: np.ndarray, annotations: list, imgpath: str) -> None:
        mainPath = path + '_main'
        print('main: ', mainPath)
        df = pd.DataFrame()

        for annotation in annotations:
            maskName = annotation['label']
            maskPath = path + '_' + maskName + '_mask' 
            bbox = annotation['bbox']
            newBbox = [math.floor(i * self.tr) for i in bbox]
            print(newBbox)
            x1, y1, x2, y2 = newBbox
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            values = (x1, y1, x2, y1, x1, y2, x2, y2)
            newRow = {
                'image path': imgpath,
                maskName: values  
            }
            
            df = pd.concat([df, pd.DataFrame([newRow])], ignore_index=True)
        
        csvPath = path + '_masks.csv'
        df.to_csv(csvPath)
        # mainPath = path + '_main'
        # np.save(mainPath, arr)


    def rect2json(self, path: str, arr: np.ndarray, annotations: list, imgpath: str) -> None:
        df = pd.DataFrame()

        for annotation in annotations:
            maskName = annotation['label']
            bbox = annotation['bbox']
            newBbox = [math.floor(i * self.tr) for i in bbox]
            x1, y1, x2, y2 = newBbox
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            bboxVals = [x1, y1, x2 - x1, y2 - y1]
            segmentation = [x1, y1, x2, y1, x2, y2, x1, y2]
            W = x2 - x1
            H = y2 - y1
            area = W * H 

            newRow = {
                'image path': imgpath,
                'label': maskName,
                'bbox': bboxVals,
                'area': area,
                'segmentation': segmentation,
                'width': W,
                'height': H,
            }
            
            df = pd.concat([df, pd.DataFrame([newRow])], ignore_index=True)
        
        jsonPath = path + '_masks.json'
        df.to_json(jsonPath, orient='records', indent=4)


    def rect2nii(self, path: str, arr: np.ndarray, annotations: list) -> None:
        for annotation in annotations:
            maskName = annotation['label']
            maskPath = path + '_' + maskName + '_mask.nii.gz'
            bbox = annotation['bbox']
            newBbox = [math.floor(i * self.tr) for i in bbox]
            x1, y1, x2, y2 = newBbox
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            mask = np.zeros_like(arr)
            mask[y1:y2+1, x1:x2+1] = 1
            niimg = nib.Nifti1Image(mask, np.eye(4))
            nib.save(niimg, maskPath)


    def poly2npy(self, path: str, arr: np.ndarray, ppoints: list, pname: str) -> None:

        verts: list[tuple] = []
        codes: list = [Path.MOVETO]
        for point in ppoints:
            x = point.x()
            y = point.y()
            x = int(x * self.tr)
            y = int(y * self.tr)
            verts.append((x, y))
            codes.append(Path.LINETO)
        codes.pop()
        codes.pop()
        codes.append(Path.CLOSEPOLY)
        poly = Path(verts, codes)
        n = self.actImgW
        x = np.arange(self.actImgW)
        y = np.arange(self.actImgW)
        xx, yy= np.meshgrid(x, y)
        points = np.vstack((xx.ravel(), yy.ravel())).T
        mask = poly.contains_points(points)
        mask = mask.reshape(self.actImgW, self.actImgW)
        maskName = pname
        maskPath = path + '_' + maskName + '_mask' 
        np.save(maskPath, mask)
        # mainPath = path + '_main'
        # np.save(mainPath, arr)


    def poly2csv(self, path: str, arr: np.ndarray, ppoints: list, pname: str, imgpath: str) -> None:
        mainPath = path + '_main'
        print('main: ', mainPath)
        df = pd.DataFrame()

        verts: list[tuple] = []
        for point in ppoints:
            x = point.x()
            y = point.y()
            x = int(x * self.tr)
            y = int(y * self.tr)
            verts.append((x, y))
            print('points x:', x, end = ', ')
            print('points y:', y)

        newRow = {
            'image path': imgpath,
            pname: verts
        }
        df = pd.concat([df, pd.DataFrame([newRow])], ignore_index=True)
        
        csvPath = path + '_masks.csv'
        df.to_csv(csvPath)
        # mainPath = path + '_main'
        # np.save(mainPath, arr)


    def poly2nii(self, path: str, arr: np.ndarray, ppoints: list, pname: str) -> None:
        verts: list[tuple] = []
        codes: list = [Path.MOVETO]
        for point in ppoints:
            x = int(point.x() * self.tr)
            y = int(point.y() * self.tr)
            verts.append((x, y))
            codes.append(Path.LINETO)
        codes.pop()
        codes.append(Path.CLOSEPOLY)
        poly = Path(verts, codes)
        x, y = np.meshgrid(np.arange(self.actImgW), np.arange(self.actImgW))
        points = np.vstack((x.ravel(), y.ravel())).T
        mask = poly.contains_points(points).reshape(self.actImgW, self.actImgW)
        maskPath = path + '_' + pname + '_mask.nii.gz'
        nii_img = nib.Nifti1Image(mask, np.eye(4))
        nib.save(nii_img, maskPath)


    def paint2npy(self, path: str, arr: np.ndarray, paintLayers: list):
        for layer in paintLayers:
            qImg = layer.pixmap.toImage()
            W = qImg.width()
            H = qImg.height()
            qImg = qImg.convertToFormat(QImage.Format.Format_RGBA8888)
            ptr = qImg.bits()
            ptr.setsize(W * H * 4)
            arr = np.array(ptr).reshape(W, H, 4)

            mask = arr[:, :, 3] > 0  # Alpha channel is the 4th channel (index 3)
            print(arr.shape)

            newW = int(W * self.tr)
            newH = int(H * self.tr)
            scaledMask = resize(mask, (newW, newH), anti_aliasing = False, preserve_range = True)
            
            maskName = layer.label
            maskPath = path + '_' + maskName + '_mask' 
            scaledMask = scaledMask > 0.5
            np.save(maskPath, scaledMask)

        # mainPath = path + '_main'
        # print('main: ', mainPath)
        # np.save(mainPath, arr)


    def poly2json(self, path: str, arr: np.ndarray, ppoints: list, pname: str, imgpath: str) -> None:
        df = pd.DataFrame()

        verts: list[tuple] = []
        xMin, yMin, xMax, yMax = float('inf'), float('inf'), -float('inf'), -float('inf')

        for point in ppoints:
            x = point.x()
            y = point.y()
            x = int(x * self.tr)
            y = int(y * self.tr)
            verts.append((x, y))

            xMin, yMin = min(xMin, x), min(yMin, y)
            xMax, yMax = max(xMax, x), max(yMax, y)

        bboxVals = [xMin, yMin, xMax - xMin, yMax - yMin]
        W = xMax - xMin
        H = yMax - yMin
        area = W * H
        segmentation = [coord for vert in verts for coord in vert]

        newRow = {
            'image path': imgpath,
            'label': pname,
            'bbox': bboxVals,
            'area': area,
            'segmentation': segmentation,
            'width': W,
            'height':H, 
        }
        
        df = pd.concat([df, pd.DataFrame([newRow])], ignore_index=True)
        
        jsonPath = path + '_masks.json'
        df.to_json(jsonPath, orient='records', indent=4)


    def paint2nii(self, path: str, arr: np.ndarray, paintLayers: list):
        for layer in paintLayers:
            qImg = layer.pixmap.toImage()
            W, H = qImg.width(), qImg.height()
            qImg = qImg.convertToFormat(QImage.Format.Format_RGBA8888)
            ptr = qImg.bits()
            ptr.setsize(W * H * 4)
            arr = np.array(ptr).reshape(W, H, 4)
            mask = arr[:, :, 3] > 0
            newW, newH = int(W * self.tr), int(H * self.tr)
            scaledMask = resize(mask, (newW, newH), anti_aliasing=False, preserve_range=True)
            scaledMask = scaledMask > 0.5
            maskName = layer.label
            maskPath = path + '_' + maskName + '_mask.nii.gz'
            nii_img = nib.Nifti1Image(scaledMask.astype(np.uint8), np.eye(4))
            nib.save(nii_img, maskPath)


    def updateTr(self):
        if self.dspImgW is not None and self.actImgW:
            self.tr = self.actImgW / self.dspImgW 
