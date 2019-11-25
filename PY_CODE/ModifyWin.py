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
import seaborn as sns
from datetime import datetime
plt.rc('font', family='Malgun Gothic') #한글 깨짐 방지
plt.rc('axes', unicode_minus=False) #한글 깨짐 방지

#to import UI path
sys.path.append("./UI") # insert your path

sys.path.append("./PY_CODE")
import mplwidget

from PandasModel import PandasModel # for table model setting
#from ImportDataWin import ImportDataWindow
from CheckBox import MyCheckBox
from CheckBox import MyQTableWidgetItemCheckBox 

class ModifyDataWindow(QMainWindow):
    def __init__(self, MainWindow, importWindow,inputdata):
        super().__init__()
        self.ui = uic.loadUi("./UI/ModifyData.ui") #insert your UI path
        self.ui.show()

        self.mainWin = MainWindow
        self.beforewindow = importWindow
        self.inputdata = inputdata.copy()
        
        HorizontalHeader = ["DA","NAME","SAMPLE","EXPECTED","FORMAT","식별자", "결측치비율", "결측치처리"]
        
        self.ui.dataTypeChange.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) #editable false
        self.ui.dataTypeChange.setColumnCount(len(HorizontalHeader))
        self.ui.dataTypeChange.setHorizontalHeaderLabels(HorizontalHeader)
        self.ui.dataTypeChange.setRowCount(len(self.inputdata.columns))

        #checkbox
        for i in range(len(self.inputdata.columns)):
            item = MyQTableWidgetItemCheckBox()
            self.ui.dataTypeChange.setItem(i, 0, item)
            chbox = MyCheckBox(item)
            chbox.setChecked(True)
            self.ui.dataTypeChange.setCellWidget(i, 0, chbox)
            chbox.stateChanged.connect(self.__checkbox_change)  # sender() 확인용 예..
    
        self.ui.dataTypeChange.setColumnWidth(0, 30) # checkbox 컬럼 폭 강제 조절. 
        self.ui.dataTypeChange.cellClicked.connect(self._cellclicked)

        #columns name, NAME 컬럼에 값 입력
        for i in range(len(self.inputdata.columns)):
            self.ui.dataTypeChange.setItem(i,1,QTableWidgetItem(str(self.inputdata.columns[i]))) 

        #index 2 and 3
        type_list = []
        for i in range(len(self.inputdata.columns)):
            temp1 = self.inputdata[self.inputdata.columns[i]][2]
            self.ui.dataTypeChange.setItem(i,2, QTableWidgetItem(str(temp1))) #SAMPLE 컬럼에 샘플 값 출력
            temp2 = str(self.inputdata[self.inputdata.columns[i]].dtype)
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
        for i in range(len(self.inputdata.columns)):
            mycom = QComboBox() 
            mycom.addItems(type_list) 
            self.ui.dataTypeChange.setCellWidget(i, 4, mycom)
        

        #index 5, set combo box item in 식별자
        id_list = ["식별자","준식별자","민감정보","일반정보"]
        for i in range(len(self.inputdata.columns)):
            mycom = QComboBox() 
            mycom.addItems(id_list)
            self.ui.dataTypeChange.setCellWidget(i, 5, mycom)
        
        self.ui.dataTypeChange.resizeColumnsToContents() 
        self.ui.dataTypeChange.resizeRowsToContents() 

        #index 6 and 7, set combo box item in 결측치비율, 결측치처리
        missing_list = ["", "평균","중간값","최빈값","제거"]
        for i in range(len(self.inputdata.columns)):
            df = self.inputdata.isnull().sum(axis = 0)
            index6 = str(df[i]) + "(" + str(
                round((df[i]/len(self.inputdata.index)*100),2)) +"%)"
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
        self.beforewindow.ui.show()

    def finish(self):
        #checked columns
        checked_number = [] # checkbox index
        unchecked_number = [] 
        check_columns = []  # 체크된 컬럼들 = i will import these columns
        combo_id = [] #식별자
        types = [] #data type check
        for i in range(len(self.inputdata.columns)):
            chbox = self.ui.dataTypeChange.cellWidget(i,0) # 0부터 checkbox 값 가져오기
            if isinstance(chbox, MyCheckBox):
                if chbox.isChecked():
                    checked_number.append(i)
                    check_columns.append(self.ui.dataTypeChange.item(i,1).text())
                    combo_id.append(self.ui.dataTypeChange.cellWidget(i,5).currentText()) #식별자 combo box
                    if(self.ui.dataTypeChange.cellWidget(i,4).currentText() == 'SAME'): #같은경우 3 번째 컬럼 값으로 데이터타입 주기
                        #print(self.ui.dataTypeChange.item(i,3).text())
                        types.append(self.ui.dataTypeChange.item(i,3).text())
                    else:#데이터타입 수정한경우 4 번째 있는 컬럼으로 데이터타입 주기
                        types.append(self.ui.dataTypeChange.cellWidget(i,4).currentText())

                    #결측치 처리
                    self.inputdata = self.MissingValueProcess(self.inputdata, i)
                    #print(self.inputdata)
                    
                else:
                    unchecked_number.append(i)
        
        unchecked_number.reverse() # 리스트 거꾸로 넣어서 index error 제거, unchecked column remove
        for i in unchecked_number:
            self.inputdata = self.inputdata.drop(self.inputdata.columns[i], axis=1) #사용자가 선택한 컬럼만 tab1_input에 저장
        

        #print(checked_number) # just 확인용
        #print(check_columns) # just 확인용    
        #print(combo_id) # just 확인용
        #print(types)   # just 확인용

        #checked columns의 식별자 딕셔너리 데이터 생성
        self.mainWin.id_dict.clear()
        self.mainWin.id_dict['식별자'] = []
        self.mainWin.id_dict['준식별자'] = []
        self.mainWin.id_dict['민감정보'] = []
        self.mainWin.id_dict['일반정보'] = []
        for i in checked_number:
            mycom = self.ui.dataTypeChange.cellWidget(i,5)
            #print(mycom.currentText())
            if mycom.currentText() == '식별자':
                self.mainWin.id_dict['식별자'].append(self.ui.dataTypeChange.item(i,1).text())
            elif mycom.currentText() == '준식별자':
                self.mainWin.id_dict['준식별자'].append(self.ui.dataTypeChange.item(i,1).text())
            elif mycom.currentText() == '민감정보':
                self.mainWin.id_dict['민감정보'].append(self.ui.dataTypeChange.item(i,1).text())
            else:
                self.mainWin.id_dict['일반정보'].append(self.ui.dataTypeChange.item(i,1).text())
        
        self.mainWin.setTables(types, combo_id, self.inputdata) #INPUTtable and typeTable of MainWindow rendering
        self.beforewindow.close()
        self.ui.hide()

    """결측치 처리 함수"""
    def MissingValueProcess(self, data, index):
        widget = self.ui.dataTypeChange.cellWidget(index,7)
        if isinstance(widget, QComboBox):               
            if(widget.currentText() == '평균'): #평균으로 채우기
                data[data.columns[index]].fillna(int(data[data.columns[index]].mean()), inplace=True)
                data[data.columns[index]] =data[data.columns[index]].astype(int) 
            elif(widget.currentText() == '중간값'): #중간값으로 채우기
                data[data.columns[index]].fillna(data[data.columns[index]].median(), inplace=True)
            elif(widget.currentText() == '최빈값'): #최빈값으로 채우기
                data[data.columns[index]].fillna(data[data.columns[index]].value_counts().idxmax(), inplace=True)
            elif(widget.currentText() == '제거'): #row 삭제
                data = data.dropna(subset=[data.columns[index]])
            data = data.reset_index(drop=True) #index 재설정
        return data

    def __checkbox_change(self, checkvalue):
        # print("check change... ", checkvalue)
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        print("checkbox sender row = ", chbox.get_row(), "in ModifyWin.py")

    def _cellclicked(self, row, col):
        print("_cellclicked... ", row, col, "in ModifyWin.py")
       
        