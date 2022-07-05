from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import math

header = ['대학본부', '교수회관', '정보전산원', '자연대학', '도서관', '정보기술대학', '공과대학', '공동실험실습관', '사회법과대학', '인문대학', '동북아경제통상', '컨벤션센터', '예체능대학', '학생복지회관', '복지회관']

start_date = '2021-06-01'
start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

s_r_degree = {}
for h in header:
    s_r_degree[h] = {}
    s_r_degree[h]['날짜'] = []
    s_r_degree[h]['supply'] = []
    s_r_degree[h]['return'] = []

for i in range(31):
    df = pd.read_excel('Report\\{}.xls'.format(start_date), sheet_name='Sheet1').to_numpy()[6:30, :].tolist()
    for d in df:
        for i in range(15):
            s_r_degree[header[i]]['날짜'].append(str(start_date)+' '+str(d[0]))
            s_r_degree[header[i]]['return'].append(d[i*10+4])
            s_r_degree[header[i]]['supply'].append(d[i*10+5])
    start_date += timedelta(days=1)

for data in s_r_degree:
    df = pd.DataFrame(s_r_degree[data])
    df.to_csv("{}.csv".format(data), index=None)

# for i in range(30):
#     df