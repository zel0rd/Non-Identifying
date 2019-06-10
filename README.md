# [D&D] Non-Identifying

### Project Overview
It is a tool for Non-Identifying that prevents certain individuals from being exposed to data.  
The tool has many features.  
  
1. File Import
  - handling missing values(결측치 처리)  
  - Select columns to use(사용할 컬럼 선택)  
  - Select data attribute(속성 선택: 식별자, 비식별자, 민감정보, 일반정보)  
  - Select data type (데이터 타입 선택)
  
2. Non-Identifying
  - Swap(교환)  
  - Shuffle(재배열: 랜덤하게 섞기)    
  - Suppression(범주화: 이항변수화, 이산형화)  
  - Masking or Remove(마스킹 혹은 삭제)  
  - Aggregation(통계값처리: 평균, 최빈, 최소, 최대)  
  - Rounding(라운딩: 올림, 내림, 반올림, 랜덤)  
  - Privacy Model: K-Anonymity, L-Diversity(프라이버시모델: K-익명성, L-다양성)  
  
3. Result: Compare before & after data  
  - Re-identification risk graph  
  - Data Correlation  

### Used tool
-   **Language: Python 3.6.5
-   **Deisgn: Qt Designer

### Installing the source
1. Download.
```
git clone git@github.com:dd-nonidentifying/Non-Identifying.git
```
2. Run the code with python.

# Program Imgae

### First Tab

- Data import and Non-Identification

<img src="./image/tab1_image.png" width="60%" height=60%/>

### Second Tab

- Compare before and after data

<img src="./image/tab2_image.png" width="60%" height=60%/>
