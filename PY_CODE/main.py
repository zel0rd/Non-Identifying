#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import sys
import time
import random #to shuffle data and random value
from random import shuffle
import numpy as np
import pandas as pd
import pandas.api.types as ptypes
from pandas import Series, DataFrame
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets

# for box or other graphs
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar,
                                                FigureCanvasQTAgg as FigureCanvas)

import matplotlib.pyplot as plt
from datetime import datetime

#to import UI path
sys.path.append("./../UI") # insert your path
import mplwidget


global tab1_input # inputtable data from file, 원본 데이터
global tab2_output ##비식별화 결과 tab2_output에 저장
global Final_Output


fileName = ""

class MainWidget(QMainWindow):
    """
    TODO: 
    1. 메인 윈도우에서 데이터타입 바꾸기 구현 필요
    2. 식별자 구분이 잘 안되므로 수정 필요
    3. 비식별화 함수 추가 필요: shuffle, rounding, 통계값, 교환 완성 // 마스킹 삭제 범주화 코딩중
     3-1. 통계값에서 datetime, string 이상치 ??
     3-2. 통계값: 회귀분석 보류, Part(group)은 여러번 적용되도록 수정필요, int형 데이터만 처리 가능
     3-3. 교환에서 외부 파일 import 기능 없음(필요시 코딩)
    4. 프라이버시 모델 구현하기(익명성, 다양성, 근접성)  ***근접성 구현 필요***
     4-1. 익명성, 다양성 기능 구현 완료 => 익명성은 한번만 사용하도록 수정 필요
     4-2. 프라이버시 모델 UI 없음
     4-3. 식별자도 그룹화해야하는 것인지??
    5. 결측치 처리 (처리방법: 평균 중앙값 최빈값 삭제)
     5-1. 예측값(회귀분석, k-군집분류 등) 보류, 현재 시계열 데이터 처리 불가
     5-2. 데이터 타입별로 처리 필요, 현재 문자열로 mean, median 사용시 버그 발생
    6. run 함수 구현 필요: run 누르면 tab2의 결과창 보여주기 -> OK
    7. compare graph 및 지표 결과 구현 필요

    기타: 
    - statusbar에 컬럼 및 행 정보 보여주기  
    - SaveFileDialog 함수 수정 필요(tab2의 output 데이터를 파일로 저장하도록)
    - 사용하는 data type: int, string, datetime
    - newwindow 사이즈 fix
    - tab1의 data classification 구현 or 다른 기능으로 수정 
    - 예외처리 필요한 부분 찾아서 처리해주기;;
    ** 그 외 TODO 추가해주세요. **
    """
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./../UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text, TODO: 기타. change dynamic text
        self.ui.show()        

        self.ui.INPUTtable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) #editable false
        self.ui.INPUTtable.cellClicked.connect(self._cellclicked) # cell 클릭 시 식별자, 준식별자 등 radio button checked 
        self.ui.actionimport_data.triggered.connect(self.ImportData) #importData from csv
        self.ui.actionsave_data.triggered.connect(self.SaveFileDialog) #export_data in menuBar, call save data event
        self.ui.actionEXIT.triggered.connect(self.CloseWindow) #exit in menuBar, call exit event

        self.ui.actionRun.triggered.connect(self.run) # TODO: 6. run 함수 구현 필요
        self.ui.actionNonIdentifier.triggered.connect(self.NonIdentifierMethod) # TODO: 3. 비식별화 함수 추가중

        #식별자 radio button change event
        self.ui.ID.clicked.connect(self.radioButtonClicked) #식별자
        self.ui.QD.clicked.connect(self.radioButtonClicked) #준식별자
        self.ui.SA.clicked.connect(self.radioButtonClicked) #민감정보
        self.ui.GI.clicked.connect(self.radioButtonClicked) #일반정보

        #privacy model button event
        self.ui.privacyAdd.clicked.connect(self.PrivacyAdd)
        self.ui.privacyDelete.clicked.connect(self.PrivacyDelete)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def ImportData(self):
        self.ui.hide()
        self.newWindow = ImportDataWindow(self)

    def NonIdentifierMethod(self):
        col = self.ui.INPUTtable.currentColumn() #get Selected Column number
        if self.ui.INPUTtable.item(col,0) is None: # if value is null, do nothing
            print('cell has nothing (NonIdentifierMethod)')
        else: #if not null, radio button check
            self.newWindow = NonIdentifierMethod(self)
    
    def _cellclicked(self, row, col): #cell 클릭시 식별자 radio button checked
        print("_cellclicked... ", row, col) #클릭 cell 확인

        if self.ui.INPUTtable.item(col,0) is None: # if value is null, do nothing
            print('Cell is empty')
        else: #if not null, radio button check
            if(self.ui.typeTable.item(col,2).text() == '식별자'):
                print("식별자")
                self.ui.ID.setChecked(True)
            elif(self.ui.typeTable.item(col,2).text() == '준식별자'):
                print("준식별자")
                self.ui.QD.setChecked(True)
            elif(self.ui.typeTable.item(col,2).text() == '민감정보'):
                print("민감정보")
                self.ui.SA.setChecked(True)
            elif(self.ui.typeTable.item(col,2).text() == '일반정보'):
                print("일반정보")
                self.ui.GI.setChecked(True)

    def radioButtonClicked(self):
        col = self.ui.INPUTtable.currentColumn() #get Selected Column number
        if self.ui.INPUTtable.item(col,0) is None: # if value is null, do nothing
            print('cell has nothing(radioButtonClicked)')
        else: #if not null, radio button check
            if self.ui.ID.isChecked(): #식별자
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("식별자")))
                print("changed to 식별자")
            elif self.ui.QD.isChecked(): #준식별자
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("준식별자")))
                print("changed to 준식별자")
            elif self.ui.SA.isChecked(): #민감정보
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("민감정보")))
                print("changed to 민감정보")
            elif self.ui.GI.isChecked(): #일반정보
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("일반정보")))
                print("changed to 일반정보")

    def PrivacyAdd(self): #add 버튼 누르면 프라이버시 모델 설정 가능
        self.ui.privacyTable.insertRow(self.ui.privacyTable.rowCount())
        privacy_list = ["K", "L", "T"]
        self.privacycom = QComboBox() 
        self.privacycom.addItems(privacy_list)
        self.ui.privacyTable.setCellWidget(self.ui.privacyTable.rowCount()-1, 0, self.privacycom)
        self.privacycom.currentIndexChanged.connect(self.updatePrivacyModelTable)

    def updatePrivacyModelTable(self): # setting privacyTable
        combobox = self.sender()
        ix = self.ui.privacyTable.indexAt(combobox.pos())
        if self.privacycom.currentIndex() == 1:
            self.IDcom = QComboBox()
            ID_list = []
            if self.ui.typeTable.item(0,0) is None:
                print("typeTable is none")
            else:
                for i in range(self.ui.typeTable.rowCount()):
                    if(self.ui.typeTable.item(i, 2).text() == "민감정보"):
                        ID_list.append(self.ui.typeTable.item(i, 0).text())
                self.IDcom.addItems(ID_list) 
            self.ui.privacyTable.setCellWidget(ix.row(), 2, self.IDcom)
        else:
            self.ui.privacyTable.removeCellWidget(ix.row(),2)
            
    def PrivacyDelete(self):
        self.ui.privacyTable.removeRow(self.ui.privacyTable.currentRow())

    def run(self):
        #익명성 설정 시 함수 호출하도록하기
        global tab2_output, Final_Output
        Final_Output = tab2_output.copy() #비식별화만 된 데이트를 프라이버시 모델에 입력

        #프라이버시 모델 적용
        for r in range(self.ui.privacyTable.rowCount()):
            widget = self.ui.privacyTable.cellWidget(r, 0)
            if isinstance(widget, QComboBox):
                current_value = widget.currentText()
                if(current_value == 'K'):
                    number = self.ui.privacyTable.item(r, 1).text()
                    self.K_anonymity(Final_Output, int(number))
                elif(current_value == 'L'):
                    number = self.ui.privacyTable.item(r, 1).text()
                    columnName = self.ui.privacyTable.cellWidget(r, 2).currentText()
                    self.L_diversity(Final_Output, number, columnName)
                elif(current_value == 'T'):
                    print(self.ui.privacyTable.item(r, 1).text())
        
        #tab2의 tables setItem
        colnum = len(Final_Output.columns) # get column count
        rownum = len(Final_Output.index) # get row count
        self.ui.INPUTDATAtable.setColumnCount(colnum) #Set Column Count
        self.ui.INPUTDATAtable.setColumnRow(rownum) #Set Column Count     
        self.ui.INPUTDATAtable.setHorizontalHeaderLabels(list(Final_Output.columns))
        self.ui.OUTPUTDATAtable.setColumnCount(colnum) #Set Column Count  
        self.ui.OUTPUTDATAtable.setColumnRow(rownum) #Set Column Count     
        self.ui.OUTPUTDATAtable.setHorizontalHeaderLabels(list(Final_Output.columns))  

        for i in range(colnum):
            for j in range(rownum): #rendering data (inputtable of Tab1)
                self.ui.INPUTDATAtable.setItem(j,i,QTableWidgetItem(str(Final_Output[Final_Output.columns[i]][j])))
                self.ui.OUTPUTDATAtable.setItem(j,i,QTableWidgetItem(str(Final_Output[Final_Output.columns[i]][j])))
        
        self.ui.tabWidget.setCurrentIndex(1) #탭 전환
        
    #K-Anonimity
    def K_anonymity(self, dataframe, number):
        """준식별자를 기준으로 그룹화해서 동일 레코드 수 계산 ->
        count 컬럼에 저장 -> count>=n 인 값만 추출 -> count 컬럼 delete  """
        try:
            number = int(number)
        except NameError:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass
        list = []
        lenth = self.ui.typeTable.columnCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        dataframe['count'] = dataframe.groupby(list)[list[0]].transform('size')
        dataframe = dataframe.loc[dataframe['count']>=number] #user parameter
        del dataframe['count']
        print(dataframe)
    
    #L_diversity
    def L_diversity(self, dataframe, number, column): 
        """준식별자를 기준으로 그룹화해서 동일 레코드 수에 대한 유니크 값 계산 ->
        count 컬럼에 저장 -> count>=n 인 값만 추출 -> count 컬럼 delete  """
        try:
            number = int(number)
        except NameError:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

        list = []
        lenth = self.ui.typeTable.columnCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        dataframe['count'] = dataframe.groupby(list)[column].transform('nunique') #salary -> 사용자 선택 민감정보
        dataframe = dataframe.loc[dataframe['count']>=number] #2는 사용자로부터 입력받아야되는 숫자
        del dataframe['count']
        print(dataframe)


#TODO: 함수 구현하기
    def T_closeness(self): 
        print("A")
#TODO: 함수 구현하기


    def SaveFileDialog(self): #TODO: 기타. 함수 수정 필요, tab2_output.copy() 수정하기
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  "CSV Files(*.csv)",
                                                  options=options)
        if fileName:
            output = tab2_output.copy()
            print(output)
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
        self.ui = uic.loadUi("./../UI/ImportData.ui") #insert your UI path
        self.ui.show()

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
            inputdata = pd.read_csv(fileName, sep=",",encoding='euc-kr') #read file
            path = os.getcwd() + fileName
            self.ui.filePath.append(path) #show file path
            print(inputdata)

            global tab1_input, tab2_output #need to define again 
            tab1_input = inputdata.copy() #save data in file, 파일에 있는 데이터를 변수에 저장 
            tab2_output = inputdata.copy()

            rownum = len(inputdata.index) # get row count
            colnum = len(inputdata.columns) # get column count
            self.ui.InputData.setColumnCount(colnum) #Set Column Count    
            self.ui.InputData.setHorizontalHeaderLabels(list(inputdata.columns))

            for i in range(colnum):
                for j in range(rownum): #rendering data (inputtable of Tab1)
                    self.ui.InputData.setItem(j,i,QTableWidgetItem(str(inputdata[inputdata.columns[i]][j])))

            self.ui.nextButton.clicked.connect(self.nextButton)

    
    def nextButton(self):
        self.ui.hide()
        self.modify = ModifyData()


    def cancelButton(self):
        self.ui.hide()
        self.mainUI = MainWidget()
        

class ModifyData(QMainWindow):
    def __init__(self, parent=None):
        super(ModifyData, self).__init__(parent)
        self.ui = uic.loadUi("./../UI/ModifyData.ui") #insert your UI path
        self.ui.show()
        
        global tab1_input
        
        HorizontalHeader = ["DA","NAME","SAMPLE","EXPECTED","FORMAT","식별자", "결측치비율", "결측치처리"]
        
        self.ui.dataTypeChange.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) #editable false
        self.ui.dataTypeChange.setColumnCount(len(HorizontalHeader))
        self.ui.dataTypeChange.setHorizontalHeaderLabels(HorizontalHeader)
        self.ui.dataTypeChange.setRowCount(len(tab1_input.columns))
       
        item = MyQTableWidgetItemCheckBox()
   
        #checkbox
        for i in range(len(tab1_input.columns)):
            item = MyQTableWidgetItemCheckBox()
            self.ui.dataTypeChange.setItem(i, 0, item)
            chbox = MyCheckBox(item)
            chbox.setChecked(True)
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
        type_list.append("string")
        type_list.append("int64")
        type_list = list(set(type_list))
        type_list = ["SAME"] + type_list
        
        #index 4, set combo box item in "FORAMT" column
        for i in range(len(tab1_input.columns)):
            mycom = QComboBox() 
            mycom.addItems(type_list) 
            self.ui.dataTypeChange.setCellWidget(i, 4, mycom)
        

        #index 5, set combo box item in 식별자
        id_list = ["식별자","준식별자","민감정보","일반정보"]
        for i in range(len(tab1_input.columns)):
            mycom = QComboBox() 
            mycom.addItems(id_list)
            self.ui.dataTypeChange.setCellWidget(i, 5, mycom)
        
        self.ui.dataTypeChange.resizeColumnsToContents() 
        self.ui.dataTypeChange.resizeRowsToContents() 

        #index 6 and 7, set combo box item in 결측치비율, 결측치처리
        missing_list = ["", "MEAN","MEDIAN","MODE","REMOVE"]
        for i in range(len(tab1_input.columns)):
            df = tab1_input.isnull().sum(axis = 0)
            index6 = str(df[i]) + "(" + str((df[i]/len(tab1_input.index)*100)) +"%)"
            self.ui.dataTypeChange.setItem(i, 6, QTableWidgetItem(str(index6)))
            if(df[i]>0): #결측치가 1개 이상이면 콤보박스 show()
                mycom = QComboBox() 
                mycom.addItems(missing_list)
                self.ui.dataTypeChange.setCellWidget(i, 7, mycom) #set 결측치 처리 combo box 
        
        self.ui.dataTypeChange.resizeColumnsToContents() 
        self.ui.dataTypeChange.resizeRowsToContents() 
        
        self.ui.backButton.clicked.connect(self.BackEvent)
        self.ui.cancelButton.clicked.connect(self.ui.hide)    
        self.ui.finishButton.clicked.connect(self.finish)

        
    def BackEvent(self):
        self.ui.hide()
        self.modify = ImportDataWindow()

    def finish(self):
        global tab1_input, tab2_output
        #checked columns
        checked_number = [] # checkbox index
        uncheced_number = []
        check_columns = []  # 체크된 컬럼들
        combo_id = []
        types = []
        for i in range(len(tab1_input.columns)):
            chbox = self.ui.dataTypeChange.cellWidget(i,0) # 0부터 checkbox 값 가져오기
            if isinstance(chbox, MyCheckBox):
                if chbox.isChecked():
                    checked_number.append(i)
                    check_columns.append(self.ui.dataTypeChange.item(i,1).text())
                    combo_id.append(self.ui.dataTypeChange.cellWidget(i,5).currentText()) #식별자 combo box
                    if(self.ui.dataTypeChange.cellWidget(i,4).currentText() == 'SAME'): #같은경우 3 번째 컬럼 값으로 데이터타입 주기
                        print(self.ui.dataTypeChange.item(i,3).text())
                        types.append(self.ui.dataTypeChange.item(i,3).text())
                    else:#데이터타입 수정한경우 4 번째 있는 컬럼으로 데이터타입 주기
                        types.append(self.ui.dataTypeChange.cellWidget(i,4).currentText())

                    #결측치 처리
                    tab1_input = self.MissingValueProcess(tab1_input, i)
                    print(tab1_input)
                    
                else:
                    uncheced_number.append(i)
        
        uncheced_number.reverse() # 리스트 거꾸로 넣어서 index error 제거, 
        for i in uncheced_number:
            tab1_input = tab1_input.drop(tab1_input.columns[i], axis=1) #사용자가 선택한 컬럼만 tab1_input에 저장
            tab2_output = tab2_output.drop(tab2_output.columns[i], axis=1) 

        #print(checked_number) # just 확인용
        #print(check_columns) # just 확인용    
        #print(combo_id) # just 확인용
        #print(types)   # just 확인용

        self.mainUI = MainWidget() #call main UI class

        #tab1의 input table rendering
        rownum = len(tab1_input.index) # get row count
        colnum = len(check_columns)
        self.mainUI.ui.INPUTtable.setRowCount(rownum) #set row number
        self.mainUI.ui.INPUTtable.setColumnCount(colnum) #set column number
        self.mainUI.ui.INPUTtable.setHorizontalHeaderLabels(check_columns)

        for k in range(colnum):
            for l in range(rownum):
                self.mainUI.ui.INPUTtable.setItem(l,k,QTableWidgetItem(str(tab1_input[check_columns[k]][l])))
                
        self.mainUI.ui.INPUTtable.resizeColumnsToContents() 
        self.mainUI.ui.INPUTtable.resizeRowsToContents() 
        
        #tab1의 data type 테이블 rendering
        self.mainUI.ui.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for rowindex in range(colnum): #컬럼 개수만큼 행에 값 넣기         
            self.mainUI.ui.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(check_columns[rowindex]))) #setitem 컬럼이름 
            self.mainUI.ui.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(types[rowindex]))) #setitem 데이터타입 입력
            self.mainUI.ui.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)

        self.ui.hide()

    """결측치 처리 함수"""
    def MissingValueProcess(self, data, index):
        widget = self.ui.dataTypeChange.cellWidget(index,7)
        if isinstance(widget, QComboBox):               
            if(widget.currentText() == 'MEAN'): #평균으로 채우기
                data[data.columns[index]].fillna(int(data[data.columns[index]].mean()), inplace=True)
                data[data.columns[index]] =data[data.columns[index]].astype(int) 
            elif(widget.currentText() == 'MEDIAN'): #중간값으로 채우기
                data[data.columns[index]].fillna(data[data.columns[index]].median(), inplace=True)
            elif(widget.currentText() == 'MODE'): #최빈값으로 채우기
                data[data.columns[index]].fillna(data[data.columns[index]].value_counts().idxmax(), inplace=True)
            elif(widget.currentText() == 'REMOVE'): #row 삭제
                data = data.dropna(subset=[data.columns[index]])
            data = data.reset_index(drop=True) #index 재설정
        return data

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


#nonidentifierMethod window, 수정중
class NonIdentifierMethod(QMainWindow):
    global tab1_input, tab2_output
    global before, after, SelectColumn, SelectColumnName, rownum, colnum

    def __init__(self, parent=None):
        super(NonIdentifierMethod, self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        self.ui = uic.loadUi("./../UI/SelectNonIdentifierMethod.ui") #insert your UI path
        self.ui.show()

        global before, SelectColumn, SelectColumnName, rownum, colnum
        SelectColumn = self.parent().ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.parent().ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name

        before = tab1_input[tab1_input.columns[SelectColumn]].to_frame() #pull one column and convert list
        rownum = len(before.index) # get row count
        colnum = len(before.columns) # get column count

        if(self.parent().ui.typeTable.item(SelectColumn, 1).text() != 'int64'): #int64만 수치데이터 method 사용
            self.ui.Method5.setEnabled(False)
            self.ui.Method6.setEnabled(False)

        self.ui.nextButton.clicked.connect(self.NextButton) #비식별화 방식 선택(6개 중 택 1 가능)
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    #radio button event start 
    def NextButton(self):
 
        if(self.ui.Method1.isChecked()): #Swap UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./../UI/Swap.ui") #insert your UI path
            self.ui.show()
            self.ui.ImportButton.hide()

            """유니크 값 추출 후 테이블에 저장"""
            self.uniqueIndex = before[SelectColumnName].unique().tolist()
            self.uniqueIndex.sort()

            self.ui.swapTable.setRowCount(len(self.uniqueIndex)) 
            self.ui.swapTable.setHorizontalHeaderLabels(['before', 'after'])

            for i in range(len(self.uniqueIndex)):
                self.ui.swapTable.setItem(i,0,QTableWidgetItem(str(self.uniqueIndex[i])))

            """선택한 컬럼의 데이터만 보여주기"""
            self.ui.compareTable.setRowCount(rownum)
            self.ui.compareTable.setHorizontalHeaderLabels([SelectColumnName, SelectColumnName])

            for j in range(rownum):
                self.ui.compareTable.setItem(j,0,QTableWidgetItem(str(before[before.columns[0]][j])))

            #self.ui.ImportButton.clicked.connect(self.)
            self.ui.runButton.clicked.connect(self.Swap)
            self.ui.finishButton.clicked.connect(self.finishButton)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)


        elif(self.ui.Method2.isChecked()): # Shuffle UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./../UI/Shuffle.ui") #insert your UI path
            self.ui.show()

            self.ui.BeforeData.setColumnCount(colnum) #Set Column Count
            self.ui.BeforeData.setRowCount(rownum) #Set Column Count s    
            self.ui.BeforeData.setHorizontalHeaderLabels(list(before.columns))

            #for i in range(colnum):
            for j in range(rownum): #rendering data (inputtable of Tab1)
                self.ui.BeforeData.setItem(j,0,QTableWidgetItem(str(before[before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Shuffle)
            self.ui.finishButton.clicked.connect(self.finishButton)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)

        elif(self.ui.Method3.isChecked()):
            print("범주화 메소드") #insert ujin's code
        elif(self.ui.Method4.isChecked()):
            print("마스킹 및 삭제") #insert ujin's code

        elif(self.ui.Method5.isChecked()): # 통계값 처리 UI 및 박스 그래프 보여주기
            self.ui = uic.loadUi("./../UI/Aggregation.ui") #insert your UI path
            self.ui.show()
            
            #Rendering before box plot start
            self.beforeFig = plt.Figure()
            self.beforeCanvas = FigureCanvas(self.beforeFig) # figure - canvas 연동
            self.ui.beforePlot.addWidget(self.beforeCanvas) #layout에 figure 삽입
            
            self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
            self.beforeCanvas.draw() 
            self.beforeGraph(tab1_input[tab1_input.columns[SelectColumn]])
            #Rendering before box plot end

            #Rendering after box plot start
            self.afterFig = plt.Figure()
            self.afterCanvas = FigureCanvas(self.afterFig) # figure - canvas 연동
            self.ui.afterPlot.addWidget(self.afterCanvas) #layout에 figure 삽입

            self.ax2 = self.afterFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
            self.afterCanvas.draw() 
            #Rendering after box plot end

            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.AllPart.currentIndexChanged.connect(self.IndexSetting)
            self.ui.columns.currentIndexChanged.connect(self.changeGraphCombobox)

            self.ui.runButton.clicked.connect(self.Outlier)
            self.ui.finishButton.clicked.connect(self.finishButton2)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)

        elif(self.ui.Method6.isChecked()): # 라운딩 UI 및 before data 테이블 값 넣기
            self.ui = uic.loadUi("./../UI/Rounding.ui") #insert your UI path
            self.ui.show()
            self.ui.randomLabel.hide()
            
            self.ui.BeforeData.setColumnCount(colnum) #Set Column Count    
            self.ui.BeforeData.setRowCount(rownum) #Set Column Count s 
            self.ui.BeforeData.setHorizontalHeaderLabels(list(before.columns))

            #for i in range(colnum):
            for j in range(rownum): #rendering data (inputtable of Tab1)
                self.ui.BeforeData.setItem(j,0,QTableWidgetItem(str(before[before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Rounding)
            self.ui.finishButton.clicked.connect(self.finishButton)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)

    #radio button event end 

    #data swap start
    def Swap(self):      
        """swapTable의 after 값으로 바꾸기"""
        global before, after
        after = before.copy()
        for i in range(len(self.uniqueIndex)):
            after.loc[after[SelectColumnName]==str(self.uniqueIndex[i]), SelectColumnName] = self.ui.swapTable.item(i,1).text()

        for j in range(rownum):
            self.ui.compareTable.setItem(j,1,QTableWidgetItem(str(after[after.columns[0]][j])))
    #data swap end

    #data shuffle(재배열) start          
    def Shuffle(self):
        number = self.ui.shffleText.toPlainText()
        try:  #숫자만 입력, 그 외 값은 예외처리
            number = int(number)
            if(number<1):
                number/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

        global before, after
        after = before[before.columns[0]].values.tolist()
        
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
        global before, after
        number = self.ui.roundText.toPlainText()
        try: #숫자만 입력, 그 외 값은 예외처리
            number = int(number)
            if(number<1):
                number/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number and bigger than 0')
        pass
      
        index = self.ui.comboBox.currentIndex()
        after = before.copy()

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

        #rendering aftetable
        self.ui.AfterData.setRowCount(rownum) #Set Column Count     
        self.ui.AfterData.setHorizontalHeaderLabels(list(after.columns))

        for i in range(rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(after[after.columns[0]][i])))
    
    """if(DataFromTable[SelectColumnName].dtype == np.float64):
            DataFromTable[SelectColumnName] = round(DataFromTable[SelectColumnName],1) # change number 4down, 5up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.ceil) # up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.floor) # down""" #float 처리, 지금 비사용        
    #data Rounding end

    #통계값 aggregation start
    def Outlier(self):
        global before, after
        after = before.copy() 

        #reference: https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame/31502974#31502974
        q1 = after[SelectColumnName].quantile(0.25) #calculate q1
        q3 = after[SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        fence_low  = q1-1.5*iqr 
        fence_high = q3+1.5*iqr

        #change 4분위수
        index = self.ui.AllPart.currentIndex()
        
        normal = after.loc[(after[SelectColumnName] >= fence_low) & (after[SelectColumnName] <= fence_high)] #select not outlier data(normal data)
        
        if index == 0:
            after = self.AllAggregation(after) #모든 값을 총계나 평균으로 변경            
            self.afterGraph(after[SelectColumnName]) #Rendering after box plot
        elif index == 1:
            after = self.partAggregation(normal, after, fence_low, fence_high)  #이상치 값만 처리
            self.afterGraph(after[SelectColumnName]) #Rendering after box plot
        elif index == 2:
            after = tab1_input.copy() 
            after = self.partGroupAggregation(after)
            print(after)
            base = str(self.ui.columns.currentText())
            self.afterGraph(after.groupby(base)[SelectColumnName].apply(list))
            

        """ float로 변경될 경우, 반올림 후 int로 재변환"""
        after[SelectColumnName]=round(after[SelectColumnName],0)
        after[SelectColumnName] = after[SelectColumnName].astype(int)
    #통계값 aggregation end

    #aggregation ui에 있는 comboBox에 값 넣기
    def IndexSetting(self, index):
        if index == 0:
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("SUM")
            self.ui.function.addItem("MEAN")
            self.beforeGraph(tab1_input[tab1_input.columns[SelectColumn]])
        elif index == 1: 
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("MEAN")
            self.ui.function.addItem("MAX")
            self.ui.function.addItem("MIN")
            self.ui.function.addItem("MEDIAN")
            self.ui.function.addItem("MODE")
            self.ui.function.addItem("REMOVE")
            self.beforeGraph(tab1_input[tab1_input.columns[SelectColumn]])
        elif index == 2:
            self.ui.function.clear() 
            self.ui.function.addItem("MEAN")
            self.ui.function.addItem("MEDIAN")
            self.ui.function.addItem("MODE")
            self.ui.function.addItem("REMOVE")
            
            self.ui.columns.show() #컬럼 이름 넣기(현재 선택한 컬럼 제외)
            self.ui.columns.clear()
            for i in tab1_input.columns:
                if i != SelectColumnName:
                    self.ui.columns.addItem(i)

            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            array = tab1_input[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))

    def beforeGraph(self, data):
        self.beforeFig.clear()
        self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
        self.ax1.boxplot(data)
        self.ax1.grid()
        self.beforeCanvas.draw() 

    def afterGraph(self, data):
        self.afterFig.clear() #canvas clear
        self.ax2 = self.afterFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
        self.ax2.boxplot(data)
        self.ax2.grid()
        self.afterCanvas.draw() 

    def changeGraphCombobox(self):
        base = str(self.ui.columns.currentText())
        if base:
            self.beforeGraph(tab1_input.sort_values([SelectColumnName]).groupby(base)[SelectColumnName].apply(list))

            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            array = tab1_input[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))

    #모든 값을 총계나 평균으로 변경
    def AllAggregation(self, Outlier):
        global SelectColumnName
        index = self.ui.function.currentIndex() 
        if index == 0: #총합으로 통일
            Outlier[SelectColumnName] = Outlier[SelectColumnName].sum()
        elif index == 1: #평균으로 통일
            Outlier[SelectColumnName] = Outlier[SelectColumnName].mean()
        return Outlier

    #이상치 값만 처리
    def partAggregation(self, Normal, Outlier, low, high):
        global SelectColumnName
        index = self.ui.function.currentIndex() 
        if index == 0: #MEAN
            Outlier.loc[(Outlier[SelectColumnName] < low) | (Outlier[SelectColumnName] > high)] = Normal[SelectColumnName].mean()
        elif index == 1: #MAX
            Outlier.loc[(Outlier[SelectColumnName] < low) | (Outlier[SelectColumnName] > high)] = Normal[SelectColumnName].max()
        elif index == 2: #MIN
            Outlier.loc[(Outlier[SelectColumnName] < low) | (Outlier[SelectColumnName] > high)] = Normal[SelectColumnName].min()
        elif index == 3: #MEDIAN
            Outlier.loc[(Outlier[SelectColumnName] < low) | (Outlier[SelectColumnName] > high)] = Normal[SelectColumnName].median()
        elif index == 4: #MODE
            mode = Normal[SelectColumnName].value_counts().idxmax() #최빈값
            Outlier.loc[(Outlier[SelectColumnName] < low) | (Outlier[SelectColumnName] > high)] = mode
        elif index == 5: #REMOVE
            Outlier = Outlier.loc[(Outlier[SelectColumnName] >= low) & (Outlier[SelectColumnName] <= high)]
        return Outlier

    #그룹화 후 이상치 값 선별 및 처리
    def partGroupAggregation(self, result):
        groupcol = str(self.ui.columns.currentText()) #그룹 기준 컬럼
        groupvalue = str(self.ui.group.currentText())   #그룹 기준 값

        Outlier = tab1_input[tab1_input[groupcol].isin([groupvalue])]
        print(Outlier)
        q1 = Outlier[SelectColumnName].quantile(0.25) #calculate q1
        q3 = Outlier[SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        low  = q1-1.5*iqr 
        high = q3+1.5*iqr

        list = []
        Normal = Outlier.loc[(Outlier[SelectColumnName] >= low) & (Outlier[SelectColumnName] <= high)] #select normal data  
        Outlier = Outlier.loc[(Outlier[SelectColumnName] < low) | (Outlier[SelectColumnName] > high)]
        for row in Outlier.index: 
            list.append(row)

        index = self.ui.function.currentIndex() 
        if index == 0: #MEAN    
            for i in range(len(list)):
                result[SelectColumnName][list[i]] = Normal[SelectColumnName].mean()
        elif index == 1: #MEDIAN
            for i in range(len(list)):
                result[SelectColumnName][list[i]] =  Normal[SelectColumnName].median()
        elif index == 2: #MODE
            for i in range(len(list)):
                mode = Normal[SelectColumnName].value_counts().idxmax() #최빈값
                result[SelectColumnName][list[i]] =  mode
        elif index == 3: #REMOVE
            for i in range(len(list)):
                result = result.drop(result.index[list[i]])
        return result   


    #데이터 tab2_output 저장 및 화면 끄기
    def finishButton(self):
        global after, SelectColumnName, tab2_output, tab1_input
        tab2_output[tab2_output.columns[SelectColumn]] = after #change values
        tab2_output.dropna(inplace=True) #통계값에서 생기는 null 삭제 작업 필요
        print(tab2_output)
        self.ui.hide()

    #통계값에서 part(group) 저장 시 사용
    def finishButton2(self):
        global after, SelectColumnName, tab2_output, tab1_input
        tab2_output[tab2_output.columns[SelectColumn]] = after[SelectColumnName] #change values
        tab2_output.dropna(inplace=True) #통계값에서 생기는 null 삭제 작업 필요
        print(tab2_output)
        self.ui.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())
