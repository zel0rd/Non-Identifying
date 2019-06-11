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
global tab2_output
#global new_data_1

fileName = ""

"""
[범주화]
  - 이항변수화 : '0','1'의 값만 가지는 가변수 만드는 것
  - 이산형화 : 연속형 변수를 2개 이상의 범주를 가지는 변수로 만들어주는 것
      np.digitize(data, bin) ; np.where(condition, factor1, factor2,...)
"""

class MainWidget(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.ui = uic.loadUi("./UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text, TODO: change dynamic text
        self.ui.show()        

        self.ui.INPUTtable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.ui.actionimport_data.triggered.connect(self.ImportData) #importData from csv
        self.ui.actionNonIdentifier.triggered.connect(self.MaskingData) # not complete 수정중
        #self.ui.actionNonIdentifier.triggered.connect(self.CategoricalData)
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def ImportData(self):
        self.ui.hide()
        self.newWindow = ImportDataWindow(self)
    
    def MaskingData(self):
        col = self.ui.INPUTtable.currentColumn() #get Selected Column number
        if self.ui.INPUTtable.item(col,0) is None: # if value is null, do nothing
            print('cell has nothing (NonIdentifierMethod)')
        else: #if not null, radio button check
            self.newWindow = MaskingDataMethod(self)
    
    """
    def CategoricalData(self):
        col = self.ui.INPUTtable.currentColumn() #get Selected Column number
        if self.ui.INPUTtable.item(col,0) is None: # if value is null, do nothing
            print('cell has nothing (NonIdentifierMethod)')
        else: #if not null, radio button check
            self.newWindow = CategoricalDataMethod(self)
    """

class ImportDataWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ImportDataWindow, self).__init__(parent)
        self.ui = uic.loadUi("./UI/ImportData.ui") #insert your UI path
        self.ui.show()
        self.ui.toolButton.clicked.connect(self.ImportDataButton)
        self.ui.cancelButton.clicked.connect(self.ui.hide)
      
    def ImportDataButton(self):

        inputdata = pd.read_csv('./DATASET/data2.csv', sep=",",encoding='euc-kr') #read file
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
    
    def changeWindow(self):
        self.ui.hide()
        self.modify = ModifyData()

    def cancelButton(self):
        self.ui.hide()
        self.mainUI = MainWidget()

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
        global tab1_input, tab2_output
        #checked columns
        checked_number = [] # checkbox index
        uncheced_number = []
        check_columns = []  # 체크된 컬럼들
        combo_id = []
        types = []
        for i in range(len(tab1_input.columns)):
            chbox = self.ui.dataTypeChange.cellWidget(i,0) # 0부터 checkbox 값 가져오기
            # print(chbox)
            if isinstance(chbox, MyCheckBox):
                if chbox.isChecked():
                    checked_number.append(i)
                    checkedColumn = self.ui.dataTypeChange.item(i,1).text()
                    check_columns.append(checkedColumn)
                    combo_id.append(self.ui.dataTypeChange.cellWidget(i,5).currentText()) #식별자 combo box
                    if(self.ui.dataTypeChange.cellWidget(i,4).currentText() == 'SAME'):
                        types.append(self.ui.dataTypeChange.item(i,3).text())
                    else:
                        types.append(self.ui.dataTypeChange.cellWidget(i,4).currentText())
                else:
                    uncheced_number.append(i)
        """
        uncheced_number.reverse() # 리스트 거꾸로 넣어서 index error 제거, 
        for i in uncheced_number:
            tab1_input = tab1_input.drop(tab1_input.columns[i], axis=1) #사용자가 선택한 컬럼만 tab1_input에 저장
            tab2_output = tab2_output.drop(tab2_output.columns[i], axis=1) 
        """

        print(checked_number) # just 확인용
        print(check_columns) # just 확인용    
        
        #MainWidget() rendering
        #self.ui.hide()  

        #self.ui = uic.loadUi("./UI/NonIdentifierUI.ui") #insert your UI path
        #self.ui.show()

        self.mainUI = MainWidget()
        
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
        for rowindex in range(colnum): #행번호            
            self.mainUI.ui.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(check_columns[rowindex]))) #setitem 컬럼이름 
            self.mainUI.ui.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)
            self.mainUI.ui.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(types[rowindex])))

        self.ui.hide()
        
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

"""
class MaskingDataMethod(QMainWindow):
    global tab1_input, tab2_output
    global before, after, SelectColumn, SelectColumnName, rownum, colnum

    def __init__(self, parent=None):
        super(MaskingDataMethod, self).__init__(parent)
        self.InitUI()
    
    def InitUI(self):
        self.ui = uic.loadUi("./UI/maskingData.ui") #insert your UI path
        self.ui.show()

        global before, after, SelectColumn, SelectColumnName, rownum, colnum
        SelectColumn = self.parent().ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.parent().ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name
        
        self.m_index = self.ui.m_comboBox.currentIndexChanged.connect(self.usedbyMasking)
        self.level = self.ui.maskingText.textChanged.connect(self.usedbyMasking)

        before = tab1_input[tab1_input.columns[SelectColumn]].to_frame() #pull one column and convert list
        rownum = len(before.index) # get row count
        colnum = len(before.columns) # get column count
        
        print("--------")
        print(before)
        print(before[before.columns[0]][1])
        print(before.columns)
        print(list(before.columns))
        
        self.ui.nextButton.clicked.connect(self.Masking)
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    def usedbyMasking(self):
        self.m_index = self.ui.m_comboBox.currentIndex()

        self.level = self.ui.maskingText.toPlainText()
        print("first")
        print(type(self.level))
        try:
            self.level = int(self.level)
            print("Second")
            print(type(self.level))
            if(self.level<1):
                self.level/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass
        
    def Masking(self):
        self.ui = uic.loadUi("./UI/maskingData_review.ui") #insert your UI path
        self.ui.show()
   
        self.ui.maskingLevel.setRowCount(rownum) #Set Column Count s    

        global before, after
    
        after = before.copy()
        maskingLev = []

        before_uniq = before[SelectColumnName].unique()
        before_uniq = list(before_uniq)
        maskingLev = list(before_uniq)

        print("@@@@@@")
        print(before_uniq)
        print(type(before_uniq))
        
        #uniq = [] #type : list
        uniq_slice = []
        uniq_len = []
        
        max_len = len(str(before[SelectColumnName][0]))

        for j in range(rownum): #rendering data (inputtable of Tab1)
            if max_len < len(str(before[SelectColumnName][j])):
                max_len = len(str(before[SelectColumnName][j]))
           
        self.ui.maskingLevel.setColumnCount(2)

        
        for j in range(rownum): #rendering data (inputtable of Tab1)
            for u in range(len(before_uniq)):
                #uniq.append(before_uniq[u])
                #uniq[u] = str(uniq[u]) 
                #uniq_slice.append(list(uniq[u])) # 한글자씩 추출하기 위해 list 사용
                #uniq_len.append(len(uniq[u])) # 마스킹할 데이터의 최대 길이 구하는 것

                before_uniq[u] = str(before_uniq[u])
                
                uniq_slice.append(list(before_uniq[u])) 
                uniq_len.append(len(before_uniq[u])) # 마스킹할 데이터의 최대 길이 구하는 것

                for l in range(1,self.level+1):
                    #if before[before.columns[0]][j] == uniq[u]:
                    #after[after.columns[0]][j] = str(after[after.columns[0]][j]).replace(uniq_slice[u][uniq_len[u]-l], "*")
                
                    maskingLev[u] = str(maskingLev[u]).replace(uniq_slice[u][uniq_len[u]-l], "*")
        
                if(self.m_index == 0): # * masking
                    #after[after.columns[0]][j] = str(after[after.columns[0]][j]).replace(uniq_slice[u][uniq_len[u]-l], "*")
                    after.loc[after[SelectColumnName]==str(before_uniq[u]), SelectColumnName] = str(maskingLev[u])
                elif(self.m_index == 1): # 0 masking
                    after[after.columns[0]][j] = str(after[after.columns[0]][j]).replace(uniq_slice[u][uniq_len[u]-l], "0")
                elif(self.m_index == 2): # remove
                    after[after.columns[0]][j] = str(after[after.columns[0]][j]).replace(uniq_slice[u][uniq_len[u]-l], " ")


            self.ui.maskingLevel.setItem(j,0,QTableWidgetItem(before[SelectColumnName][j]))
            self.ui.maskingLevel.setItem(j,1,QTableWidgetItem(after[after.columns[0]][j]))
        
        #self.ui.cancelButton.clicked.connect(self.MaskingDataMethod)
"""        

class CategoricalDataMethod(QMainWindow):
    global tab1_input, tab2_output
    global before, after, SelectColumn, SelectColumnName, rownum, colnum

    def __init__(self, parent=None):
        super(CategoricalDataMethod, self).__init__(parent)
        self.InitUI()
    
    def InitUI(self):
        self.ui = uic.loadUi("./UI/CategoricalData.ui") #insert your UI path
        self.ui.show()

        global before, after, SelectColumn, SelectColumnName, rownum, colnum
        SelectColumn = self.parent().ui.INPUTtable.currentColumn() #get Selected Column number
        SelectColumnName = self.parent().ui.INPUTtable.horizontalHeaderItem(SelectColumn).text() #get Selected Column name
        
        before = tab1_input[tab1_input.columns[SelectColumn]].to_frame() #pull one column and convert list
        rownum = len(before.index) # get row count
        colnum = len(before.columns) # get column count
        
        self.ui.nextButton.clicked.connect(self.Categorical_next)
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    def Categorical_next(self):
        global before, after
        
        if(self.ui.ordering.isChecked()):
            self.ui = uic.loadUi("./UI/ordering_categorical.ui")
            self.ui.show()
        
            #self.original_uniq = before[before.columns[0]].unique()
            self.original_uniq = before[SelectColumnName].unique()
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

        elif(self.ui.intervals.isChecked()):
            self.ui = uic.loadUi("./UI/intervals_categorical.ui") #insert your UI path
            self.ui.show()

            self.ui.original.setRowCount(rownum) #Set Column Count s 
            self.ui.original.setHorizontalHeaderLabels(['original'])

            for j in range(rownum): #rendering data (inputtable of Tab1)
                self.ui.original.setItem(j,0,QTableWidgetItem(str(before[before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Intervals_Categorical)
    
            
    def Intervals_Categorical(self):
        after = before.copy()

        self.ui.categorical.setRowCount(rownum) #Set Column Count s 
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
            
        for j in range(rownum):
            if before[before.columns[0]][j] < minValue:
                after[after.columns[0]][j] = "<" + str(minValue)
                self.ui.categorical.setItem(j,0,QTableWidgetItem(str(after[after.columns[0]][j])))
            elif before[before.columns[0]][j] > maxValue:
                after[after.columns[0]][j] = ">" + str(maxValue)
                self.ui.categorical.setItem(j,0,QTableWidgetItem(str(after[after.columns[0]][j])))
            else:
                ii = int((maxValue-minValue)/interValue)
                for i in range(ii):
                    if before[before.columns[0]][j]-minValue >= i*interValue and before[before.columns[0]][j]-minValue < (i+1)*interValue:
                        after[after.columns[0]][j] = "[" + str(minValue+i*interValue) + "," + str(minValue+(i+1)*interValue) + ")"
                        self.ui.categorical.setItem(j,0,QTableWidgetItem(str(after[after.columns[0]][j])))

    def Ordering_Categorical(self):

        orderValue = self.ui.orderText.toPlainText()
        UsrChckVal = orderValue.split(',')
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
            
            #print(self.groupEle)
            #print(self.str_groupEle)
            
        except ValueError:
            QtWidgets.QMessageBox.about(self, 'Error','이미 범주화 처리가 된 요소입니다.')
        pass
      
        self.ui.finishButton.clicked.connect(self.Ordering_Categorical_finish)

    def Ordering_Categorical_finish(self):
        after = before.copy()

        for b in range(self.a):
            for z in range(len(self.groupEle[b])):
                after.loc[after[SelectColumnName]==str((self.groupEle[b][z])), SelectColumnName] = str((self.str_groupEle[b]))

                    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())