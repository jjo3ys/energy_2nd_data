import joblib
import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

df1 = pd.read_csv("augumentationed_data.csv", index_col=None)

def return_degree_model(save=False, load=False):
    # df2 = pd.read_csv("degree_data.csv", index_col=None)
    df2 = pd.read_csv("real_temp.csv", index_col=None)

    df1['날짜'] = pd.to_datetime(df1['날짜'])
    df2['날짜'] = pd.to_datetime(df2['날짜'])

    df = pd.merge(df1, df2, how='left')
    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df[df['날짜'].dt.dayofweek <=4]

    return_list = df['환수온도'].to_numpy().tolist()
    last_list = [None for i in range(len(return_list))]
    for i in range(1, len(return_list)):
        last_list[i] = return_list[i-1]
    df['Last_Return'] = last_list

    df = df.dropna()

    x = df.drop(['환수온도', '공급온도'], axis=1)
    y = df['환수온도']
    if not load:
        x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, test_size=0.2)

        x_train1 = x_train.drop('날짜', axis=1)
        x_test1 = x_test.drop('날짜', axis=1)

        MLR = LinearRegression()
        MLR.fit(x_train1, y_train)

        y_predict = MLR.predict(x_test1)
        

        plt.scatter(y_test, y_predict, alpha=0.4)
        plt.xlabel("Actual Return Degree")
        plt.ylabel("Predicted Return Degree")
        plt.title("MULTIPLE LINEAR REGRESSION")
        plt.savefig('Return_Degree_Result_with_Real_Temp.png')

        print('R**2 : {}%'.format(round(1-(((y_test-y_predict)**2).sum()/((y_test-y_test.mean())**2).sum()), 4)*100))
    
    else:
        MLR = joblib.load('ReturnDegreeModel.pkl')
        x = x.drop('날짜', axis=1)
        y_predict = MLR.predict(x)
        
        print('R**2 : {}%'.format(round(1-(((y-y_predict)**2).sum()/((y-y.mean())**2).sum()), 4)*100))

    if save:
        joblib.dump(MLR, 'ReturnDegreeModel.pkl')
        result_df = pd.DataFrame()
        for x in x_test.columns:
            result_df[x] = x_test[x]
        
        result_df['real_return'] = y_test
        result_df['pred_return'] = y_predict

        result_df = result_df.sort_index()

        result_df.to_csv("Return_Model_Result_with_Real_Temp.csv", index=None, encoding='cp949')

def temperature_model(save=False):
    df2 = pd.read_csv("temperature.csv", index_col=None)

    df = pd.merge(df1, df2, how='left')
    df = pd.merge(df1, df2, how='left')
    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df[df['날짜'].dt.dayofweek <=4]

    x = df.drop(['날짜', '온도'], axis=1)
    y = df['온도']

    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, test_size=0.2)

    MLR = LinearRegression()
    MLR.fit(x_train, y_train)

    y_predict = MLR.predict(x_test)
    
    plt.scatter(y_test, y_predict, alpha=0.4)
    plt.xlabel("Actual Temperature")
    plt.ylabel("Predicted Temperature")
    plt.title("MULTIPLE LINEAR REGRESSION")
    plt.savefig('Temperature_Result.png')

    print('R**2 : {}%'.format(round(1-(((y_test-y_predict)**2).sum()/((y_test-y_test.mean())**2).sum()), 4)*100))

    if save:
        joblib.dump(MLR, 'TemperatureModel.pkl')
        result_df = pd.DataFrame()
        for x in x_test.columns:
            result_df[x] = x_test[x]
        
        result_df['real_temp'] = y_test
        result_df['pred_temp'] = y_predict

        result_df.to_csv("Temp_Model_Result.csv", index=None, encoding='cp949')
    
def q_model(save=False):
    df2 = pd.read_csv("temperature.csv", index_col=None)
    df = pd.merge(df1, df2, how='left')
    total_df = pd.DataFrame()

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

    total_wf = 16000
    wf = [3986.28, 1209.48, 848.66, 1259.43, 1531.40, 863.21, 1151.27, 102.52, 435.12, 935.72, 2013.41, 1212.51, 211.61, 481.76, 593.70]
    building_data = {}

    for b, w in zip(buildings, wf):
        building_data[b] = total_wf*w/sum(wf)
    for b in buildings:
        model_df = pd.DataFrame()
        model_df[b+'_Wf'] = [building_data[b] for i in range(len(df))]
        model_df[b+'_supply'] = df[b+'_supply']
        model_df['온도'] = df['온도']
        model_df[b+'_return'] = df[b+'_return']

        real_return = model_df[b+'_return'].to_numpy().tolist()
        return_list = [None for i in range(len(real_return))]
        for i in range(1, len(real_return)):
            return_list[i] = real_return[i-1]

        model_df[b+'last_return'] = return_list

        model_df = model_df.dropna()
        x = model_df[[b+'_Wf', b+'_supply', '온도', b+'last_return']]
        y = model_df[b+'_return']

        x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, test_size=0.2, random_state=32)

        MLR = LinearRegression()
        MLR.fit(x_train, y_train)
        
        y_predict = MLR.predict(x_test)
        print('{} R**2 : {}%'.format(b, round(1-(((y_test-y_predict)**2).sum()/((y_test-y_test.mean())**2).sum()), 4)*100))

        if save:
            total_df[b+'Real_supply'] = x_test[b+'_supply']
            total_df[b+'Real_return'] = y_test   
            total_df[b+'Pred_return'] = y_predict

            total_df['온도'] = x_test['온도']
            total_df = total_df.sort_index()
            if not os.path.exists('Return degree models'):
                os.mkdir('Return degree models')
            total_df.to_csv("Return degree models\\{}_Return.csv".format(b), index=None, encoding='cp949')

def calc_rt(rt, wf, supply):
    return (rt*3024)/(wf*60) + supply

def load():
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
    wf = [3986.28, 1209.48, 848.66, 1259.43, 1531.40, 863.21, 1151.27, 102.52, 435.12, 935.72, 2013.41, 1212.51, 211.61, 481.76, 593.70]
    total_rt = 1500
    list1_ = df1.drop('날짜', axis=1).to_numpy().tolist()[55]

    last_return = pd.read_csv("real_temp.csv", index_col=None).to_numpy().tolist()[54][2]

    supply_list = []
    for i in range(len(list1_)):
        if i%2 ==0: supply_list.append(list1_[i])

    case1 = []
    case1_rt = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 800, 50]
    for i in range(len(wf)):
        return_rt = calc_rt(case1_rt[i], wf[i], supply_list[i])
        case1.append(supply_list[i])
        case1.append(return_rt)

    case1.append(last_return)

    case2 = []
    case2_rt = [800, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]

    for i in range(len(wf)):
        return_rt = calc_rt(case2_rt[i], wf[i], supply_list[i])
        case2.append(supply_list[i])
        case2.append(return_rt)
    case2.append(last_return)

    for i, building in enumerate(buildings):
        print('{} 공급온도: {}, case1 환수온도: {}, case2 환수온도: {}'.format(building, round(supply_list[i], 2), round(case1[i*2+1], 2), round(case2[i*2+1], 2)))

    model = joblib.load('ReturnDegreeModel.pkl')
    case1_pred = model.predict([case1])
    case2_pred = model.predict([case2])
    
    print(case1_pred, case2_pred)
load()