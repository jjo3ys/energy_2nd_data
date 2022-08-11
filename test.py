# -*- coding:utf-8 -*-

import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# Initializing parameters --------------
PARAM_TARGET_SAMPLES = 10
PARAM_FILE_NAME = "."

# batch process = 시뮬레이션 목적으로 동일한 프로그램을 입력만 바꿔서 여러번 돌리고 싶다!
# 입력을 어떻게 바꿀 거냐?
# argument !! (argc, argv) >> c:\PLB_DEMAND_GENERATOR 3 test1  >> argc = 2, argv[0] = 3, argv[1] = test1

for s in range(1,(PARAM_TARGET_SAMPLES+1)):

    print("\n\nSampleID:"+str(s)+"====================================")

    DEMANDS = {}
    COSTS = {}
    ACC_COSTS = {}
    ACC_ACC_COSTS = {}
    ACC_RAD_COSTS = {}
    START_PERIOD = 1000
    END_OF_PERIOD = -1

    # Reading input files -------------------

    fileName = "C:/Users\gpu\PycharmProjects\mystudy\PLB_Energy\pattern/train/KBD01_PARAMETERS_" + str(s) + ".csv"

    print("Reading:" + fileName)
    df = pd.read_csv(fileName, sep=',')
    for row in range(len(df)):
        CAP_MIN = df.cap_min[row]
        CAP_MAX = df.cap_max[row]
        ACC_MIN = df.acc_min[row]
        ACC_MAX = df.acc_max[row]
        ACC_RAD_MAX = df.acc_rad_max[row]
        ACC_ACC_MAX = df.acc_acc_max[row]
        ACC_INIT = df.acc_init[row]
        ACC_END = df.acc_end[row]
        DOWNTIME_MIN = df.downtime_min[row]
        OPTIME_MIN = df.optime_min[row]

    fileName = "C:/Users\gpu\PycharmProjects\mystudy\PLB_Energy\pattern/train/KBD02_DEMANDS_" + str(s) + ".csv"
    print("Reading:" + fileName)
    df = pd.read_csv(fileName, sep=',')
    for row in range(len(df)):
        period = df.period[row]
        demand = df.demand[row]
        DEMANDS[period] = demand

        if (START_PERIOD > period):
            START_PERIOD = period

        if (END_OF_PERIOD < period):
            END_OF_PERIOD = period

    PERIODS = range(START_PERIOD, END_OF_PERIOD + 1)

    fileName = "C:/Users\gpu\PycharmProjects\mystudy\PLB_Energy\pattern/train/KBD03_COSTS_" + str(s) + ".csv"
    print("Reading:" + fileName)
    df = pd.read_csv(fileName, sep=',')
    for row in range(len(df)):
        period = df.period[row]
        cost = df.plb_cost[row]
        COSTS[period] = cost
        cost = df.acc_cost[row]
        ACC_COSTS[period] = cost
        cost = df.acc_acc_cost[row]
        ACC_ACC_COSTS[period] = cost
        cost = df.acc_rad_cost[row]
        ACC_RAD_COSTS[period] = cost

    # Modeling the MIP problem -----------------------------

    try:
        m = gp.Model("PLB_MIP")
        plb_level = {}  # Production Quantity of PLb t
        for t in PERIODS:
            varName = "plb_level[" + str(t) + "]"
            plb_level[t] = m.addVar(vtype=GRB.CONTINUOUS,name=varName)

        plb_surplus = {}
        for t in PERIODS:
            varName = "plb_surplus[" + str(t) + "]"
            plb_surplus[t] = m.addVar(vtype=GRB.CONTINUOUS,name=varName)

        plb_status = {}  # Production status(on/off)
        for t in PERIODS:
            varName = "plb_status[" + str(t) + "]"
            plb_status[t] = m.addVar(vtype=GRB.BINARY,name=varName)

        plb_startup = {}
        for t in PERIODS:
            plb_startup[t] = m.addVar(vtype=GRB.BINARY,name=("plb_startup["+str(t)+"]"))

        plb_shutdown = {}
        for t in PERIODS:
            plb_shutdown[t] = m.addVar(vtype=GRB.BINARY,name=("plb_shutdown["+str(t)+"]"))

        acc_level = {}  # Inventory level of ACC(accumulator, inventory buffer)
        for t in PERIODS:
            varName = "acc_level[" + str(t) + "]"
            acc_level[t] = m.addVar(vtype=GRB.CONTINUOUS,name=varName)

        acc_acc = {}  # Hourly accumulation amount
        for t in PERIODS:
            acc_acc[t] = m.addVar(vtype=GRB.CONTINUOUS,name=("acc_acc["+str(t)+"]"))

        acc_rad = {}  # Hourly radiation amount
        for t in PERIODS:
            acc_rad[t] = m.addVar(vtype=GRB.CONTINUOUS,name=("acc_rad["+str(t)+"]"))

        supply_in = {}  # Hourly radiation amount
        for t in PERIODS:
            supply_in[t] = m.addVar(vtype=GRB.CONTINUOUS,name=("supply_in["+str(t)+"]"))

        supply_out = {}  # Hourly radiation amount
        for t in PERIODS:
            supply_out[t] = m.addVar(vtype=GRB.CONTINUOUS,name=("supply_out["+str(t)+"]"))

        obj = GRB.quicksum(COSTS[t] * plb_level[t] for t in PERIODS) + \
              GRB.quicksum(3000 * plb_surplus[t] for t in PERIODS) + \
              GRB.quicksum(ACC_COSTS[t] * acc_level[t] for t in PERIODS) + \
              GRB.quicksum(ACC_ACC_COSTS[t] * acc_acc[t] for t in PERIODS) + \
              GRB.quicksum(ACC_RAD_COSTS[t] * acc_rad[t] for t in PERIODS) + \
              GRB.quicksum(1000000 * supply_out[t] for t in PERIODS) + \
              GRB.quicksum(2000000 * supply_in[t] for t in PERIODS)

        m.setObjective(obj, GRB.MINIMIZE)

        for t in PERIODS:
            if t == START_PERIOD:
                m.addConstr(plb_level[t] + supply_in[t] + ACC_INIT == DEMANDS[t] + supply_out[t] + acc_level[t])
            else:
                m.addConstr(plb_level[t] + supply_in[t] + acc_level[t - 1] == DEMANDS[t] + supply_out[t] + acc_level[t])

        m.addConstr(acc_level[END_OF_PERIOD] == ACC_END)

        for t in PERIODS:
            if t == START_PERIOD:
                m.addConstr(plb_startup[t] == plb_status[t])
            else:
                m.addConstr(plb_status[t - 1] + plb_startup[t] == plb_status[t] + plb_shutdown[t])

        for t in PERIODS:
            for ot in range(OPTIME_MIN):
                if t+ot in PERIODS:
                    m.addConstr(plb_status[t+ot] >= plb_startup[t])

            for dt in range(DOWNTIME_MIN):
                if t+dt in PERIODS:
                    m.addConstr(plb_status[t+dt] <= (1 - plb_shutdown[t]))

        for t in PERIODS:
            m.addConstr(plb_level[t] >= CAP_MIN * plb_status[t])
            m.addConstr(plb_level[t] <= CAP_MAX * plb_status[t])

        for t in PERIODS:
            m.addConstr(plb_surplus[t] == CAP_MAX * plb_status[t] - plb_level[t])

        for t in PERIODS:
            m.addConstr(acc_level[t] >= ACC_MIN)
            m.addConstr(acc_level[t] <= ACC_MAX)

        for t in PERIODS:
            m.addConstr(acc_acc[t] <= ACC_ACC_MAX)
            m.addConstr(acc_rad[t] <= ACC_RAD_MAX)

        for t in PERIODS:
            if t == START_PERIOD:
                m.addConstr(ACC_INIT + acc_acc[t] == acc_level[t] + acc_rad[t])
            else:
                m.addConstr(acc_level[t - 1] + acc_acc[t] == acc_level[t] + acc_rad[t])

        m.optimize()

        #m.write("TEST_"+str(s)+".lp")

        if m.status == GRB.Status.OPTIMAL:
            print("OBJ:"+str(m.objVal))
            #for v in m.getVars(): if v.x>0.001: print(v.varName+"\t"+str(v.x))

            # fileName = "KBD91_PLB_LEVEL_"+str(s)+".csv"
            # print("Writing:"+fileName)
            #
            # with open(fileName,'w') as resultFile:
            #     theHeader = str("period,plb_level\n")
            #     resultFile.write(theHeader)
            #
            #     for t in PERIODS:
            #         theRow = str(t)+","+str(plb_level[t].x)+"\n"
            #         resultFile.write(theRow)
            #
            # fileName = "KBD92_ACC_LEVEL_"+str(s)+".csv"
            # print("Writing:"+fileName)
            #
            # with open(fileName,'w') as resultFile:
            #     theHeader = str("period,acc_level\n")
            #     resultFile.write(theHeader)
            #
            #     for t in PERIODS:
            #         theRow = str(t)+","+str(acc_level[t].x)+"\n"
            #         resultFile.write(theRow)
            #
            # fileName = "KBD93_SUPPLY_IN_OUT_"+str(s)+".csv"
            # print("Writing:"+fileName)
            #
            # with open(fileName,'w') as resultFile:
            #     theHeader = str("period,supply_in,supply_out\n")
            #     resultFile.write(theHeader)
            #
            #     for t in PERIODS:
            #         theRow = str(t)+","+str(supply_in[t].x)+","+str(supply_out[t].x)+"\n"
            #         resultFile.write(theRow)

            fileName = "C:/Users\gpu\PycharmProjects\mystudy\PLB_Energy\pattern\mip/KBD99_SUMMARY_" + str(s) + ".csv"
            print("Writing:"+fileName)

            with open(fileName,'w') as resultFile:
                theHeader = str("period,demand,acc_level,acc_acc,acc_rad,plb_level,supply_in,supply_out\n")
                resultFile.write(theHeader)

                for t in PERIODS:
                    theRow = str(t)+","+str(DEMANDS[t])+","+str(int(acc_level[t].x))+ \
                             "," + str(int(acc_acc[t].x)) + "," + str(int(acc_rad[t].x)) + \
                             "," + str(int(plb_level[t].x))+ \
                             "," + str(int(supply_in[t].x))+","+str(int(supply_out[t].x))+"\n"
                    resultFile.write(theRow)



    except GRB.GurobiError:
        print(">>There are no feasible!!",GRB.GurobiError)
