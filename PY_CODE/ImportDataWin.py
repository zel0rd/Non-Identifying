#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import sys
import pandas as pd
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets

import matplotlib.pyplot as plt
plt.rc('font', family='Malgun Gothic') #한글 깨짐 방지
plt.rc('axes', unicode_minus=False) #한글 깨짐 방지

#to import UI path
sys.path.append("./UI") # insert your path
sys.path.append("./PY_CODE")

from PandasModel import PandasModel # for table model setting
from ModifyWin import ModifyDataWindow # for table model setting


#importWinows
class ImportDataWindow(QMainWindow):
    def __init__(self, MainWindow):
        super().__init__()
        self.ui = uic.loadUi("./UI/ImportData.ui") #insert your UI path
        self.ui.show()

        self.mainWin = MainWindow
        self.ui.InputData.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) #editable false
        self.ui.toolButton.clicked.connect(self.ImportDataButton)
        self.ui.cancelButton.clicked.connect(self.cancelButton)
      
    def ImportDataButton(self):
        options = QFileDialog.Options()
      #  options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  options=options)
        if fileName:
            self.inputdata = pd.read_csv(fileName, sep=",",encoding='euc-kr') #read file
            path = os.getcwd() + fileName
            self.ui.filePath.append(path) #show file path

            DataModel = PandasModel(self.inputdata.iloc[:40]) #show 40 rows
            self.ui.InputData.setModel(DataModel) #speed up

            """
            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.InputData.setColumnCount(colnum) #Set Column Count   
            self.ui.InputData.setRowCount(rownum) 
            self.ui.InputData.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.InputData.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))
            """

            self.ui.nextButton.clicked.connect(self.nextButton)

    
    def nextButton(self):
        self.ui.hide()
        self.modify = ModifyDataWindow(self.mainWin, self, self.inputdata)


    def cancelButton(self):
        self.ui.hide()
        