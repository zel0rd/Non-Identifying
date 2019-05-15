#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import pandas as pd
from pandas import Series, DataFrame
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import numpy

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import time

#to import UI path
import sys 
sys.path.append('..\\UI')


import mplwidget

global data_1
global data_2
global print_line
global new_data_2
global new_data_1

fileName = ""

class MatplotlibWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.ui = uic.loadUi("C:\\Users\\jh\\Desktop\\python\\UI\\DeIdentifierUI.ui")
        self.ui.statusbar.showMessage("Start program") #statusbar text, TODO: change dynamic text
        self.ui.show()
        
        #TODO: add event per button

    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MatplotlibWidget()
    sys.exit(app.exec_())
