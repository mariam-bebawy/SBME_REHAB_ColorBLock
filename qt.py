############################
#### IMPORTS
############################

import os, sys, cv2, time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
# from time import time
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
        uic.loadUi(r'qt.ui', self)


        ############################
        #### BUTTON CONNECTIONS
        ############################
        self.cvimg = [[]]
        self.final = [[]]
        self.btnOpen.clicked.connect(lambda: self.open())
        

        ############################
        #### GLOBAL VARIABLES
        ############################
        # self.imageview = self.findChild(QLabel, "imageview")
        # self.disply_width = 550
        # self.display_height = 500
        

    ############################
    #### FUNCTION DEFINITIONS
    ############################

    def open(self):
        print(f"open function activated !")
        self.labelCheck.setText("CLICKED !")


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
