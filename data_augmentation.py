import pandas as pd
import numpy as np


buildings = ['공과대학', 
             '공동실험실습관', 
             '교수회관', 
             '대학본부', 
             '도서관', 
             '동북아경제통상', 
             '복지회관', 
             '사회법과대학', 
             '예체능대학', 
             '인문대학', 
             '자연대학', 
             '정보기술대학', 
             '정보전산원', 
             '컨벤션센터', 
             '학생복지회관']

def Supply_Return_DataAugumentaion():
    datetime_id = pd.date_range(start='2021-06-01 00:00:00', end='2021-06-30 23:45:00', freq="15T")
    df = pd.DataFrame(index=datetime_id)

    for building in buildings:
        supply_list = []
        return_list = []

        building_df = pd.read_csv("{}.csv".format(building))
        building_df['날짜'] = pd.to_datetime(building_df['날짜'])
        building_df = building_df.loc[building_df['날짜'] <= pd.to_datetime('2021-07-01 00:00:00')]
        building_df = building_df.to_numpy().tolist()
        for i in range(len(building_df)):
            Supply = building_df[i][1]
            Return = building_df[i][2]

            try:
                next_supply = building_df[i+1][1]
                next_return = building_df[i+1][2]
            except IndexError: continue

            supply_list.append(Supply)
            return_list.append(Return)

            for i in range(1, 4):
                supply_list.append(Supply+(Supply + next_supply)*i/4)
                return_list.append(Return+(Return + next_return)*i/4)

        df["{}_supply".format(building)] = supply_list
        df["{}_return".format(building)] = return_list

    df.to_csv('augumentationed_data.csv')

def Degree_DataAugumentaion():
    df = pd.read_csv('degree_data.csv')
    degree = df['환수온도'].to_numpy().tolist()
    for i in range(len(degree)):
        if str(degree[i]) == 'nan' and str(degree[i+1]) == 'nan':
            count = 2
            while True:
                if str(degree[i+count]) != 'nan':break
                count += 1
            try:
                degree[i] = (degree[i-1]+degree[i+count])/count
            except:
                degree[i] = sum(degree)/len(degree)
        
        elif str(degree[i]) == 'nan':
            try:
                ave = (degree[i-1]+degree[i+1])/2
                degree[i] = int(ave)
            except:
                degree[i] = sum(degree)/len(degree)

    df['환수온도'] = degree
    df['날짜'] = pd.date_range(start='2021-06-01 00:00:00', end='2021-06-30 23:45:00', freq="15T")
    df.to_csv('degree_data.csv', columns=['날짜', '환수온도'], index=None)