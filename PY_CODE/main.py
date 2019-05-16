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
sys.path.append("C:\\Users\\jh\\Desktop\\python\\UI") # insert your path

import mplwidget

global tab1_input # inputtable data in tab1
global tab2_input
#global print_line
global tab2_output
#global new_data_1

fileName = ""

class MatplotlibWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.ui = uic.loadUi("C:\\Users\\jh\\Desktop\\python\\UI\\DeIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text, TODO: change dynamic text
        self.ui.show()        

        self.ui.actionimport_data.triggered.connect(self.ImportFileDialog) #import_data in menuBar, call read data from file
        self.ui.actionsave_data.triggered.connect(self.SaveFileDialog) #export_data in menuBar, call save data event
        self.ui.actionEXIT.triggered.connect(self.CloseWindow) #exit in menuBar, call exit event
        
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        
    def ImportFileDialog(self):     #Get Directory and File -> Load datas
        options = QFileDialog.Options()
      #  options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  options=options)
        if fileName:
            print('input file name is ' + fileName) #show filename -> console
            inputdata = pd.read_csv(fileName, sep=",",encoding='euc-kr') #read file

            global tab1_input #need to define again 
            tab1_input = inputdata #save data in file, 파일에 있는 데이터를 변수에 저장 
            print(tab1_input) #saved data print-> console

            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.INPUTtable.setColumnCount(colnum) #Set Column Count    
            self.ui.INPUTtable.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.INPUTtable.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))
            
            self.ui.statusbar.showMessage(fileName + ', columns: ' + str(colnum) + ', rows: ' + str(rownum)) #statusbar show(file path)
    
    def SaveFileDialog(self): #tab2_output convert to csv file and save
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  "CSV Files(*.csv)",
                                                  options=options)
        if fileName:
            output = DataFrame(tab1_input)
            print(tab1_input)
            output.to_csv(fileName, encoding='ms949', index=False)  
        """
        nowDatetime =  datetime.now().strftime('%Y-%m-%d %H-%M-%S')    
        if(fileName == ""):
            output.to_csv("result_%s.csv" % nowDatetime, encoding='ms949')    
        else:
            output.to_csv(fileName, encoding='ms949')
        """  
            
    def CloseWindow(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                     "QUIT",
                                     "Are you sure want to exit process?",
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
       

                              
        
#        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MatplotlibWidget()
    sys.exit(app.exec_())
