#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import sys
import time
import numpy as np
import pandas as pd
import pandas.api.types as ptypes
from pandas import Series, DataFrame
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets


from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

from datetime import datetime

#to import UI path
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
        self.ui.hide()
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
       
class Manager(QMainWindow):
    def __init__(self):
        super(ImportDataWindow, self).__init__(parent)
        self.ui = uic.loadUi("./../UI/ImportData.ui") #insert your UI path
        self.ui.show()
        
        self.ImportDataWindow = ImportDataWindow()
        self.ModifyData = ModifyData()

        self.ImportDataWindow.nextButton.clicked.connect(self.ModifyData.show)
        self.ModifyData.backButton.clicked.connect(self.ImportDataWindow.show)

        self.first.show()


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
            path = os.getcwd() + fileName
            self.ui.filePath.append(path)
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

        self.ui.nextButton.clicked.connect(self.hide)
        
class ModifyData(QMainWindow):
    def __init__(self, parent=None):
        super(ModifyData,self).__init_(parent)
        self.ui = uic.loadUi("./../UI/ModifyData.ui") #insert your UI path
        self.ui.show()
        
        global tab1_input
        
        HorizontalHeader = ["DA","NAME","SAMPLE","EXPECTED","FORMAT","식별자"]
        
        self.ui.dataTypeChange.setColumnCount(len(HorizontalHeader))
        self.ui.dataTypeChange.setHorizontalHeaderLabels(HorizontalHeader)
        self.ui.dataTypeChange.setRowCount(len(tab1_input.columns))

        print(tab1_input.columns)
        print(len(tab1_input.columns))
        
        
        item = MyQTableWidgetItemCheckBox()
   
        #checkbox
        for i in range(len(tab1_input.columns)):
            item = MyQTableWidgetItemCheckBox()
            self.ui.dataTypeChange.setItem(i, 0, item)
            chbox = MyCheckBox(item)
#            chbox.setChecked(True)
            # print(chbox.sizeHint())
            self.ui.dataTypeChange.setCellWidget(i, 0, chbox)
            chbox.stateChanged.connect(self.__checkbox_change)  # sender() 확인용 예..
    

        self.ui.dataTypeChange.setColumnWidth(0, 30) # checkbox 컬럼 폭 강제 조절. 
        self.ui.dataTypeChange.cellClicked.connect(self._cellclicked)
        

        #columns name
        for i in range(len(tab1_input.columns)):
            self.ui.dataTypeChange.setItem(i,1,QTableWidgetItem(str(tab1_input.columns[i])))


        #type_list = ["same","int","string"]
        type_list = []
        
        for i in range(len(tab1_input.columns)):
#            print(tab1_input[tab1_input.columns[i]][2])
            temp1 = tab1_input[tab1_input.columns[i]][2]
            self.ui.dataTypeChange.setItem(i,2, QTableWidgetItem(str(temp1)))
#            print(type(tab1_input[tab1_input.columns[i]][2]))
            temp2 = str(type(tab1_input[tab1_input.columns[i]][2]))
            self.ui.dataTypeChange.setItem(i,3, QTableWidgetItem(str(temp2)))
            type_list.append(str(type(tab1_input[tab1_input.columns[i]][2])))
            
        type_list.append("datetime64[ns]", "string", "int64")
        type_list = list(set(type_list))
        type_list = ["SAME"] + type_list
        
         #combo box
        for i in range(len(tab1_input.columns)):
            mycom = QComboBox() 
            mycom.addItems(type_list) 
            #mycom.addItem("") 
            self.ui.dataTypeChange.setCellWidget(i, 4, mycom)
        
        id_list = ["식별자","준식별자","민감정보","일반정보"]
        
       #식별자
        for i in range(len(tab1_input.columns)):
            mycom = QComboBox() 
            mycom.addItems(id_list) 
                #mycom.addItem("") 
            self.ui.dataTypeChange.setCellWidget(i, 5, mycom)
        
        
        
        self.ui.dataTypeChange.resizeColumnsToContents() 
        self.ui.dataTypeChange.resizeRowsToContents() 
        
        self.ui.backButton.clicked.connect(self.hide)

        
        
        
        
#        self.ui.backButton.clicked.connect(self.Modify_hide)
        self.ui.finishButton.clicked.connect(self.finish)
        
#    def Modify_hide(self):
#        time.sleep(1)
#        print("close")
#        self.ui.hide()
#        time.sleep(3)
#        print("open")
#        self.ImportDataWindow()
#        
    def finish(self):
        
        #checked columns
        checked_number = [] # checkbox index
        check_columns = []  # 체크된 컬럼들
        combo_id = []
        types = []
        for i in range(len(tab1_input.columns)):
            chbox = self.ui.dataTypeChange.cellWidget(i,0)
            if isinstance(chbox, MyCheckBox):
                if chbox.isChecked():
#                    print("It is checked : " + str(i))
                    checked_number.append(i)
                    checkedColumn = self.ui.dataTypeChange.item(i,1).text()
                    check_columns.append(checkedColumn)
                    combo_id.append(str(self.ui.dataTypeChange.cellWidget(i,5).currentText())) #식별자 combo box
                    if(self.ui.dataTypeChange.cellWidget(i,4).currentText() == 'SAME'):
                        types.append(self.ui.dataTypeChange.itemAt(i,3).text())
                    else:
                        types.append(str(self.ui.dataTypeChange.cellWidget(i,4).currentText()))
                    

        print(checked_number) # just 확인용
        print(check_columns) # just 확인용      
        

        self.ui.hide()  

        self.ui = uic.loadUi("./../UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.show()
        
        
        rownum = len(tab1_input.index) # get row count
        self.ui.INPUTtable.setColumnCount(len(check_columns))
        self.ui.INPUTtable.setHorizontalHeaderLabels(check_columns)

        for k in range(len(check_columns)):
            for l in range(rownum):
                self.ui.INPUTtable.setItem(l,k,QTableWidgetItem(str(tab1_input[check_columns[k]][l])))
                
        self.ui.INPUTtable.resizeColumnsToContents() 
        self.ui.INPUTtable.resizeRowsToContents() 
        
        #tab1의 data type 테이블 rendering
        self.ui.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for rowindex in range(colnum): #행번호            
            self.ui.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(check_columns[rowindex]))) #setitem 컬럼이름 
            self.ui.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)
            self.ui.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(types[rowindex])))
        

        
    def __checkbox_change(self, checkvalue):
        # print("check change... ", checkvalue)
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        print("checkbox sender row = ", chbox.get_row())

    def _cellclicked(self, row, col):
        print("_cellclicked... ", row, col)
        
class MyCheckBox(QCheckBox): 
    def __init__(self, item): 
        """ 
        :param item: QTableWidgetItem instance 
        """ 
        super().__init__() 
        self.item = item 
        self.mycheckvalue = 2 # 0 --> unchecked, 2 --> checked 
        self.stateChanged.connect(self.__checkbox_change) 
        self.stateChanged.connect(self.item.my_setdata) # checked 여부로 정렬을 하기위한 data 저장 
        
    def __checkbox_change(self, checkvalue): 
        # print("myclass...check change... ", checkvalue) 
        self.mycheckvalue = checkvalue 
        print("checkbox row= ", self.get_row()) 
        
    def get_row(self): 
        return self.item.row()
    
class MyQTableWidgetItemCheckBox(QTableWidgetItem): 
    """ checkbox widget 과 같은 cell 에 item 으로 들어감. checkbox 값 변화에 따라, 사용자정의 data를 기준으로 정렬 기능 구현함. """ 
    def __init__(self): 
        super().__init__() 
        self.setData(Qt.UserRole, 0) 
        
    def __lt__(self, other): 
        # print(type(self.data(Qt.UserRole))) 
        return self.data(Qt.UserRole) < other.data(Qt.UserRole) 
    
    def my_setdata(self, value): 
        # print("my setdata ", value) 
        self.setData(Qt.UserRole, value) 
        # print("row ", self.row())

    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())
