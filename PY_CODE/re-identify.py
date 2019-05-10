#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 20:34:53 2018

@author: zel0rd


import csv
import sys
import pandas as pd
from pandas import Series, DataFrame
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import numpy


from operator import itemgetter 
from sklearn.utils import shuffle
data = pd.read_csv('identify_data.csv',sep=",",encoding='euc-kr')
data = shuffle(data)
print(data[:100])

data['우편번호'].values
data['나이'].values

#table구하기
list(set(data['나이'].values))
for i in range(data.columns):
    list(set(data[data.columns[i]].values))
    
data.to_csv("tt.csv",encoding='euc-kr')

data['나이'].index


"""

import csv
import sys
import pandas as pd
from pandas import Series, DataFrame
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import numpy


import time

global data_1
global data_2
global print_line
global new_data_2
global new_data_1

fileName = ""
class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("re-identify.ui")
        self.ui.show()
        
        self.ui.add_1.clicked.connect(self.openFileNameDialog)
        self.ui.add_2.clicked.connect(self.openFileNameDialog2)
        self.ui.compareButton.clicked.connect(self.compare)
        self.ui.compareButton_2.clicked.connect(self.test)
        self.ui.add_key.clicked.connect(self.add_key)
        self.ui.show_table.clicked.connect(self.show_table)
        self.ui.export_2.clicked.connect(self.export)
        
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        #self.openFileNameDialog()
        #self.openFileNamesDialog()
 
        self.show()
 
        self.ui.pushButton.clicked.connect(self.openFileNameDialog)
        
    def openFileNameDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        print(fileName)
        data = pd.read_csv(fileName,sep=",",encoding='euc-kr')
        global data_1
        data_1 = data
        print(data_1)
        self.ui.path_1.setText(fileName)   
        self.ui.tableWidget_1.setColumnCount(len(data.columns))
        
        #cellinfo=QTableWidgetItem(item)
       #self.ui.tableWidget = QTableWidget()
        #self.ui.tableWidget.setHorizontalHeaderLabels((data.columns[0],data.columns[1], data.columns[2]))
        #self.ui.tableWidget.setVerticalHeaderLabels((data.columns[0],data.columns[1], data.columns[2]))
        #self.ui.tableWidget.setRowCount(len(data.columns))
        #self.ui.tableWidget.setColumnCount(len(data.columns))
        #for i in len(data.columns):
         #   self.ui.tableWidget.setItem(0,i,tableWidgetItem(data.columns[i]))
       # self.ui.tableWidget.setRowCount(4) 
        #self.ui.tableWidget.setColumnCount(2)
      #  self.ui.tableWidget.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
        #self.ui.tableWidget.setItem(1,0, "bbb")
        #self.ui.tableWidget.setItem(1,1, "ccc")
        """
        col=0
        row=0
        for tup in data.columns:
            for item in tup:
                cellinfo=QTableWidgetItem(item)
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col+=1
            row += 1
            
        for i in data.columns:
            for j in len(data.columns):
                cellinfo=QTableWidgetItem(data.columns[i])
                self.
                """

        for i in range(len(data.columns)):
            self.ui.tableWidget_1.setItem(0,i,QTableWidgetItem(data.columns[i]))
            
        for i in range(len(data.columns)):
            for j in range(1,6):
               # print(str(i) + " " + str(j))
                self.ui.tableWidget_1.setItem(j,i,QTableWidgetItem(str(data[data.columns[i]][j])))
               # print(data[data.columns[i]][j])            

        #columnCount()
        #print(self.ui.tableWidget.columnCount())
        
#        for i in range(self.ui.tableWidget_1.columnCount()):
#            for j in range(self.ui.tableWidget_1.rowCount()):
#                datas
#        
#        temp = []
#        print(self.ui.tableWidget_1.columnCount())
#        for i in range(self.ui.tableWidget_1.columnCount()):
#            for j in range(self.ui.tableWidget_1.rowCount()):
#                print(self.ui.tableWidget_1.item(j,i).text())
#                temp
#        df = []
#        for i in range(self.ui.tableWidget_.columnCount()):
#            df.append(list(self.ui.tableWidget_4[self.ui.tableWidget_4.colums[i]].values))
#        
#        print(df)
#        self.ui.tableWidget_1.Item(1,1).text()
##       

    def openFileNameDialog2(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        print(fileName)
        data = pd.read_csv(fileName,sep=",",encoding='euc-kr')
        global data_2
        data_2 = data
        print(data_2)
        self.ui.path_2.setText(fileName)
        self.ui.tableWidget_3.setColumnCount(len(data.columns))
        for i in range(len(data.columns)):
            self.ui.tableWidget_3.setItem(0,i,QTableWidgetItem(data.columns[i]))
            
        for i in range(len(data.columns)):
            for j in range(1,6):
                #print(str(i) + " " + str(j))
                self.ui.tableWidget_3.setItem(j,i,QTableWidgetItem(str(data[data.columns[i]][j])))
                #print(data[data.columns[i]][j])
        #cell = self.ui.tableWidget.item(1,1).text()
        #print(cell)
        #for i in range(len)
        
        #self.ui.tableWidget.setColumnCount(2)
        
    def test(self):
        origin_columns = []
        id_columns = []
        for i in range(self.ui.tableWidget_1.columnCount()):
            origin_columns.append(self.ui.tableWidget_1.item(0,i).text())
        #print(origin_columns)
            
        for i in range(self.ui.tableWidget_3.columnCount()):
            id_columns.append(self.ui.tableWidget_3.item(0,i).text())
        #print(id_columns)
        #print(origin_columns)
        #print(id_columns)
        
        #공통 컬럼 검색
        temp = []
        for i in range(len(origin_columns)):
            if origin_columns[i] in id_columns:
                temp.append(origin_columns[i])
                
        for i in range(len(temp)):
            self.ui.tableWidget_6.setItem(0,i,QTableWidgetItem(temp[i]))
        
        
    def compare(self):
        #set Columns name
        global print_line
        print_line = self.ui.lineEdit.text()
        
        origin_columns = []
        id_columns = []
        for i in range(self.ui.tableWidget_1.columnCount()):
            origin_columns.append(self.ui.tableWidget_1.item(0,i).text())
        #print(origin_columns)
            
        for i in range(self.ui.tableWidget_3.columnCount()):
            id_columns.append(self.ui.tableWidget_3.item(0,i).text())
        #print(id_columns)
        #print(origin_columns)
        #print(id_columns)
        
        #공통 컬럼 검색
        temp = []
        for i in range(len(origin_columns)):
            if origin_columns[i] in id_columns:
                temp.append(origin_columns[i])
                
        print(temp)
        #for i in temp:
        #    print(data_1[temp])
        
        dic = {}
        new_dic = {}
        for i in range(len(temp)):
            dic[i] = temp[i]
        
        for k,v in dic.items():
            new_dic[v] = k
            
            
        
        global new_data_1
        global new_data_2
            
        new_data_1 = []
        for i in temp:
            new_data_1 = pd.concat([data_1[temp]],axis=1)
            
        new_data_2 = []
        for i in temp:
            new_data_2 = pd.concat([data_2[temp]],axis=1)
        
        #compare용 데이터 생성 완료
        print(new_data_1)
        print(new_data_2)
        
        print(type(new_data_1))
        print(new_data_1)
        
        """
        for i in range(len(data.columns)):
            for j in range(1,6):
               # print(str(i) + " " + str(j))
                self.ui.tableWidget_1.setItem(j,i,QTableWidgetItem(str(data[data.columns[i]][j])))
      
        
        print(dic)
        print(new_dic)
        for k,v in new_data_1.items():
            col = new_dic[k]
            for row,val in enumerate(v):
                item = QTableWidgetItem(val)
                self.ui.tableWidget_4.setItem(row,col,item)
         """
        #tableWidget_4 Header 입력
        for i in range(len(new_data_1.columns)):
            self.ui.tableWidget_4.setItem(0,i,QTableWidgetItem(new_data_1.columns[i]))
         
        #new_data_1 Data 입력
        for i in range(len(new_data_1.columns)):
             for j in range(1,int(print_line)+1):
                 #print(new_data_1[new_data_1.columns[i]][j])
                 self.ui.tableWidget_4.setItem(j,i,QTableWidgetItem(str(new_data_1[new_data_1.columns[i]][j])))
        #tableWidget_5 Header 입력   
        for i in range(len(new_data_2.columns)):
            self.ui.tableWidget_5.setItem(0,i,QTableWidgetItem(new_data_2.columns[i]))
        
        #new_data_2 Data 입력
        for i in range(len(new_data_2.columns)):
             for j in range(1,int(print_line)+1):
                 #print(new_data_1[new_data_1.columns[i]][j])
                 self.ui.tableWidget_5.setItem(j,i,QTableWidgetItem(str(new_data_2[new_data_2.columns[i]][j])))
        
        #df3 = self.ui.tableWidget_4.getdataframe
        #print(type(df3))
        #df3.to_csv("test_df3.csv")
    
        #self.ui.tableWidget_4.setHorizontalHeaderLables(["aaa","bbb"])
        #self.ui.tableWidget_5.setHorizontalHeaderLables(temp)
        
        #for i in range(len(temp)):
            
    def show_table(self):
        df=[]
        for i in range(len(new_data_2.columns)):
#            df.append(list(set(self.ui.tableWidget_5.Item(0,i).text())))
            df.append(list(set(new_data_2[new_data_2.columns[i]].values)))
        
        df2 = DataFrame(df)
        df2_T = df2.transpose()
        df2_T.to_csv("id_table.csv")
#        
#        
#        print(new_data_2.columns[0])
        
        
      ##      col = 
            
            #for j in temp:
                #print(data_1[temp][i])
                #self.ui.tableWidget_4.setItem(i,temp,QTableWidgetItem(data_1[temp][i]))
        """
        print(data_1)
        print(temp)
        print("********************")
        for i in range(len(temp)):
            print(data_1['나이'])
        print("&&&&&&&&&&&&&&&&&&&&")
        for i in range(len(temp)):
            print(data_2[temp[i]])
        """     
        #print(origin_columns)
        #print(id_columns)
        #print(temp)
    def export(self):  
        
        
        headers = []
        for i in range(self.ui.tableWidget_4.columnCount()):
            headers.append(self.ui.tableWidget_4.item(0,i).text())
            
#        print(headers)
        
        #data 선언
        
        data = [["a"] * self.ui.tableWidget_4.columnCount() for i in range(int(print_line))]
        #print(data)

        #print(self.ui.tableWidget_4.rowCount())
        #print(self.ui.tableWidget_4.columnCount())
        
        #대입
        for i in range(int(print_line)):
            for j in range(self.ui.tableWidget_4.columnCount()):
#                data[i][j] =  self.ui.tableWidget_4.item(i+1,j).text()
                print("%s %s"%(i,j))
                data[i][j] = self.ui.tableWidget_4.item(i+1,j).text()
                
        print(data)
        
        f = open('export_test.csv','w',encoding='euc-kr',newline='')
        wr = csv.writer(f, delimiter='\t')
        
        wr.writerow([0,headers])
        for i in range(len(data)):
            wr.writerow([i,data[i]])
            
        f.close()
        
        print("done")
        
        #new lablel 생성
    def add_key(self):
        
        
        columns = self.ui.tableWidget_4.columnCount()
        rows = self.ui.tableWidget_4.rowCount()
        
        global new_data_1
        global new_data_2
        global print_line
        #data[:100]
        
        
        print(new_data_1['나이'])
        
        export_data = new_data_1[:int(print_line)]

#        new_data_1 = new_data_1['나이']


        id_ages = []
        for i in range(len(export_data['나이'])):
            if(0 <= export_data['나이'][i] < 10):
                id_ages.append('0')
            elif(10 <= export_data['나이'][i] < 20):
                id_ages.append('1')
            elif(20 <= export_data['나이'][i] < 30):
                id_ages.append('2')
            elif(30 <= export_data['나이'][i] < 40):
                id_ages.append('3')
            elif(40 <= export_data['나이'][i] < 50):
                id_ages.append('4')
            elif(50 <= export_data['나이'][i] < 60):
                id_ages.append('5')
            elif(60 <= export_data['나이'][i] < 70):
                id_ages.append('6')
            elif(70 <= export_data['나이'][i] < 80):
                id_ages.append('7')
                
        id_ages = pd.DataFrame(id_ages)

        #print(id_ages)
                
        export_data = pd.concat([export_data,id_ages],axis=1)
        export_data.to_csv("ort_test.csv",encoding='euc-kr')
        
        
        
        #export_data = pd.concat([export_data,id_ages],axis=1)
#        
#        export_data.to_csv("ori_test",encoding='euc-kr')
#        
        
        
        
        
#        f = open('ori_test.csv','w',encoding='euc-kr',newline='')
#        wr = csv.writer(f, delimiter='\t')
#        
#        wr.writerow(new_data_1.columns)
#        for i in range(len(new_data_1['나이'])):
#            wr.writerow(new_data_1[i])
#            
#        f.close()
#        
        
        #print(id_ages)
        #print("done2")
                
                
            
        
        #dataset = numpy.zeros((rows,columns))
        
#        df = []
#        for i in range(self.ui.tableWidget_4.columnCount()):
#            df.append(list(self.ui.tableWidget_4[self.ui.tableWidget_4.colums[i]].values))
#        
#        print(df)
#        for i in range(len(new_data_2.columns)):
#            df.append(list(set(new_data_2[new_data_2.columns[i]].values)))
        
#        print(dataset)
        #test = self.ui.tableWidget_1.item(0,0)
        #print(test)
#        #print(test.text())
#        
#        for i in range(rows):
#            for j in range(columns):
#                #print(str(i) + " " + str(j) + "\n")
#                #dataset[i][j] =  self.ui.tableWidget_4.item(i,j)
#                #print(self.ui.tableWidget_4.item(i,j).text())
#                dataset[i][j] = self.ui.tableWidget_4.item(i,j).text()
                
       # print(dataset)
       
      
                
#        print(self.ui.tableWidget_4.rowCount()-1)
#        print(self.ui.tableWidget_4.columnCount())
#        
#        df = pd.DataFrame(data)
#        for i in range(5):
#            for i in range(len(data[0])):
#                print(data[i][j])
##        print(data.head())
#        print(type(data))
#        print(headers)
        
 
    def openFileNamesDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())