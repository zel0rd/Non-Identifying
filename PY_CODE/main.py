#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import sys
import time
import random
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
sys.path.append("./UI") # insert your path
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
        
        self.ui = uic.loadUi("./UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text, TODO: change dynamic text
        self.ui.show()        

        self.ui.INPUTtable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.ui.actionimport_data.triggered.connect(self.ImportData) #importData from csv
        #self.ui.actionimport_data.triggered.connect(self.ImportFileDialog) #import_data in menuBar, call read data from file
        self.ui.actionsave_data.triggered.connect(self.SaveFileDialog) #export_data in menuBar, call save data event
        self.ui.actionEXIT.triggered.connect(self.CloseWindow) #exit in menuBar, call exit event

        #self.ui.actionRun.triggered.connect(self.Missing) # not complete 수정중
        self.ui.actionNonIdentifier.triggered.connect(self.NonIdentifierMethod) # not complete 수정중


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
            global tab2_output
            tab1_input = inputdata #save data in file, 파일에 있는 데이터를 변수에 저장 
            tab2_output = inputdata
            print(tab2_output) #saved data print-> console

            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.INPUTtable.setColumnCount(colnum) #Set Column Count    
            self.ui.INPUTtable.setRowCount(rownum)
            self.ui.INPUTtable.setHorizontalHeaderLabels(list(inputdata.columns))
            self.ui.INPUTtable.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.INPUTtable.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))

            
        
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def ImportData(self):
        self.ui.hide()
        self.newWindow = ImportDataWindow(self)


    def NonIdentifierMethod(self):
        self.newWindow = NonIdentifierMethod(self)

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
        
    def SaveFileDialog(self): #tab2_output convert to csv file and save, TODO: need to edit
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


#importWinows
class ImportDataWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ImportDataWindow, self).__init__(parent)
        self.ui = uic.loadUi("./UI/ImportData.ui") #insert your UI path
        self.ui.show()
        self.ui.toolButton.clicked.connect(self.ImportDataButton)
        self.ui.cancelButton.clicked.connect(self.ui.hide)
      
    def ImportDataButton(self):
        options = QFileDialog.Options()
      #  options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  options=options)
        if fileName:
            inputdata = pd.read_csv(fileName, sep=",",encoding='euc-kr') #read file
            path = os.getcwd() + fileName
            self.ui.filePath.append(path) #show file path
            print(inputdata)

            global tab1_input #need to define again 
            tab1_input = inputdata #save data in file, 파일에 있는 데이터를 변수에 저장 

            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.InputData.setColumnCount(colnum) #Set Column Count    
            self.ui.InputData.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.InputData.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))

            self.ui.nextButton.clicked.connect(self.changeWindow)
        #self.ui.cancelBUtton.clicked.connect(self.ui.hide)
    
    def changeWindow(self):
        self.ui.hide()
        self.modify = ModifyData()
        


class ModifyData(QMainWindow):
    def __init__(self, parent=None):
        super(ModifyData,self).__init__(parent)
        self.ui = uic.loadUi("./UI/ModifyData.ui") #insert your UI path
        self.ui.show()
        
        global tab1_input
        
        HorizontalHeader = ["DA","NAME","SAMPLE","EXPECTED","FORMAT","식별자"]
        
        self.ui.dataTypeChange.setColumnCount(len(HorizontalHeader))
        self.ui.dataTypeChange.setHorizontalHeaderLabels(HorizontalHeader)
        self.ui.dataTypeChange.setRowCount(len(tab1_input.columns))
       
        item = MyQTableWidgetItemCheckBox()
   
        #checkbox
        for i in range(len(tab1_input.columns)):
            item = MyQTableWidgetItemCheckBox()
            self.ui.dataTypeChange.setItem(i, 0, item)
            chbox = MyCheckBox(item)
            self.ui.dataTypeChange.setCellWidget(i, 0, chbox)
            chbox.stateChanged.connect(self.__checkbox_change)  # sender() 확인용 예..
    
        self.ui.dataTypeChange.setColumnWidth(0, 30) # checkbox 컬럼 폭 강제 조절. 
        self.ui.dataTypeChange.cellClicked.connect(self._cellclicked)
        

        #columns name, NAME 컬럼에 값 입력
        for i in range(len(tab1_input.columns)):
            self.ui.dataTypeChange.setItem(i,1,QTableWidgetItem(str(tab1_input.columns[i]))) 


        
        #index 2 and 3
        type_list = []
        for i in range(len(tab1_input.columns)):
            temp1 = tab1_input[tab1_input.columns[i]][2]
            self.ui.dataTypeChange.setItem(i,2, QTableWidgetItem(str(temp1))) #SAMPLE 컬럼에 샘플 값 출력
            #temp2 = str(type(tab1_input[tab1_input.columns[i]][2]))
            temp2 = str(tab1_input[tab1_input.columns[i]].dtype)
            if (temp2 == "object"): # dataframe에서 object == string
                temp2 = "string"
            type_list.append(temp2) # 컬럼별로 데이터타입 리스트에 추가
            self.ui.dataTypeChange.setItem(i,3, QTableWidgetItem(str(temp2))) #EXPECTED 컬럼에 데이터 타입 출력
            
        type_list.append("datetime64[ns]")
        type_list = list(set(type_list))
        type_list = ["SAME"] + type_list
        
        #set combo box item in "FORAMT" column
        for i in range(len(tab1_input.columns)):
            mycom = QComboBox() 
            mycom.addItems(type_list) 
            self.ui.dataTypeChange.setCellWidget(i, 4, mycom)
        

        #set combo box item in 식별자
        id_list = ["식별자","준식별자","민감정보","일반정보"]
        for i in range(len(tab1_input.columns)):
            mycom = QComboBox() 
            mycom.addItems(id_list)
            self.ui.dataTypeChange.setCellWidget(i, 5, mycom)
        
        self.ui.dataTypeChange.resizeColumnsToContents() 
        self.ui.dataTypeChange.resizeRowsToContents() 
        
        self.ui.backButton.clicked.connect(self.BackEvent)
        self.ui.cancelButton.clicked.connect(self.ui.hide)    
        self.ui.finishButton.clicked.connect(self.finish)
        
    def BackEvent(self):
        self.ui.hide()
        self.modify = ImportDataWindow()

    def finish(self):
        #checked columns
        checked_number = [] # checkbox index
        check_columns = []  # 체크된 컬럼들
        for i in range(len(tab1_input.columns)):
            chbox = self.ui.dataTypeChange.cellWidget(i,0) # 0부터 checkbox 값 가져오기
            if isinstance(chbox, MyCheckBox):
                if chbox.isChecked():
                    checked_number.append(i)
                    checkedColumn = self.ui.dataTypeChange.item(i,1).text()
                    check_columns.append(checkedColumn)

        print(checked_number) # just 확인용
        print(check_columns) # just 확인용      
        

        #MainWidget() rendering
        self.ui.hide()  

        self.ui = uic.loadUi("./UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.show()
        
        #tab1의 input table rendering
        rownum = len(tab1_input.index) # get row count
        colnum = len(check_columns)
        self.ui.INPUTtable.setRowCount(rownum) #set row number
        self.ui.INPUTtable.setColumnCount(colnum) #set column number
        self.ui.INPUTtable.setHorizontalHeaderLabels(check_columns)

        for k in range(colnum):
            for l in range(rownum):
                self.ui.INPUTtable.setItem(l,k,QTableWidgetItem(str(tab1_input[check_columns[k]][l])))
                
        self.ui.INPUTtable.resizeColumnsToContents() 
        self.ui.INPUTtable.resizeRowsToContents() 
        """
        #tab1의 data type 테이블 rendering
        self.ui.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for down in range(colnum): #행번호
            mycom = self.ui.dataTypeChange.cellWidget(i,5)
            self.ui.INPUTtable.setItem(down, 0, QTableWidgetItem(str(check_columns[down])))
            self.ui.INPUTtable.setItem(down, 1, QTableWidgetItem(str(tab1_input[check_columns[k]][l])))
            self.ui.INPUTtable.setItem(down, 2, QTableWidgetItem(str(tab1_input[check_columns[k]][l])))"""

        
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
    
                
#nonidentifierMethod window
class NonIdentifierMethod(QMainWindow):
    global tab1_input, tab2_output
    global before, after, SelectColumn, SelectColumnName, rownum, colnum

    def __init__(self, parent=None):
        super(NonIdentifierMethod, self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        self.ui = uic.loadUi("./UI/SelectNonIdentifierMethod.ui") #insert your UI path
        self.ui.show()

        global before, SelectColumn, SelectColumnName, rownum, colnum
        SelectColumn = self.parent().ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.parent().ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name

        before = tab1_input[SelectColumnName].to_frame() #pull one column and convert list
        rownum = len(before.index) # get row count
        colnum = len(before.columns) # get column count

        """if(before[SelectColumnName].dtype == np.int64): # TODO: not int, string
            self.ui.Method5.setCheckable(False)
            self.ui.Method6.setCheckable(False)"""

        self.ui.nextButton.clicked.connect(self.NextButton)
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    #radio button event start 
    def NextButton(self):
        global before, rownum, colnum

        if(self.ui.Method3.isChecked()): # Shuffle UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./UI/Shuffle.ui") #insert your UI path
            self.ui.show()
            
            self.ui.BeforeData.setRowCount(rownum) #Set Column Count s
            self.ui.BeforeData.setColumnCount(colnum) #Set Column Count       
            self.ui.BeforeData.setHorizontalHeaderLabels(list(before.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.BeforeData.setItem(j,i,QTableWidgetItem(str(before[before.columns[i]][j])))

            self.ui.runButton.clicked.connect(self.Shuffle)
            self.ui.finishButton.clicked.connect(self.finishButton)
            self.ui.cancelButton.clicked.connect(self.ui.hide)


        elif(self.ui.Method5.isChecked()): # 라운딩 UI 및 before data 테이블 값 넣기
            self.ui = uic.loadUi("./UI/Rounding.ui") #insert your UI path
            self.ui.show()
            self.ui.randomLabel.hide()
            
            self.ui.BeforeData.setRowCount(rownum) #Set Column Count s
            self.ui.BeforeData.setColumnCount(colnum) #Set Column Count       
            self.ui.BeforeData.setHorizontalHeaderLabels(list(before.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.BeforeData.setItem(j,i,QTableWidgetItem(str(before[before.columns[i]][j])))

            self.ui.runButton.clicked.connect(self.Rounding)
            self.ui.finishButton.clicked.connect(self.finishButton)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            
            #self.ui.backButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
    
    #radio button event end 

    #data shuffle(재배열) start          
    def Shuffle(self):
        number = self.ui.shffleText.toPlainText()
        try:  #숫자만 입력, 그 외 값은 예외처리
            number = int(number)
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

        global before, rownum, colnum, tab2_output, SelectColumn, SelectColumnName, after
        after = before[SelectColumnName].values.tolist()
        
        for i in range(number): #shuffle 
    	    shuffle(after)

        self.ui.AfterData.setRowCount(rownum) #Set Column Count s
        self.ui.AfterData.setColumnCount(colnum) #Set Column Count       
        self.ui.AfterData.setHorizontalHeaderLabels(list(before.columns))
        
        for i in range(rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(after[i])))
    #Shuffle() end

    #data Rounding start
    def Rounding(self):
        global before, rownum, colnum, tab2_output, SelectColumn, SelectColumnName, after
        number = self.ui.roundText.toPlainText()
        try: #숫자만 입력, 그 외 값은 예외처리
            number = int(number)
            if(number<=0):
                print(1 / number)
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number and bigger than 0')
        pass
      
        index = self.ui.comboBox.currentIndex()
        after = before[SelectColumnName].to_frame() 

        if(index == 0):# 올림
            self.ui.randomLabel.hide()
            for i in range(rownum):
                after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+9*pow(10, number-1))//pow(10, number))*pow(10, number) # change number, up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+9*10^n-1)//10^n)*10^n # change number, up
        elif(index == 1):#내림
            self.ui.randomLabel.hide()
            for i in range(rownum):
                after.loc[i, SelectColumnName] = (after.loc[i, SelectColumnName]//pow(10, number))*pow(10, number) # change number, down
                #after.loc[i, SelectColumnName] = (after.loc[i, SelectColumnName]//10^n-1)*10^n # change number, down
        elif(index == 2):#5를 기준으로 up down, 반올림
            self.ui.randomLabel.hide()
            for i in range(rownum):
                after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+5*pow(10, number-1))//pow(10, number))*pow(10, number) # change number, 4down, 5up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+5)//10)*10 # change number, 4down, 5up
        elif(index == 3): #random 값을 기준으로 up down
            randomN = random.randint(0,9)
            self.ui.randomLabel.show() #show random value label
            self.ui.randomLabel.setText("Value: " + str(randomN)) #랜덤 값 보여주기
            for i in range(rownum):
                after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+(10-randomN))//pow(10, number))*pow(10, number) # change number, 4down, 5up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+(10-randomN))//10^n-1)*10^n # change number, 4down, 5up

        self.ui.AfterData.setRowCount(rownum) #Set Column Count
        self.ui.AfterData.setColumnCount(colnum) #Set Column Count       
        self.ui.AfterData.setHorizontalHeaderLabels(list(after.columns))

        for i in range(rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(after[after.columns[0]][i])))
    
    """if(DataFromTable[SelectColumnName].dtype == np.float64):
            DataFromTable[SelectColumnName] = round(DataFromTable[SelectColumnName],1) # change number 4down, 5up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.ceil) # up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.floor) # down""" #float 처리, 지금 비사용        
    #data Rounding end


    #데이터 tab2_output 저장 및 화면 끄기
    def finishButton(self):
        global after, SelectColumnName, tab2_output
        tab2_output[SelectColumnName] = after #change values
        print(tab2_output)
        self.ui.hide()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())
