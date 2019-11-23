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
import mplwidget
sys.path.append("./PY_CODE")
from PandasModel import PandasModel # for table model setting

global tab1_input # inputtable data from file, 원본 데이터
global tab2_output # 비식별화 결과 tab2_output에 저장
global Final_Output # Run 함수에서 프라이버시 모델 적용을 위해 필요


fileName = ""

class MainWidget(QMainWindow):
    """
    TODO: 
    1. 메인 윈도우에서 데이터타입 바꾸기 구현 필요
    2. 식별자 구분이 잘 안되므로 수정 필요
    3. 비식별화 함수 추가 필요: shuffle, rounding, 통계값, 교환 완성,마스킹, 삭제, 범주화 코딩완료 -> ok
     3-1. 통계값에서 datetime, string 이상치 ??
     3-2. 통계값: 회귀분석 보류, Part(group)은 여러번 적용되도록 수정필요, int형 데이터만 처리 가능
     3-3. 교환에서 외부 파일 import 기능 없음(필요시 코딩) -> 확인
    4. 프라이버시 모델 구현하기(익명성, 다양성, 근접성)  ***근접성 구현 필요***
     4-1. 익명성, 다양성 기능 구현 완료 => 익명성은 한번만 사용하도록 수정 필요
     4-2. 프라이버시 모델 UI 없음 -> 확인
     4-3. 식별자도 그룹화해야하는 것인지? no
    5. 결측치 처리 
     5-1. 처리방법: 평균 중앙값 최빈값 삭제 -> ok
     5-2. 예측값(회귀분석, k-군집분류 등) 보류, 현재 시계열 데이터 처리 불가
     5-3. 데이터 타입별로 처리 필요, 현재 문자열로 mean, median 사용시 버그 발생
    6. run 함수 구현 필요: run 누르면 tab2의 결과창 보여주기 -> OK
    7. compare graph 및 지표 결과 구현 필요
     7-2. 재식별 리스크 그래프 필요 -> ok 
     7-1. 데이터 손실 및 유용성 그래프 필요 -> ok
     7-2. before, after 데이터 상관관계 변화도 나중에 구현 예정
    8. 라디오 버튼 밑에 식별자, 비식별자, 민감정보, 일반정보 보여주기 -> ok
    9. 비식별 적용 함수 테이블에 보여주기 -> ok
     9-1. 현재 비식별화 기법 최대 1개만 적용 가능
    10. MainWindow 계속 보이게 바꾸기 -> ok
    11. 속도 개선
     - Qtablewidget은 custom model 적용이 불가하기 때문에 Qtableview로 수정필요
     - Import 할 때 QtableWidget -> QtableView로 수정 -> ok
     - 분석탭에 INPUTtable, 비식별탭의 INPUTDATAtable, OUTPUTDATAtable -> QtableView로 수정

    기타: 
    - statusbar에 컬럼 및 행 정보 보여주기  -> ok
    - SaveFileDialog 함수 수정 필요(tab2의 output 데이터를 파일로 저장하도록) ->Final_Output or tab2_output으로 저장, ok
    - 사용하는 data type: int, string, datetime **확인 요청**
    - newwindow 사이즈 fix 및 통일 
    - 데이터 타입, 데이터가 없어서 생기는 에러 예외처리 해주기 **은근 많음**
    - NonIdentifierMethod 클래스에 있는 전역변수 self로 바꿔주기 -> ok
    - 몇몇개의 tablewidget NoEditTriggers 설정 필요 (qt designer or 코드로 설정)
    ** 그 외 TODO 추가해주세요. **
    """
    
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text
        self.ui.show()        

        self.InitializingGraphUI() #CorrelationGraph of tab2 초기화 

        self.ui.INPUTtable.clicked.connect(self.viewClicked) # cell 클릭 시 식별자, 준식별자 등 radio button checked 
        self.ui.actionimport_data.triggered.connect(self.ImportData) #importData from csv
        self.ui.actionsave_data.triggered.connect(self.SaveFileDialog) #export_data in menuBar, call save data event
        self.ui.actionEXIT.triggered.connect(self.CloseWindow) #exit in menuBar, call exit event

        self.ui.actionRun.triggered.connect(self.run) # TODO: 6. run 함수 구현 필요
        self.ui.actionNonIdentifier.triggered.connect(self.NonIdentifierMethod) # TODO: 3. 비식별화 함수 추가중

        #식별자 radio button change event
        self.id_dict = {}
        self.ui.ID.clicked.connect(self.radioButtonClicked) #식별자
        self.ui.QD.clicked.connect(self.radioButtonClicked) #준식별자
        self.ui.SA.clicked.connect(self.radioButtonClicked) #민감정보
        self.ui.GI.clicked.connect(self.radioButtonClicked) #일반정보

        #privacy model button event
        self.ui.privacyAdd.clicked.connect(self.PrivacyAdd)
        self.ui.privacyDelete.clicked.connect(self.PrivacyDelete)
        
        #for methodTableWidget
        self.methodCol_List = {}

    def ImportData(self):
        self.newWindow = ImportDataWindow(self)

    def NonIdentifierMethod(self):
        col = self.col
        if col > len(tab1_input.columns)-1 or len(tab1_input.columns) <1 : # if value is null, do nothing
            print('cell has nothing (NonIdentifierMethod)')
        else: #if not null, radio button check
            self.newWindow = NonIdentifierMethod(col)
    
    def viewClicked(self, item): #cell 클릭시 식별자 radio button checked
        self.col = item.column()
        self.row = item.row()

        print("_cellclicked... ", self.row, self.col) #클릭 cell 확인

        if self.col > len(tab1_input.columns)-1 or len(tab1_input.columns) <1: # if value is null, do nothing
            print('Cell is empty')
        else: #if not null, radio button check
            if(self.ui.typeTable.item(self.col,2).text() == '식별자'):
                print("식별자")
                self.ui.ID.setChecked(True)
                self.setTypeListWidget(self.id_dict['식별자'], self.col)
            elif(self.ui.typeTable.item(self.col,2).text() == '준식별자'):
                print("준식별자")
                self.ui.QD.setChecked(True)
                self.setTypeListWidget(self.id_dict['준식별자'], self.col)
            elif(self.ui.typeTable.item(self.col,2).text() == '민감정보'):
                print("민감정보")
                self.ui.SA.setChecked(True)
                self.setTypeListWidget(self.id_dict['민감정보'], self.col)
            elif(self.ui.typeTable.item(self.col,2).text() == '일반정보'):
                print("일반정보")
                self.ui.GI.setChecked(True)
                self.setTypeListWidget(self.id_dict['일반정보'], self.col)

    def setTables(self, types, combo_id):
        global tab1_input
        self.model = PandasModel(tab1_input)
        self.ui.INPUTtable.setModel(self.model)

        rownum = len(tab1_input.index)
        colnum = len(tab1_input.columns)

        #tab1의 data type 테이블 rendering
        self.ui.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for rowindex in range(colnum): #컬럼 개수만큼 행에 값 넣기         
            self.ui.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(tab1_input.columns[rowindex]))) #setitem 컬럼이름 
            self.ui.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(types[rowindex]))) #setitem 데이터타입 입력
            self.ui.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)
        
        self.ui.statusbar.showMessage("Imported Data Column: " + str(colnum) + ", Row: " + str(rownum)) #statusbar text, TODO: 기타. change dynamic text

        """rownum = len(tab1_input.index) # get row count
        colnum = len(tab1_input.columns)
        self.ui.INPUTtable.setRowCount(rownum) #set row number
        self.ui.INPUTtable.setColumnCount(colnum) #set column number
        self.ui.INPUTtable.setHorizontalHeaderLabels(tab1_input.columns.tolist())

        for k in range(colnum):
            for l in range(rownum):
                self.ui.INPUTtable.setItem(l,k,QTableWidgetItem(str(tab1_input[tab1_input.columns[k]][l])))
                
        self.ui.INPUTtable.resizeColumnsToContents() 
        self.ui.INPUTtable.resizeRowsToContents() 
        
        #tab1의 data type 테이블 rendering
        self.ui.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for rowindex in range(colnum): #컬럼 개수만큼 행에 값 넣기         
            self.ui.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(tab1_input.columns[rowindex]))) #setitem 컬럼이름 
            self.ui.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(types[rowindex]))) #setitem 데이터타입 입력
            self.ui.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)
        
        self.ui.statusbar.showMessage("Imported Data Column: " + str(colnum) + ", Row: " + str(rownum)) #statusbar text, TODO: 기타. change dynamic text
        """


    def radioButtonClicked(self):
        col = self.col
        if self.col > len(tab1_input.columns)-1 or len(tab1_input.columns) <1: # if value is null, do nothing
            print('cell has nothing(radioButtonClicked)')
        else: #if not null, radio button check
            self.removeDictionaryValue(col)
            if self.ui.ID.isChecked(): #식별자
                self.id_dict['식별자'].append(tab1_input.columns[col])
                self.setTypeListWidget(self.id_dict['식별자'], col)
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("식별자")))
                print("changed to 식별자")
            elif self.ui.QD.isChecked(): #준식별자
                self.id_dict['준식별자'].append(tab1_input.columns[col]) 
                self.setTypeListWidget(self.id_dict['준식별자'], col)           
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("준식별자")))
                print("changed to 준식별자")
            elif self.ui.SA.isChecked(): #민감정보
                self.id_dict['민감정보'].append(tab1_input.columns[col])
                self.setTypeListWidget(self.id_dict['민감정보'], col)
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("민감정보")))
                print("changed to 민감정보")
            elif self.ui.GI.isChecked(): #일반정보
                self.id_dict['일반정보'].append(tab1_input.columns[col])
                self.setTypeListWidget(self.id_dict['일반정보'], col)
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("일반정보")))
                print("changed to 일반정보")
                
    def removeDictionaryValue(self, col):
        old_id = self.ui.typeTable.item(col,2).text() 
        self.id_dict[old_id].remove(tab1_input.columns[col])

    def setTypeListWidget(self, data, col): #radio button과 같은 속성만 보여주기
        self.ui.typeListWidget.clear()
        for i in data:
            self.ui.typeListWidget.addItem(i)

    def PrivacyAdd(self): #add 버튼 누르면 프라이버시 모델 설정 가능
        self.ui.privacyTable.insertRow(self.ui.privacyTable.rowCount())
        privacy_list = ["K", "L", "T"]
        self.privacycom = QComboBox() 
        self.privacycom.addItems(privacy_list)
        self.ui.privacyTable.setCellWidget(self.ui.privacyTable.rowCount()-1, 0, self.privacycom)
        self.privacycom.currentIndexChanged.connect(self.updatePrivacyModelTable)

    def updatePrivacyModelTable(self): # setting privacyTable, L이나 T 모델에서 컬럼 선택하도록하기
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
        global tab1_input, tab2_output, Final_Output

        Final_Output = tab2_output.copy() #비식별화만 된 데이트를 프라이버시 모델에 입력

        #프라이버시 모델 적용
        for r in range(self.ui.privacyTable.rowCount()):
            widget = self.ui.privacyTable.cellWidget(r, 0)
            if isinstance(widget, QComboBox):
                current_value = widget.currentText()
                if(current_value == 'K'):
                    number = self.ui.privacyTable.item(r, 1).text()
                    Final_Output = self.K_anonymity(Final_Output, int(number))
                elif(current_value == 'L'):
                    number = self.ui.privacyTable.item(r, 1).text()
                    columnName = self.ui.privacyTable.cellWidget(r, 2).currentText()
                    Final_Output = self.L_diversity(Final_Output, number, columnName)
                elif(current_value == 'T'):
                    print(self.ui.privacyTable.item(r, 1).text())
        
        #tab2의 before table setItem
        BeforeDataModel = PandasModel(tab1_input)
        self.ui.INPUTDATAtable.setModel(BeforeDataModel)
        """colnum = len(tab1_input.columns) # get column count
        rownum = len(tab1_input.index) # get row count
        self.ui.INPUTDATAtable.setColumnCount(colnum) #Set Column Count
        self.ui.INPUTDATAtable.setRowCount(rownum) #Set Column Count     
        self.ui.INPUTDATAtable.setHorizontalHeaderLabels(tab1_input.columns.tolist())

        for i in range(colnum):
            for j in range(rownum): #rendering data (inputtable of Tab2)
                self.ui.INPUTDATAtable.setItem(j,i,QTableWidgetItem(str(tab1_input[tab1_input.columns[i]][j])))"""
        
        AfterDataModel = PandasModel(Final_Output)
        self.ui.OUTPUTDATAtable.setModel(AfterDataModel)
        """colnum = len(Final_Output.columns) # get column count
        rownum = len(Final_Output.index) # get row count
        self.ui.OUTPUTDATAtable.setColumnCount(colnum) #Set Column Count  
        self.ui.OUTPUTDATAtable.setRowCount(rownum) #Set Column Count     
        self.ui.OUTPUTDATAtable.setHorizontalHeaderLabels(Final_Output.columns.tolist())

        for i in range(colnum):
            for j in range(rownum): #rendering data (outputtable of Tab2)
                self.ui.OUTPUTDATAtable.setItem(j,i,QTableWidgetItem(str(Final_Output[Final_Output.columns[i]][j])))"""
        
        self.setGraph()
        self.ui.tabWidget.setCurrentIndex(1) #탭 전환


    def InitializingGraphUI(self):
        self.before, _ = plt.subplots(figsize=(5,5)) #original code: self.before, self.ax1
        self.before_canvas = FigureCanvas(self.before) # figure - canvas 연동
        self.ui.inputGraph1.addWidget(self.before_canvas) #layout에 figure 삽입
        self.before_canvas.draw() 

        self.after, _ = plt.subplots(figsize=(5,5))
        self.after_canvas = FigureCanvas(self.after) # figure - canvas 연동
        self.ui.outputGraph1.addWidget(self.after_canvas) #layout에 figure 삽입
        self.after_canvas.draw() 


    def setGraph(self):
        #set graph
        graphcount = tab1_input.copy()
        self.correlation_beforegraph(len(graphcount.columns), tab1_input)
        self.max = 0
        list = []
        lenth = self.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        graphcount = graphcount.groupby(list).count()
        graphcount = 1 / graphcount
        print(graphcount[graphcount.columns[0]])
        self.risk_beforegraph(self.ui.inputGraph, graphcount[graphcount.columns[0]])
        

        graphcount = Final_Output.copy()
        self.correlation_aftergraph(len(graphcount.columns), graphcount)
        list = []
        lenth = self.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        graphcount = graphcount.groupby(list).count()
        graphcount = 1 / graphcount
        print(graphcount[graphcount.columns[0]])
        self.risk_aftergraph(self.ui.outputGraph, graphcount[graphcount.columns[0]], self.max.max())
        

    def correlation_beforegraph(self, columns, datas):
        self.ui.inputGraph1.removeWidget(self.before_canvas)
        self.before, _ = plt.subplots(figsize=(columns,columns))
        self.before_canvas = FigureCanvas(self.before) # figure - canvas 연동
        self.ui.inputGraph1.addWidget(self.before_canvas) #layout에 figure 삽입
        
        corr = datas.corr()
        colormap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr, cmap=colormap, annot=True, fmt=".2f")

        self.before_canvas.draw() 


    def correlation_aftergraph(self, columns, datas):
        self.ui.outputGraph1.removeWidget(self.after_canvas)
        self.after, _ = plt.subplots(figsize=(columns,columns))
        self.after_canvas = FigureCanvas(self.after) # figure - canvas 연동
        self.ui.outputGraph1.addWidget(self.after_canvas) #layout에 figure 삽입
        
        corr = datas.corr()
        colormap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr, cmap=colormap, annot=True, fmt=".2f")

        self.after_canvas.draw() 


    def risk_beforegraph(self, widget, data):
        """ reference: https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html tab2의 리스크 그래프 그리기"""
        widget.canvas.axes.clear()
        widget.canvas.axes.hist(data)
        widget.canvas.axes.set_title('Risk of Re-Identification')
        self.max, x, _ = widget.canvas.axes.hist(data)
        widget.canvas.draw()
    
    def risk_aftergraph(self, widget, data, max):
        """ reference: https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html tab2의 리스크 그래프 그리기"""
        widget.canvas.axes.clear()
        widget.canvas.axes.hist(data)
        widget.canvas.axes.set_title('Risk of Re-Identification')
        widget.canvas.axes.set_ylim([0, max])
        widget.canvas.draw()


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
        lenth = self.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        dataframe['count'] = dataframe.groupby(list)[list[0]].transform('size')
        dataframe = dataframe.loc[dataframe['count']>=number] #user parameter
        del dataframe['count']
        dataframe = dataframe.reset_index(drop=True)
        print(dataframe)
        return dataframe
    
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
        lenth = self.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        dataframe['count'] = dataframe.groupby(list)[column].transform('nunique') #salary -> 사용자 선택 민감정보
        dataframe = dataframe.loc[dataframe['count']>=number] #2는 사용자로부터 입력받아야되는 숫자
        del dataframe['count']
        dataframe = dataframe.reset_index(drop=True)       
        print(dataframe)
        return dataframe


#TODO: 함수 구현하기
    def T_closeness(self): 
        print("A")
#TODO: 함수 구현하기


    def SaveFileDialog(self):
        global Final_Output, tab2_output
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  "CSV Files(*.csv)",
                                                  options=options)
        if fileName:
            try:
                output = Final_Output.copy()
            except:
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
        self.ui = uic.loadUi("./UI/ImportData.ui") #insert your UI path
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
            #print(inputdata)

            global tab1_input, tab2_output #need to define again 
            tab1_input = inputdata.copy() #save data in file, 파일에 있는 데이터를 변수에 저장 
            tab2_output = inputdata.copy()

            DataModel = PandasModel(tab1_input)
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
        self.modify = ModifyData()


    def cancelButton(self):
        self.ui.hide()
        

class ModifyData(QMainWindow):
    def __init__(self, parent=None):
        super(ModifyData, self).__init__(parent)
        self.ui = uic.loadUi("./UI/ModifyData.ui") #insert your UI path
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
        missing_list = ["", "평균","중간값","최빈값","제거"]
        for i in range(len(tab1_input.columns)):
            df = tab1_input.isnull().sum(axis = 0)
            index6 = str(df[i]) + "(" + str(
                round((df[i]/len(tab1_input.index)*100),2)) +"%)"
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
        unchecked_number = []
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
                        #print(self.ui.dataTypeChange.item(i,3).text())
                        types.append(self.ui.dataTypeChange.item(i,3).text())
                    else:#데이터타입 수정한경우 4 번째 있는 컬럼으로 데이터타입 주기
                        types.append(self.ui.dataTypeChange.cellWidget(i,4).currentText())

                    #결측치 처리
                    tab1_input = self.MissingValueProcess(tab1_input, i)
                    #print(tab1_input)
                    
                else:
                    unchecked_number.append(i)
        
        unchecked_number.reverse() # 리스트 거꾸로 넣어서 index error 제거, unchecked column remove
        for i in unchecked_number:
            tab1_input = tab1_input.drop(tab1_input.columns[i], axis=1) #사용자가 선택한 컬럼만 tab1_input에 저장
        
        tab2_output = tab1_input.copy()
        print(tab2_output)

        #print(checked_number) # just 확인용
        #print(check_columns) # just 확인용    
        #print(combo_id) # just 확인용
        #print(types)   # just 확인용

        #checked columns의 식별자 딕셔너리 데이터 생성
        ex.id_dict.clear()
        ex.id_dict['식별자'] = []
        ex.id_dict['준식별자'] = []
        ex.id_dict['민감정보'] = []
        ex.id_dict['일반정보'] = []
        for i in checked_number:
            mycom = self.ui.dataTypeChange.cellWidget(i,5)
            #print(mycom.currentText())
            if mycom.currentText() == '식별자':
                ex.id_dict['식별자'].append(self.ui.dataTypeChange.item(i,1).text())
            elif mycom.currentText() == '준식별자':
                ex.id_dict['준식별자'].append(self.ui.dataTypeChange.item(i,1).text())
            elif mycom.currentText() == '민감정보':
                ex.id_dict['민감정보'].append(self.ui.dataTypeChange.item(i,1).text())
            else:
                ex.id_dict['일반정보'].append(self.ui.dataTypeChange.item(i,1).text())
        
        ex.setTables(types, combo_id) #INPUTtable and typeTable of MainWindow rendering
        """self.mainUI = ex.ui #call main UI variable

        #tab1의 input table rendering
        rownum = len(tab1_input.index) # get row count
        colnum = len(check_columns)
        self.mainUI.INPUTtable.setRowCount(rownum) #set row number
        self.mainUI.INPUTtable.setColumnCount(colnum) #set column number
        self.mainUI.INPUTtable.setHorizontalHeaderLabels(check_columns)

        for k in range(colnum):
            for l in range(rownum):
                self.mainUI.INPUTtable.setItem(l,k,QTableWidgetItem(str(tab1_input[check_columns[k]][l])))
                
        self.mainUI.INPUTtable.resizeColumnsToContents() 
        self.mainUI.INPUTtable.resizeRowsToContents() 
        
        #tab1의 data type 테이블 rendering
        self.mainUI.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for rowindex in range(colnum): #컬럼 개수만큼 행에 값 넣기         
            self.mainUI.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(check_columns[rowindex]))) #setitem 컬럼이름 
            self.mainUI.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(types[rowindex]))) #setitem 데이터타입 입력
            self.mainUI.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)
        """
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

    def __init__(self, col=0, parent=None):
        super(NonIdentifierMethod, self).__init__(parent)
        self.SelectColumn = col
        self.SelectColumnName = tab1_input.columns.values[col]
        self.InitUI()

    def InitUI(self):
        self.ui = uic.loadUi("./UI/SelectNonIdentifierMethod.ui") #insert your UI path
        self.ui.show()

        self.before = tab1_input[tab1_input.columns[self.SelectColumn]].to_frame() #pull one column and convert list
        self.rownum = len(self.before.index) # get row count
        self.colnum = len(self.before.columns) # get column count

        if(ex.ui.typeTable.item(self.SelectColumn, 1).text() != 'int64'): #int64만 수치데이터 method 사용
            self.ui.Method5.setEnabled(False)
            self.ui.Method6.setEnabled(False)

        self.ui.nextButton.clicked.connect(self.NextButton) #비식별화 방식 선택(6개 중 택 1 가능)
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    #radio button event start 
    def NextButton(self):

        if(self.ui.Method1.isChecked()): #Swap UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./UI/Swap.ui") #insert your UI path
            self.ui.show()
            self.ui.ImportButton.hide()

            """유니크 값 추출 후 테이블에 저장"""
            uniqueIndex = self.before[self.SelectColumnName].unique().tolist()
            uniqueIndex.sort()

            self.ui.swapTable.setRowCount(len(uniqueIndex)) 
            self.ui.swapTable.setHorizontalHeaderLabels(['before', 'after'])

            for i in range(len(uniqueIndex)):
                self.ui.swapTable.setItem(i,0,QTableWidgetItem(str(uniqueIndex[i])))

            """선택한 컬럼의 데이터만 보여주기"""
            self.ui.compareTable.setRowCount(self.rownum)
            self.ui.compareTable.setHorizontalHeaderLabels([self.SelectColumnName, self.SelectColumnName])

            for j in range(self.rownum):
                self.ui.compareTable.setItem(j,0,QTableWidgetItem(str(self.before[self.SelectColumnName][j])))

            #self.ui.runButton.clicked.connect(self.Swap)
            self.ui.runButton.clicked.connect(lambda: self.Swap(uniqueIndex))
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("교환"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)

        elif(self.ui.Method2.isChecked()): # Shuffle UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./UI/Shuffle.ui") #insert your UI path
            self.ui.show()

            self.ui.BeforeData.setRowCount(self.rownum) #Set Column Count s    
            self.ui.BeforeData.setHorizontalHeaderLabels(list(self.before.columns))

            #for i in range(colnum):
            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.BeforeData.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Shuffle)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("재배열"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method3.isChecked()):
            self.ui = uic.loadUi("./UI/CategoricalData.ui") #insert your UI path
            self.ui.show()

            self.ui.nextButton.clicked.connect(self.Categorical_next)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method4.isChecked()): # 마스킹 및 삭제
            self.ui = uic.loadUi("./UI/maskingData.ui") #insert your UI path
            self.ui.show()

            self.m_level = self.ui.maskingText.textChanged.connect(self.usedbyMasking)
            self.m_index = self.ui.m_comboBox.currentIndexChanged.connect(self.usedbyMasking)

            self.before = tab1_input[self.SelectColumnName].to_frame() #pull one column and convert list
            rownum = len(self.before.index) # get row count
            colnum = len(self.before.columns) # get column count

            self.ui.nextButton.clicked.connect(self.Masking)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method5.isChecked()): # 통계값 처리 UI 및 박스 그래프 보여주기
            self.ui = uic.loadUi("./UI/Aggregation.ui") #insert your UI path
            self.ui.show()
            self.RemoveFlag = False

            #Rendering before box plot start
            self.beforeFig = plt.Figure()
            self.beforeCanvas = FigureCanvas(self.beforeFig) # figure - canvas 연동
            self.ui.beforePlot.addWidget(self.beforeCanvas) #layout에 figure 삽입
            
            self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
            self.beforeCanvas.draw() 
            self.AggregationbeforeGraph(tab1_input[self.SelectColumnName])
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
            self.ui.AllPart.currentIndexChanged.connect(self.ComboBoxSetting)
            self.ui.columns.currentIndexChanged.connect(self.ColumnComboSetting)

            self.ui.runButton.clicked.connect(self.Outlier)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method6.isChecked()): # 라운딩 UI 및 before data 테이블 값 넣기
            self.ui = uic.loadUi("./UI/Rounding.ui") #insert your UI path
            self.ui.show()
            self.ui.randomLabel.hide()
            
            self.ui.BeforeData.setRowCount(self.rownum) #Set Column Count s 
            self.ui.BeforeData.setHorizontalHeaderLabels(list(self.before.columns))

            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.BeforeData.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Rounding)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("라운딩"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
    #radio button event end 

    def usedbyMasking(self):
        self.m_level = self.ui.maskingText.toPlainText()
        self.m_index = self.ui.m_comboBox.currentIndex()
        try:
            self.m_level = int(self.m_level)
            if(self.m_level<1):
                self.m_level/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

    #data swap start
    def Swap(self, uniqueIndex):      
        """swapTable의 after 값으로 바꾸기"""
        self.after = self.before.copy()
        self.swap_list = []
        for i in range(len(uniqueIndex)):
            self.after.loc[self.after[self.SelectColumnName]==str(uniqueIndex[i]), self.SelectColumnName] = self.ui.swapTable.item(i,1).text()
            self.swap_list.append((str(uniqueIndex[i]) + "->" + self.ui.swapTable.item(i,1).text()))

        for j in range(self.rownum):
            self.ui.compareTable.setItem(j,1,QTableWidgetItem(str(self.after[self.SelectColumnName][j])))
    #data swap end

    #data shuffle(재배열) start          
    def Shuffle(self):
        self.shufflenumber = self.ui.shffleText.toPlainText()
        try:  #숫자만 입력, 그 외 값은 예외처리
            self.shufflenumber = int(self.shufflenumber)
            if(self.shufflenumber<1):
                self.shufflenumber/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

        tempList = self.before[self.before.columns[0]].values.tolist()
        
        for i in range(self.shufflenumber): #shuffle 
    	    shuffle(tempList)

        self.ui.AfterData.setRowCount(self.rownum) #Set Column Count s   
        self.ui.AfterData.setHorizontalHeaderLabels(list(self.before.columns))
        
        for i in range(self.rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(tempList[i])))
        #self.after[self.SelectColumnName] = tempList
        self.after = DataFrame(data={self.SelectColumnName: tempList})
    #Shuffle() end

    def Categorical_next(self):

        if(self.ui.ordering.isChecked()):
            self.ui = uic.loadUi("./UI/ordering_categorical.ui")
            self.ui.show()
        
            self.original_uniq = self.before[self.SelectColumnName].unique()
            self.ui.original.setRowCount(len(self.original_uniq))
            self.ui.original.setHorizontalHeaderLabels(['values'])

            self.ui.categorical.setHorizontalHeaderLabels(['categorical'])
            self.ui.categorical.setRowCount(len(self.original_uniq))

            self.original_uniq = list(self.original_uniq)
            self.original_pop = self.original_uniq.copy()   # type: list
            self.groupEle = []
            self.str_groupEle = []
            self.a = 0

            for v in range(len(self.original_uniq)):
                self.ui.original.setItem(v,0,QTableWidgetItem(str(self.original_uniq[v])))
            
            self.ui.runButton.clicked.connect(self.Ordering_Categorical)
            self.ui.cancelButton.clicked.connect(self.ui.hide)

        elif(self.ui.intervals.isChecked()):
            self.ui = uic.loadUi("./UI/intervals_categorical.ui") #insert your UI path
            self.ui.show()

            self.ui.original.setRowCount(self.rownum) #Set Column Count s 
            self.ui.original.setHorizontalHeaderLabels(['original'])

            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.original.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Intervals_Categorical)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("연속 변수 범주화"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
    
    def Ordering_Categorical(self):
        orderValue = self.ui.orderText.toPlainText()
        UsrChckVal = orderValue.split(',')
        print(UsrChckVal)
        UsrChckVal = [int (i) for i in UsrChckVal] #배열 원소 int형으로 변환


        categoricalNum = len(self.original_pop) - len(UsrChckVal)
        groupEle_tmp = []
        
        try:
            if categoricalNum >= 0:
                for c in range(len(UsrChckVal)):
                    groupEle_tmp.append(self.original_uniq[UsrChckVal[c]-1])
                    self.original_pop.remove(groupEle_tmp[c])

                self.groupEle.append(groupEle_tmp)
                groupEle_tmp = str(groupEle_tmp)
                groupEle_tmp = groupEle_tmp.replace("'","")
                self.str_groupEle.append(groupEle_tmp)
                self.ui.categorical.setItem(self.a, 0, QTableWidgetItem(str(groupEle_tmp)))
                print(len(self.groupEle[self.a]))
                self.a = self.a + 1
            
        except ValueError:
            QtWidgets.QMessageBox.about(self, 'Error','이미 범주화 처리가 된 요소입니다.')
        pass
      
        self.ui.finishButton.clicked.connect(self.Ordering_Categorical_finish)

    def Ordering_Categorical_finish(self):
        self.after = self.before.copy()

        self.o_Categorical = []

        for b in range(self.a):
            for z in range(len(self.groupEle[b])):
                self.after.loc[self.after[self.SelectColumnName]==str((self.groupEle[b][z])), self.SelectColumnName] = str((self.str_groupEle[b]))
                for j in range(len(self.original_uniq)):
                    if self.original_uniq[j] == self.groupEle[b][z]:
                        self.o_Categorical.append(str(self.original_uniq[j]) + "  " + str(self.str_groupEle[b]))
        self.finishButton("순위 변수 범주화")

    def Intervals_Categorical(self):
        self.after = self.before.copy()

        self.i_Categorical = []

        self.ui.categorical.setRowCount(self.rownum) #Set Column Count s 
        self.ui.categorical.setHorizontalHeaderLabels(['categorical'])

        minValue = self.ui.minText.toPlainText()
        maxValue = self.ui.maxText.toPlainText()
        interValue = self.ui.interText.toPlainText()

        try:
            minValue = int(minValue)
            maxValue = int(maxValue)
            interValue = int(interValue)
            if(minValue<1):
                minValue/0
            elif(maxValue<1):
                maxValue/0
            elif(interValue<1):
                interValue/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass
            
        for j in range(self.rownum):
            if self.before[self.before.columns[0]][j] < minValue:
                self.after[self.after.columns[0]][j] = "<" + str(minValue)
                self.i_Categorical.append(str(self.before[self.before.columns[0]][j]) + "  " + str(self.after[self.after.columns[0]][j]))
                self.ui.categorical.setItem(j,0,QTableWidgetItem(str(self.after[self.after.columns[0]][j])))
            elif self.before[self.before.columns[0]][j] > maxValue:
                self.after[self.after.columns[0]][j] = ">" + str(maxValue)
                self.i_Categorical.append(str(self.before[self.before.columns[0]][j]) + "  " + str(self.after[self.after.columns[0]][j]))
                self.ui.categorical.setItem(j,0,QTableWidgetItem(str(self.after[self.after.columns[0]][j])))
            else:
                ii = int((maxValue-minValue)/interValue)
                for i in range(ii):
                    if self.before[self.before.columns[0]][j]-minValue >= i*interValue and self.before[self.before.columns[0]][j]-minValue < (i+1)*interValue:
                        self.after[self.after.columns[0]][j] = "[" + str(minValue+i*interValue) + "," + str(minValue+(i+1)*interValue) + ")"
                        self.i_Categorical.append(str(self.before[self.before.columns[0]][j]) + "  " + str(self.after[self.after.columns[0]][j]))
                        self.ui.categorical.setItem(j,0,QTableWidgetItem(str(self.after[self.after.columns[0]][j])))
             
    def Masking(self):
        self.ui = uic.loadUi("./UI/maskingData_review.ui") #insert your UI path
        self.ui.show()
        self.ui.maskingLevel.setRowCount(self.rownum) #Set Column Count s    
        
        self.after = self.before.copy()

        before_uniq = self.before[self.before.columns[0]].unique()
        
        unique_len = []
        mask = []
        after_uniq = before_uniq.copy()

        for i in before_uniq:
            unique_len.append(len(i)-1)

        for j in range(self.rownum): #rendering data (inputtable of Tab1)
            for u in range(len(before_uniq)):
                if(self.m_index == 0): # * masking
                    if self.m_level > unique_len[u]:
                        t_lev = unique_len[u]+1
                        mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], "*"*t_lev))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                    else:
                        mask.append(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1], "*"*self.m_level))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(self.m_level-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                elif(self.m_index == 1): # 0 masking
                    if self.m_level > unique_len[u]:
                        t_lev = unique_len[u]+1
                        mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], "0"*t_lev))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                    else:
                        mask.append(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1], "0"*self.m_level))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(self.m_level-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                elif(self.m_index == 2): # remove
                    if self.m_level > unique_len[u]:
                        t_lev = unique_len[u]+1
                        mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], " "*t_lev))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                    else:
                        mask.append(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1], " "*self.m_level))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(self.m_level-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
            
            self.ui.maskingLevel.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))
            self.ui.maskingLevel.setItem(j,1,QTableWidgetItem((self.after[self.after.columns[0]][j])))        

        #self.ui.backButton.clicked.connect(self.ui.hide)
        self.ui.finishButton.clicked.connect(lambda: self.finishButton("마스킹"))
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    #data Rounding start
    def Rounding(self):
        number = self.ui.roundText.toPlainText()
        try: #숫자만 입력, 그 외 값은 예외처리
            number = int(number)
            if(number<1):
                number/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number and bigger than 0')
        pass

        self.RoundingLevel = ""
        index = self.ui.comboBox.currentIndex()
        self.after = self.before.copy()

        if(index == 0):# 올림
            self.ui.randomLabel.hide()
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ", 올림"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = ((self.after.loc[i, self.SelectColumnName]+9*pow(10, number-1))//pow(10, number))*pow(10, number) # change number, up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+9*10^n-1)//10^n)*10^n # change number, up
        elif(index == 1):#내림
            self.ui.randomLabel.hide()
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ",내림"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = (self.after.loc[i, self.SelectColumnName]//pow(10, number))*pow(10, number) # change number, down
                #after.loc[i, SelectColumnName] = (after.loc[i, SelectColumnName]//10^n-1)*10^n # change number, down
        elif(index == 2):#5를 기준으로 up down, 반올림
            self.ui.randomLabel.hide()
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ", 반올림"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = ((self.after.loc[i, self.SelectColumnName]+5*pow(10, number-1))//pow(10, number))*pow(10, number) # change number, 4down, 5up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+5)//10)*10 # change number, 4down, 5up
        elif(index == 3): #random 값을 기준으로 up down
            randomN = random.randint(0,9)
            self.ui.randomLabel.show() #show random value label
            self.ui.randomLabel.setText("Value: " + str(randomN)) #랜덤 값 보여주기
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ", 랜덤(" + str(randomN) + ")"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = ((self.after.loc[i, self.SelectColumnName]+(10-randomN))//pow(10, number))*pow(10, number) # change number, 4down, 5up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+(10-randomN))//10^n-1)*10^n # change number, 4down, 5up
            
        #rendering aftetable
        self.ui.AfterData.setRowCount(self.rownum) #Set Column Count     
        self.ui.AfterData.setHorizontalHeaderLabels(list(self.after.columns))

        for i in range(self.rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(self.after[self.after.columns[0]][i])))
    
    """if(DataFromTable[SelectColumnName].dtype == np.float64):
            DataFromTable[SelectColumnName] = round(DataFromTable[SelectColumnName],1) # change number 4down, 5up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.ceil) # up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.floor) # down""" #float 처리, 지금 비사용        
    #data Rounding end

    #통계값 aggregation start
    def Outlier(self):
        self.after = self.before.copy() 
        self.AggregationLevel = ""

        #reference: https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame/31502974#31502974
        q1 = self.after[self.SelectColumnName].quantile(0.25) #calculate q1
        q3 = self.after[self.SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        fence_low  = q1-1.5*iqr 
        fence_high = q3+1.5*iqr

        #change 4분위수
        index = self.ui.AllPart.currentIndex()
        
        normal = self.after.loc[(self.after[self.SelectColumnName] >= fence_low) & (self.after[self.SelectColumnName] <= fence_high)] #select not outlier data(normal data)
        
        if index == 0:
            self.after = self.AllAggregation(self.after) #모든 값을 총계나 평균으로 변경            
            self.AggregationafterGraph(self.after[self.SelectColumnName]) #Rendering after box plot
            self.AggregationLevel = self.AggregationLevel + "ALL(" + str(self.ui.function.currentText()) + ")"
        elif index == 1:
            self.after = self.partAggregation(normal, self.after, fence_low, fence_high)  #이상치 값만 처리
            self.AggregationafterGraph(self.after[self.SelectColumnName]) #Rendering after box plot
            self.AggregationLevel = self.AggregationLevel + "PART(" + str(self.ui.function.currentText()) + ")"
        elif index == 2:
            self.after = tab1_input.copy() 
            self.after = self.partGroupAggregation(self.after)
            base = str(self.ui.columns.currentText())
            self.AggregationafterGraph(self.after.groupby(base)[self.SelectColumnName].apply(list))
            self.AggregationLevel = (self.AggregationLevel + "GROUP(" + 
                                    str(self.ui.function.currentText()) + "), " +
                                    str(self.ui.group.currentText()) +
                                    " of " +
                                    str(self.ui.columns.currentText()))

            

        """ float로 변경될 경우, 반올림 후 int로 재변환"""
        self.after[self.SelectColumnName]=round(self.after[self.SelectColumnName],0)
        self.after[self.SelectColumnName] = self.after[self.SelectColumnName].astype(int)

        if(self.RemoveFlag == True):
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("통계 처리 삭제"))
        else:
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("통계 처리"))
    #통계값 aggregation end

    #aggregation ui에 있는 comboBox에 값 넣기
    def ComboBoxSetting(self, index):
        if index == 0: #한 컬럼만 처리 + 모두 하나의 값으로 통일
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("총합")
            self.ui.function.addItem("평균값")
            self.AggregationbeforeGraph(tab1_input[self.SelectColumnName])
        elif index == 1: #한 컬럼만 처리 + 이상치만 처리
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("평균값")
            self.ui.function.addItem("최대값")
            self.ui.function.addItem("최소값")
            self.ui.function.addItem("중앙값")
            self.ui.function.addItem("최빈값")
            self.ui.function.addItem("삭제")
            self.AggregationbeforeGraph(tab1_input[self.SelectColumnName])
        elif index == 2: #한 컬럼에서 일부만 처리 + 이상치만 처리
            self.ui.function.clear() 
            self.ui.function.addItem("평균값")
            self.ui.function.addItem("중앙값")
            self.ui.function.addItem("최빈값")
            self.ui.function.addItem("삭제")
            
            self.ui.columns.show() #컬럼 이름 넣기(현재 선택한 컬럼 제외)
            self.ui.columns.clear()
            for i in tab1_input.columns:
                if i != self.SelectColumnName:
                    self.ui.columns.addItem(i)

            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            array = tab1_input[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))


    def ColumnComboSetting(self): # 컬럼별(그룹)일 때 group combobox 세팅
        base = str(self.ui.columns.currentText())
        if base:
            self.AggregationbeforeGraph(tab1_input.sort_values([self.SelectColumnName]).groupby(base)[self.SelectColumnName].apply(list))

            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            array = tab1_input[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))


    #모든 값을 총계나 평균으로 변경
    def AllAggregation(self, Outlier):
        self.RemoveFlag = False
        index = self.ui.function.currentIndex() 
        if index == 0: #총합으로 통일
            Outlier[self.SelectColumnName] = Outlier[self.SelectColumnName].sum()
        elif index == 1: #평균으로 통일
            Outlier[self.SelectColumnName] = Outlier[self.SelectColumnName].mean()
        return Outlier

    #이상치 값만 처리
    def partAggregation(self, Normal, Outlier, low, high):
        index = self.ui.function.currentIndex() 
        if index == 0: #MEAN
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].mean()
        elif index == 1: #MAX
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].max()
        elif index == 2: #MIN
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].min()
        elif index == 3: #MEDIAN
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].median()
        elif index == 4: #MODE
            self.RemoveFlag = False
            mode = Normal[self.SelectColumnName].value_counts().idxmax() #최빈값
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = mode
        elif index == 5: #REMOVE
            self.RemoveFlag = True
            b_length = len(Outlier.index)
            Outlier = Outlier.loc[(Outlier[self.SelectColumnName] >= low) & (Outlier[self.SelectColumnName] <= high)]
            self.RemoveRowCount = b_length - len(Outlier.index)
        return Outlier

    #그룹화 후 이상치 값 선별 및 처리
    def partGroupAggregation(self, result):
        groupcol = str(self.ui.columns.currentText()) #그룹 기준 컬럼
        groupvalue = str(self.ui.group.currentText())   #그룹 기준 값

        Outlier = tab1_input[tab1_input[groupcol].isin([groupvalue])]
        
        q1 = Outlier[self.SelectColumnName].quantile(0.25) #calculate q1
        q3 = Outlier[self.SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        low  = q1-1.5*iqr 
        high = q3+1.5*iqr

        list = []
        Normal = Outlier.loc[(Outlier[self.SelectColumnName] >= low) & (Outlier[self.SelectColumnName] <= high)] #select normal data  
        Outlier = Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)]
        for row in Outlier.index: 
            list.append(row)

        index = self.ui.function.currentIndex() 
        if index == 0: #MEAN    
            self.RemoveFlag = False
            for i in range(len(list)):
                result[self.SelectColumnName][list[i]] = Normal[self.SelectColumnName].mean()
        elif index == 1: #MEDIAN
            self.RemoveFlag = False
            for i in range(len(list)):
                result[self.SelectColumnName][list[i]] =  Normal[self.SelectColumnName].median()
        elif index == 2: #MODE
            self.RemoveFlag = False
            for i in range(len(list)):
                mode = Normal[self.SelectColumnName].value_counts().idxmax() #최빈값
                result[self.SelectColumnName][list[i]] =  mode
        elif index == 3: #REMOVE
            self.RemoveFlag = True
            self.RemoveRowCount = len(list)
            for i in range(len(list)):
                result = result.drop(result.index[list[i]])
        return result   

    def AggregationbeforeGraph(self, data):
        self.beforeFig.clear()
        self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
        self.ax1.boxplot(data)
        self.ax1.grid()
        self.beforeCanvas.draw() 

    def AggregationafterGraph(self, data):
        self.afterFig.clear() #canvas clear
        self.ax2 = self.afterFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
        self.ax2.boxplot(data)
        self.ax2.grid()
        self.afterCanvas.draw() 

    #데이터 tab2_output 및 methodTable 저장 및 UI 끄기
    def finishButton(self, methodname):
        global tab2_output, tab1_input

        tab2_output[self.SelectColumnName] = self.after[self.SelectColumnName] #change values
        self.ui.hide()
        
        if(methodname == "통계 처리 삭제"):
            changednumber = self.RemoveRowCount
            tab2_output = tab2_output.dropna(subset=[tab2_output.columns[self.SelectColumn]]) #통계값에서 생기는 null 삭제 작업 필요
            tab2_output = tab2_output.reset_index(drop=True)
        else:
            changednumber = self.calculateCahngeValue(self.before, self.after, self.SelectColumnName)
        
        print(tab2_output)

        #methodTable에 이미 비식별 메소드가 있다면 삭제
        if(self.SelectColumnName in ex.methodCol_List):
            print("this is duplicated check")
            ex.ui.methodTable.removeRow(int(ex.methodCol_List[self.SelectColumnName])) #컬럼이 저장된 행 삭제
            for key, value in ex.methodCol_List.items():
                if value > ex.methodCol_List[self.SelectColumnName]:
                    ex.methodCol_List[key] -= 1
            del ex.methodCol_List[self.SelectColumnName]  #딕셔너리에서 컬럼 삭제


        if(methodname == "교환"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.swap_list, changednumber)
        elif(methodname == "재배열"):
            self.methodTable_Level(self.SelectColumnName, methodname,  ("Suffled " + str(self.shufflenumber)), changednumber)
        elif(methodname == "연속 변수 범주화"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.i_Categorical, changednumber)
        elif(methodname == "순위 변수 범주화"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.o_Categorical, changednumber)
        elif(methodname == "마스킹"): 
            self.methodTable_Level(self.SelectColumnName, methodname, ("level " + str(self.m_level)), changednumber)
        elif(methodname == "통계 처리"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.AggregationLevel, changednumber)
        elif(methodname == "통계 처리 삭제"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.AggregationLevel, changednumber)
        elif (methodname == "라운딩"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.RoundingLevel, changednumber)

        ex.methodCol_List[self.SelectColumnName]  = ex.ui.methodTable.rowCount()-1 #컬럼이 저장된 행 저장  
        print(ex.methodCol_List)


    def methodTable_Level(self, colName, method, level, changeNumber):
        ex.ui.methodTable.insertRow(ex.ui.methodTable.rowCount())
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 0, QTableWidgetItem(str(colName))) #column name
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 1, QTableWidgetItem(str(method))) #비식별 method
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 2, QTableWidgetItem(str(level))) #detail
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 3, QTableWidgetItem(str(changeNumber))) #영향받은 row 수 
 

    def methodTable_Box(self, colName, method, level_list, changeNumber):
        levelcom = QComboBox() 
        levelcom.addItems(level_list)

        ex.ui.methodTable.insertRow(ex.ui.methodTable.rowCount())
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 0, QTableWidgetItem(str(colName))) #column name
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 1, QTableWidgetItem(str(method))) #비식별 method
        ex.ui.methodTable.setCellWidget(ex.ui.methodTable.rowCount()-1, 2, levelcom)
        ex.ui.methodTable.setItem(ex.ui.methodTable.rowCount()-1, 3, QTableWidgetItem(str(changeNumber))) #영향받은 row 수

    def calculateCahngeValue(self, beforedata, afterdata, colname):
        df = beforedata[colname] != afterdata[colname]
        return (df == True).sum()  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())
