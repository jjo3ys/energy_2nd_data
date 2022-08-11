import time
import gurobipy as gp
from gurobipy import GRB
from gurobipy import *
import pandas as pd
import math

def linebyline(df):
    on_list = [0, 0, 0, 0, 0, 0]
    result = []
    rt_list = [427.5, 427.5, 162, 162, 360, 360]
    df= df.to_numpy().tolist()
        # Create a new model
    for i in range(len(df)):
        demand = df[i][1]
        on_count_list = [1 if on_list[i]<=3 and on_list[i] >= 1 else 0 for i in range(len(on_list)) ]
        #Over
        m = gp.Model("mip1")
        m.setParam('OutputFlag', 0)

        var_list = [m.addVar(vtype=GRB.BINARY, name="{}ref".format(i+1)) for i in range(len(on_list))]
        m.update()

        obj = (427.5*var_list[0] + 427.5*var_list[1] + 162*var_list[2] + 162*var_list[3] + 360*var_list[4] + 360*var_list[5] - demand)
        m.setObjective(obj, GRB.MINIMIZE)

        for j in range(len(on_list)): 
            m.addConstr(var_list[j] >= on_count_list[j], "c{}".format(j))
        m.addConstr(obj >= 0, "c6")
        m.optimize()

        over_re = 0
        over_on_list = [on_list[i] for i in range(len(on_list))]
        for id, v in enumerate(m.getVars()):
            if int(v.x) == 0:
                over_on_list[id] = 0
            else:
                over_on_list[id] += 1
            over_re += rt_list[id]*int(v.x)

        #Under
        m = gp.Model("mip1")
        m.setParam('OutputFlag', 0)

        var_list = [m.addVar(vtype=GRB.BINARY, name="{}ref".format(i+1)) for i in range(len(on_list))]
        m.update()

        obj = demand - (427.5*var_list[0] + 427.5*var_list[1] + 162*var_list[2] + 162*var_list[3] + 360*var_list[4] + 360*var_list[5])
        m.setObjective(obj, GRB.MINIMIZE)
 
        for j in range(len(on_list)): 
            m.addConstr(var_list[j] >= on_count_list[j], "c{}".format(j))
        m.addConstr(obj >= 0, "c6")
        m.optimize()

        under_on_list = [on_list[i] for i in range(len(on_list))]
        under_re = 0
        for id, v in enumerate(m.getVars()):
            try:
                if int(v.x) == 0:
                    under_on_list[id] = 0
                else:
                    under_on_list[id] += 1
                under_re += rt_list[id]*int(v.x)
            except:
                
                if under_on_list[id] >= 1 and under_on_list[id] <=3:
                    under_re+=rt_list[id]
                    under_on_list[id] += 1

        if abs(under_re-demand)*2 < abs(over_re-demand):
            optim = under_re
            on_list = under_on_list 
        else:
            optim = over_re
            on_list = over_on_list 

        result.append([df[i][0], optim, demand]+on_list)
    result = pd.DataFrame(result, columns = ['DATE', 'OPTM', 'Real_RT', '427.5(1)', '427.5(2)', '162(1)', '162(2)', '360(1)', '360(2)'])
    result.to_csv('gurobi_result.csv', index=None)

def oneday(df):
    rt_list = [427.5, 427.5, 162, 162, 360, 360]
    df['day'] = pd.to_datetime(df['DATE']).dt.day
    date_ = df['DATE'].to_numpy().tolist()
    day_ = df['day'].to_numpy().tolist()
    rt_ = df['Real_RT'].to_numpy().tolist()
    real_dict = {}
    for date, day, rt in zip(date_, day_, rt_):
        if day not in real_dict:
            real_dict[day] = [[rt, date]]
        else:
            real_dict[day].append([rt, date])

    print(len(real_dict))
    prod_list = []
    for day in real_dict:
        m = gp.Model('mip1')
        m.setParam('OutputFlag', 0) 

        rt475_1 = {}
        rt475_2 = {}
        rt180_1 = {}
        rt180_2 = {}
        rt600_1 = {}
        rt600_2 = {}
        
        demand = 0

        for id, data in enumerate(real_dict[day]):
            rt475_1[id] = m.addVar(vtype=GRB.BINARY, name="475rt1_{}".format(id))
            rt475_2[id] = m.addVar(vtype=GRB.BINARY, name="475rt2_{}".format(id))
            rt180_1[id] = m.addVar(vtype=GRB.BINARY, name="180rt1_{}".format(id))
            rt180_2[id] = m.addVar(vtype=GRB.BINARY, name="180rt2_{}".format(id))
            rt600_1[id] = m.addVar(vtype=GRB.BINARY, name="600rt1_{}".format(id))
            rt600_2[id] = m.addVar(vtype=GRB.BINARY, name="600rt2_{}".format(id))
            demand += data[0]

        obj = quicksum(427.5*rt475_1[id] for id in range(len(real_dict[day])))+\
              quicksum(427.5*rt475_2[id] for id in range(len(real_dict[day])))+\
              quicksum(162*rt180_1[id] for id in range(len(real_dict[day])))+\
              quicksum(162*rt180_2[id] for id in range(len(real_dict[day])))+\
              quicksum(360*rt600_1[id] for id in range(len(real_dict[day])))+\
              quicksum(360*rt600_2[id] for id in range(len(real_dict[day]))) - demand
        # obj = (427.5*rt475_1[id] + 427.5*rt475_2[id] + 162*rt180_1[id] + 162*rt180_2[id] + 360*rt600_1[id] + 360*rt600_2[id] for id in range(len(real_dict[day]))) - demand
        m.setObjective(obj**2, GRB.MINIMIZE)
        for id in range(len(real_dict[day])):
            if id == 0:
                m.addConstr(rt475_1[id] <= 1)
                m.addConstr(rt475_2[id] <= 1)
                m.addConstr(rt180_1[id] <= 1)
                m.addConstr(rt180_2[id] <= 1)
                m.addConstr(rt600_1[id] <= 1)
                m.addConstr(rt600_2[id] <= 1)
            
            else:
                for i in range(1, 4):
                    if id+i in rt475_1:
                        m.addConstr(rt475_1[id+i] >= rt475_1[id])
                        m.addConstr(rt475_2[id+i] >= rt475_2[id])
                        m.addConstr(rt180_1[id+i] >= rt180_1[id])
                        m.addConstr(rt180_2[id+i] >= rt180_2[id])
                        m.addConstr(rt600_1[id+i] >= rt600_1[id])
                        m.addConstr(rt600_2[id+i] >= rt600_2[id])
        print("start")
        start = time.time()
        m.optimize()
        prod = 0
        print('end : {}'.format(time.time()-start))
        for id, v in enumerate(m.getVars()):
            if id % 6 == 0 or id%6 == 1:
                prod += int(v.x)*427.5
            elif id% 6 == 2 or id%6 == 3:
                prod += int(v.x)*162
            elif id%6 == 3:
                prod += int(v.x)*360
            else:
                prod += int(v.x)*360
                prod_list.append(prod)
                prod = 0
        
            # if int(v.x) == 0:
            #     over_on_list[id] = 0
            # else:
            #     over_on_list[id] += 1
            # on_result.append(int(v.x))
    mip = pd.DataFrame(prod_list, columns='mip', index=None)
    mip.to_csv('MIP.csv', index=None)

df = pd.read_csv("DQN_data.csv")
oneday(df)