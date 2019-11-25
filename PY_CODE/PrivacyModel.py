class PrivacyModel:
    
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWin = mainWindow

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
        lenth = self.mainWin.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.mainWin.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.mainWin.ui.typeTable.item(i, 0).text())

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
        lenth = self.mainWin.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.mainWin.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.mainWin.ui.typeTable.item(i, 0).text())

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

