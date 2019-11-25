#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pandas.api.types as ptypes
from pandas import Series, DataFrame
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets

import matplotlib.pyplot as plt
from datetime import datetime
plt.rc('font', family='Malgun Gothic') #한글 깨짐 방지
plt.rc('axes', unicode_minus=False) #한글 깨짐 방지

#to import UI path
sys.path.append("./UI") # insert your path
sys.path.append("./PY_CODE")


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
        print("checkbox row= ", self.get_row(), "in CheckBox.py") 
        
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

