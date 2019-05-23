#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import pandas as pd
from pandas import Series, DataFrame
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets
import numpy

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import time
from datetime import datetime

#to import UI path
import sys 
sys.path.append("C:\\Users\\san\\Desktop\\D_D\\python_UI\\Non-Identifying\\UI") # insert your path

import mplwidget

global tab1_input # inputtable data in tab1
global tab2_input
#global print_line
global tab2_output
#global new_data_1

fileName = ""

class ImportDataWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ImportDataWindow, self).__init__(parent)
        self.ui = uic.loadUi("C:\\Users\\san\\Desktop\\D_D\\python_UI\\Non-Identifying\\UI\\ImportData.ui") #insert your UI path
        self.ui.show()
        self.ui.toolButton.clicked.connect(self.ImportDataButton)
        self.ui.cancelButton.clicked.connect(qApp.quit)  #try to close the window(failed!!!!!!!)

    def ImportDataButton(self):
        options = QFileDialog.Options()

        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  options=options)
        if fileName:
            inputdata = pd.read_csv(fileName, sep=",",encoding='euc-kr') #read file
            #print(inputdata)

            self.ui.filePath.setText(fileName) #show file path

            global tab1_input #need to define again 
            tab1_input = inputdata #save data in file, 파일에 있는 데이터를 변수에 저장 

            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.InputData.setColumnCount(colnum) #Set Column Count    
            self.ui.InputData.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.InputData.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))

        self.ui.nextButton.clicked.connect(self.ModifyData)

    def ModifyData(self):
        self.ui = uic.loadUi("C:\\Users\\san\\Desktop\\D_D\\python_UI\\Non-Identifying\\UI\\ModifyData.ui") #insert your UI path
        self.ui.show()

        inputdata = tab1_input
        columns = len(inputdata.columns)
    
        #열 인덱싱        
        inputType = inputdata.dtypes
        #inputType = inputType.values
        print(inputType)
        print(inputType.shape)
        #print(inputType[[1]])
        
        #print(inputdata.columns[1])
        #print(type(inputdata.columns[1]))

        for i in range(columns):
            #print(inputdata.columns[i])
            
            self.ui.dataTypeChange.setItem(i,0,QTableWidgetItem(str(inputdata.columns[i])))
            self.ui.dataTypeChange.setItem(i,1,QTableWidgetItem(str(inputType[[i]])))

        #데이터 타입 변환 함수 .astype()
        #https://riptutorial.com/ko/pandas/example/10052/dtype-%EB%B3%80%EA%B2%BD%ED%95%98%EA%B8%B0
        
           
#        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImportDataWindow()
    sys.exit(app.exec_())
