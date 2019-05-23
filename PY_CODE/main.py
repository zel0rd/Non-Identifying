#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets
import numpy
import pandas.api.types as ptypes


from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import time
from datetime import datetime

#to import UI path
import sys 
sys.path.append("./../UI") # insert your path
import mplwidget

#to shuffle data
from random import shuffle

global tab1_input # inputtable data in tab1
global tab2_input
#global print_line
global tab2_output
#global new_data_1

fileName = ""

class MainWidget(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.ui = uic.loadUi("./../UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text, TODO: change dynamic text
        self.ui.show()        

        self.ui.INPUTtable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.ui.actionimport_data.triggered.connect(self.ImportData) #importData from csv
        self.ui.actionsave_data.triggered.connect(self.SaveFileDialog) #export_data in menuBar, call save data event
        self.ui.actionEXIT.triggered.connect(self.CloseWindow) #exit in menuBar, call exit event

        self.ui.actionRun.triggered.connect(self.Missing) # not complete 수정중
        
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        
        
    def ImportData(self):
        self.newWindow = ImportDataWindow(self)

#Jihye' code multiline start, 데이터타입별로 처리하기, 
    #결측치 처리하기, https://rfriend.tistory.com/262 수정필요
    def Missing(self): 
        #1. null 레코드 추출
        global tab1_input
        temp = tab1_input[tab1_input.isnull().any(axis=1) ==True]
        print("\n\n\n\this is null values\n\n\n\n")
        print(temp)
        
        #tab1_input = tab1_input.fillna(tab1_input.mean()) #평균으로 처리
        tab1_input = tab1_input.where(pd.notnull(tab1_input), tab1_input.mean(), axis='columns') #평균으로 처리
        print(tab1_input)
        

    #4분위수 처리, 현재 평균 -> 다른값으로도 바꿀 수 있게 하기 수정필요
    def Outlier(self):
        global tab1_input
        rownum = len(tab1_input.index) # get row count
        SelectColumn = self.ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name

        OutlierData = tab1_input[SelectColumnName].to_frame()
        pd.to_numeric(OutlierData[SelectColumnName]) #TODO: you need to edit this line
        print(OutlierData.dtypes) # check data type
        
        #reference: https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame/31502974#31502974
        q1 = OutlierData[SelectColumnName].quantile(0.25) #calculate q1
        q3 = OutlierData[SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        fence_low  = q1-1.5*iqr 
        fence_high = q3+1.5*iqr

        #change 4분위수
        Outliered = OutlierData.loc[(OutlierData[SelectColumnName] >= fence_low) & (OutlierData[SelectColumnName] <= fence_high)] #select not outlier data
        OutlierData.loc[(OutlierData[SelectColumnName] < fence_low) | (OutlierData[SelectColumnName] > fence_high)] = Outliered[SelectColumnName].mean()

        #이상치 제거
        #OutlierData = OutlierData.loc[(OutlierData[SelectColumnName] > fence_low) & (OutlierData[SelectColumnName] < fence_high)] #select not outlier data
        
        tab1_input[SelectColumnName] = OutlierData[SelectColumnName]#change values

        for i in range(rownum): #rendering values again
            #self.ui.INPUTtable.setItem(i,SelectColumn, QTableWidgetItem(ShuffleData[i]))
            self.ui.INPUTtable.setItem(i,SelectColumn, QTableWidgetItem(str(tab1_input[tab1_input.columns[SelectColumn]][i])))

    #데이터 비식별확기법 수정필요
    def Swap():
        print("a")

    def Aggregation(self): #미완성함수, 수정매우많이필요
        global tab1_input
        rownum = len(tab1_input.index) # get row count
        SelectColumn = self.ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name

        OutlierData = tab1_input[SelectColumnName].to_frame()
        pd.to_numeric(OutlierData[SelectColumnName]) #TODO: you need to edit this line
        print(OutlierData.dtypes) # check data type

        #group by
        # df['column_name'].str.extract('(\d+)').astype(int) # 숫자만 추출하고 데이터 형태 변환

    def Micro_aggregatio():
        print("A")

    def Shuffle(self):
        global tab1_input
        rownum = len(tab1_input.index) # get row count
        #rownum = self.ui.IPUTtable.rowCount()
        SelectColumn = self.ui.INPUTtable.currentColumn()
        SelectColumnName = self.ui.INPUTtable.horizontalHeaderItem(SelectColumn).text()
        print("SelectedIndex is " + str(SelectColumn))
        print("SelectColumnName is ", str(SelectColumnName))
        
        #ShuffleData = self.GetDataFromTable(ShuffleData, SelectColumn, SelectRows) #get datas from selected column
        
        ShuffleData = tab1_input[SelectColumnName].tolist() #pull one column and convert list
        print(ShuffleData) # check shuffed data

        for i in range(3): #TODO: you need to modify this line (get argument from user) 
    	    shuffle(ShuffleData)

        tab1_input[SelectColumnName] = ShuffleData #change values
        
        for i in range(rownum): #rendering values again
            #self.ui.INPUTtable.setItem(i,SelectColumn, QTableWidgetItem(ShuffleData[i]))
            self.ui.INPUTtable.setItem(i,SelectColumn, QTableWidgetItem(str(tab1_input[tab1_input.columns[SelectColumn]][i])))
        
    def Rounding(self):
        global tab1_input
        rownum = len(tab1_input.index) # get row count
        SelectColumn = self.ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name

        DataFromTable = tab1_input[SelectColumnName].to_frame()
        pd.to_numeric(DataFromTable[SelectColumnName]) #TODO: you need to edit this line
        print(DataFromTable.dtypes) # check data type

        #5를 기준으로 up down
        if(DataFromTable[SelectColumnName].dtype == np.float64):
            DataFromTable[SelectColumnName] = round(DataFromTable[SelectColumnName],1) # change number 4down, 5up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.ceil) # up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.floor) # down
        elif(DataFromTable[SelectColumnName].dtype == np.int64):
            for i in range(rownum):
                DataFromTable.loc[i, SelectColumnName] = ((DataFromTable.loc[i, SelectColumnName]+5)//10)*10 # change number, 4down, 5up
            #for i in range(10):
            #    DataFromTable.loc[i, SelectColumnName] = (DataFromTable.loc[i, SelectColumnName]//10)*10 # change number, down
            #for i in range(10):
            #    DataFromTable.loc[i, SelectColumnName] = ((DataFromTable.loc[i, SelectColumnName]+9)//10)*10 # change number, up

        tab1_input[SelectColumnName] = DataFromTable #change values

        for i in range(rownum): #rendering values again
            #self.ui.INPUTtable.setItem(i,SelectColumn, QTableWidgetItem(ShuffleData[i]))
            self.ui.INPUTtable.setItem(i,SelectColumn, QTableWidgetItem(str(tab1_input[tab1_input.columns[SelectColumn]][i])))

    #K-Anonimiyu 수정필요
    def K_anonymity(self):
        list = ['sex', 'age', 'loc']
        df = tab1_input.groupby(list).size().reset_index(name='count')
        df = df.loc[df['count']>1] #change parameter
        del df['count']
        print(df)

    def L_diversity(self): #수정필요
        list = ['sex']
        df = tab1_input.groupby(list).size().reset_index(name='count')
        df = df.loc[df['count']>1] #change parameter
        print(df)

    def T_closeness(self): #수정필요
        print("A")
#Jihye' code multiline finish
        
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

    def CloseWindow(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                     "QUIT",
                                     "Are you sure want to exit process?",
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
       

class ImportDataWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ImportDataWindow, self).__init__(parent)
        self.ui = uic.loadUi("./../UI/ImportData.ui") #insert your UI path
        self.ui.show()
        self.ui.toolButton.clicked.connect(self.ImportDataButton)
        #self.ui.cancelButton.clicked.connect(qApp.quit)  #try to close the window(failed!!!!!!!)
        #self.ui.filePath.showMessage(self.ImportDataButton) #show file path

    def ImportDataButton(self):
        options = QFileDialog.Options()
      #  options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  options=options)
        if fileName:
            inputdata = pd.read_csv(fileName, sep=",",encoding='euc-kr') #read file
            print(inputdata)

            #self.ui.InputPath.showMessage(fileName) #show file path

            global tab1_input #need to define again 
            tab1_input = inputdata #save data in file, 파일에 있는 데이터를 변수에 저장 
            #print(tab1_input) #saved data print-> console

            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.InputData.setColumnCount(colnum) #Set Column Count    
            self.ui.InputData.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.InputData.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))

        self.ui.nextButton.clicked.connect(self.ModifyData)

    def ModifyData(self):
        self.ui = uic.loadUi("./../UI/ModifyData.ui") #insert your UI path
        self.ui.show()

        inputdata = tab1_input
        columns = len(inputdata.columns)
        columnsName = inputdata.columns
        print(columnsName)
        #열 인덱싱        
        inputType = inputdata.dtypes

        for i in range(len(inputdata.columns)):
            self.ui.dataTypeChange.setItem(i,0,QTableWidgetItem(str(inputdata.columns[i])))
            print(inputdata[columnsName[i]])
            if(inputdata[columnsName[i]].dtype == np.int64):
                self.ui.dataTypeChange.setItem(i,1, QTableWidgetItem(str("Integer")))
            elif(inputdata[columnsName[i]].dtype == np.datetime64[ns]):
                self.ui.dataTypeChange.setItem(i,1, QTableWidgetItem(str("date/time")))
            else:
                self.ui.dataTypeChange.setItem(i,1, QTableWidgetItem(str("String")))
                

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())
