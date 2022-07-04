import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

df1 = pd.read_csv("augumentationed_data.csv", index_col=None)

def return_degree_model():
    df2 = pd.read_csv("degree_data.csv", index_col=None)

    df = pd.merge(df1, df2, how='left')

    x = df.drop(['날짜', '환수온도'], axis=1)
    y = df['환수온도']

    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, test_size=0.2)

    MLR = LinearRegression()
    MLR.fit(x_train, y_train)

    y_predict = MLR.predict(x_test)

    plt.scatter(y_test, y_predict, alpha=0.4)
    plt.xlabel("Actual Return Degree")
    plt.ylabel("Predicted Return Degree")
    plt.title("MULTIPLE LINEAR REGRESSION")
    plt.savefig('Return_Degree_Result.png')

    print('Accuracy : {}%'.format(round(1-(((y_test-y_predict)**2).sum()/((y-y.mean())**2).sum()), 4)*100))

def temperature_model():
    df2 = pd.read_csv("temperature.csv", index_col=None)

    df = pd.merge(df1, df2, how='left')

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

    print('Accuracy : {}%'.format(round(1-(((y_test-y_predict)**2).sum()/((y-y.mean())**2).sum()), 4)*100))