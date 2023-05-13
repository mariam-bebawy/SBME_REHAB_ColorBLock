############################
#### IMPORTS
############################


# CHECK BRIGHTNESS
# CHECK CLR THEORY

import os, sys, cv2, colorsys, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from collections import Counter
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, deltaE_cie76, rgb2hsv

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.set_facecolor('#e1e1e1')
        super(MplCanvas, self).__init__(self.fig)


############################
#### CONNECT MAIN WINDOW
############################

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        ############################
        #### LOAD UI FILE
        ############################
        uic.loadUi(r'ui.ui', self)


        ############################
        #### BUTTON CONNECTIONS
        ############################
        self.img = [[]]
        self.height, self.width = 500, 500      # resizing
        self.window = [[]]      # ROI window
        self.clr1, self.clr2 = [], []

        self.clrThrFUNC = [
            self.complimentary, 
            self.splitComplimentary, 
            self.analogous, 
            self.triadic, 
            self.tetradic, 
        ]

        # 4 push buttons
        self.btnOpen1.clicked.connect(lambda: self.openImg(1))
        self.btnOpen2.clicked.connect(lambda: self.openImg(2))
        self.btnMatch.setEnabled(False)
        self.btnMatch.clicked.connect(lambda: self.checkMatch())
        self.btnClear.clicked.connect(lambda: self.clear())


        ############################
        #### GLOBAL VARIABLES
        ############################
        self.graph = pg.PlotItem()
        pg.PlotItem.hideAxis(self.graph, 'left')
        pg.PlotItem.hideAxis(self.graph, 'bottom')

        self.wdgColor1.setCentralItem(self.graph)
        self.wdgColor1.setBackground(QtGui.QColor('#e1e1e1'))

        self.wdgColor2.setCentralItem(self.graph)
        self.wdgColor2.setBackground(QtGui.QColor('#e1e1e1'))
        

    ############################
    #### FUNCTION DEFINITIONS
    ############################

    def openImg(self, val):
        # browse for image
        path = QFileDialog.getOpenFileName(
            self, "Open File", "This PC", 
            "All FIles (*);; PNG Files(*.png);; JPG Files (*.jpg)"
        )
        img = cv2.imread(path[0])

        # prompting the user to upload a bright image
        if self.checkBrightness(img) == 0 :
            self.openImg(val)
        
        # get ROI window to get color later on
        img = self.getROI(img)
        clrRGB = self.getColor(img)
        clrHEX = self.RGB2HEX(clrRGB)

        # set background color of empty label
        if val == 1 :
            self.clr1 = clrRGB
            # self.lblColor1.setText(f"RGB : {clrRGB}\nHEX : {clrHEX}")
            self.wdgColor1.setBackground(QtGui.QColor(clrHEX))
        else :
            self.clr2 = clrRGB
            # self.lblColor2.setText(f"RGB : {clrRGB}\nHEX : {clrHEX}")
            self.wdgColor2.setBackground(QtGui.QColor(clrHEX))

        if len(self.clr1) != 0 and len(self.clr2) != 0 :
            self.btnMatch.setEnabled(True)

    def checkBrightness(self, img, threshold=150):
        """
        checks the overall brightness of an image
        to make sure colors are interpreted correctly

        if brightness is lower than threshold,
        user is prompted to take another image
        """
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        values = img[:, :, 2]
        brightness = int(np.mean(values))
        # print(f"average brightness of image = {brightness}")

        if brightness < threshold : return 0
        else : return 1

    def getROI(self, img, margin=100):
        """
        resizing of image to given width and height
        cropping ROI of image to get ROI window
        """
        img = cv2.resize(img, (self.height, self.width))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        self.window = img[
            h//2-margin:h//2+margin, 
            w//2-margin:w//2+margin
        ]
        return img
    
    def getColor(self, img, n=3):
        """
        kmeans method on ROI
        return RGB and HEX

        average color vs dominant color !!!
        """
        # AVERAGING IS THE SAME AS CHOOSING n_clusters=1
        # avgRow = np.average(img, axis=0)
        # avg = np.average(avgRow,axis=0).astype(int)
        # return avg

        # kmeans METHOD RETURNS COLOURS IN ORDER OF MOST DOMINANT
        imgMod = img.reshape(img.shape[0] * img.shape[1], 3)
        clf = KMeans(n_clusters = n)
        labels = clf.fit_predict(imgMod)
        counts = Counter(labels)
        counts = dict(sorted(counts.items()))
        clrsCenter = clf.cluster_centers_
        clrsOrdered = [clrsCenter[i] for i in counts.keys()]
        clrsHEX = [self.RGB2HEX(clrsOrdered[i]) for i in counts.keys()]
        clrsRGB = [clrsOrdered[i] for i in counts.keys()]

        print(f"rgb : {clrsRGB}, type : {type(clrsRGB)}")
        print(f"hex : {clrsHEX}, type : {type(clrsHEX)}")
        return clrsRGB[0]
        
    def RGB2HEX(self, color):
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

    def checkMatch(self):
        for clrThr in self.clrThrFUNC:
            CLRS = clrThr(self.clr1)
            # print(CLRS)
            for i in CLRS:
                rRange, gRange, bRange = self.createRange(i)
                # H2YFHA FOR NOW
                if not self.checkClrRange(self.clr2, rRange, gRange, bRange) :
                    self.lblMatch.setText("colors are all safe !\ncolors are a good match !")
                    break
                else :
                    self.lblMatch.setText("colors are out of range !\ntry another piece")

    def createRange(self, clr, margin=10):
        """
        create R G B ranges to check for match
        """
        r, g, b = clr
        rRange = list(range(r-margin, r+margin))
        gRange = list(range(g-margin, g+margin))
        bRange = list(range(b-margin, b+margin))
        print(f"r Range : {rRange}\ng Range : {gRange}\nb Range : {bRange}\n")
        return rRange, gRange, bRange
    
    def checkClrRange(self, clr, rRange, gRange, bRange):
        """
        check given color with color ranges
        """
        if (clr[0] not in rRange) and (clr[1] not in gRange) and (clr[2] not in bRange) :
            return 0
        return 1
    
    def complimentary(self, val):
        """
        Takes rgb tuple and produces complimentary color.
        """
        #value has to be 0 < x 1 in order to convert to hls
        r, g, b = map(lambda x: x/255.0, val)
        #hls provides color in radial scale
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        #get hue changes at 150 and 210 degrees
        deg_180_hue = h + (180.0 / 360.0)
        color_180_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_180_hue, l, s)))
        return [color_180_rgb]

    def splitComplimentary(self, val):
        """
        Takes rgb tuple and produces list of split complimentary colors.
        """
        #value has to be 0 <span id="mce_SELREST_start" style="overflow:hidden;line-height:0;"></span>&lt; x 1 in order to convert to hls
        r, g, b = map(lambda x: x/255.0, val)
        #hls provides color in radial scale
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        #get hue changes at 150 and 210 degrees
        deg_150_hue = h + (150.0 / 360.0)
        deg_210_hue = h + (210.0 / 360.0)
        #convert to rgb
        color_150_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_150_hue, l, s)))
        color_210_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_210_hue, l, s)))
        return [color_150_rgb, color_210_rgb]
    
    def analogous(self, val, d=100):
        """
        Takes rgb tuple and angle (out of 100) and produces list of analogous colors)
        """
        analogous_list = []
        #set color wheel angle
        d = d /360.0
        #value has to be 0 <span id="mce_SELREST_start" style="overflow:hidden;line-height:0;"></span>&lt; x 1 in order to convert to hls
        r, g, b = map(lambda x: x/255.0, val)
        #hls provides color in radial scale
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        #rotate hue by d
        h = [(h+d) % 1 for d in (-d, d)]
        for nh in h:
            new_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(nh, l, s)))
            analogous_list.append(new_rgb)
        return analogous_list

    def triadic(self, val):
        """
        Takes rgb tuple and produces list of triadic colors.
        """
        #value has to be 0 < x 1 in order to convert to hls
        r, g, b = map(lambda x: x/255.0, val)
        #hls provides color in radial scale
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        #get hue changes at 120 and 240 degrees
        deg_120_hue = h + (120.0 / 360.0)
        deg_240_hue = h + (240.0 / 360.0)
        #convert to rgb
        color_120_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_120_hue, l, s)))
        color_240_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_240_hue, l, s)))
        return [color_120_rgb, color_240_rgb]
    
    def tetradic(self, val):
        """
        Takes rgb tuple and produces list of tetradic colors.
        """
        #value has to be 0 <span id="mce_SELREST_start" style="overflow:hidden;line-height:0;"></span>&lt; x 1 in order to convert to hls
        r, g, b = map(lambda x: x/255.0, val)
        #hls provides color in radial scale
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        #get hue changes at 120 and 240 degrees
        deg_60_hue = h + (60.0 / 360.0)
        deg_180_hue = h + (180.0 / 360.0)
        deg_240_hue = h + (240.0 / 360.0)
        #convert to rgb
        color_60_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_60_hue, l, s)))
        color_180_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_180_hue, l, s)))
        color_240_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_240_hue, l, s)))
        return [color_60_rgb, color_180_rgb, color_240_rgb]
    
    def clear(self):
        self.clr1, self.clr2 = [], []
        self.wdgColor1.setBackground(QtGui.QColor('#e1e1e1'))
        self.wdgColor2.setBackground(QtGui.QColor('#e1e1e1'))
        self.lblMatch.setText("")
        self.btnMatch.setEnabled(False)


############################
#### CALL MAIN FUNCTION
############################

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
