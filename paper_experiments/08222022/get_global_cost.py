# import needed packages

#import folium
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import shapefile
import pickle
import random
import networkx as nx
import sys


# import trajectories

global_file = sys.argv[1]

print(global_file[3:].split('.')[0]+'_cost.pk')
#sys.exit(0)
#trajectoryNum = 500


Global_T= None
with open(global_file,'r') as f:
    reader = csv.reader(f)
    Global_T = list(reader)

Global_T = Global_T[1:] # remove row names

# Local_T = None
# with open(local_file,'r') as f:
#     reader = csv.reader(f)
#     Local_T = list(reader)

# Local_T = Local_T[1:] # remove row names
######### information for turns ##########
turn_list = []
with open("../../turning_network_linkID_updated.csv",'r') as f:
    reader = csv.reader(f)
    turn_list = list(reader)
    
isTurn = []
with open("../../turning_network_turn_updated.csv",'r') as f:
    reader = csv.reader(f)
    isTurn = list(reader)
    
isTurnDict = {}
for turn in isTurn:
    isTurnDict[(turn[0],turn[1])] = int(turn[2])
    
road_ID_with_turn = {}
for element in turn_list:
    road_ID_with_turn[element[0]] = (element[1],element[2])
    
def calculateTurn(trip):
    total_turn = 0
    for i in trip:
        total_turn += isTurnDict[road_ID_with_turn[i]]
    return total_turn
######### information for turns end ##########


######### information for calculating time ##########
time_list = []
with open("../../turning_network_time_updated.csv",'r') as f:
    time_list = csv.reader(f)
    time_list = list(time_list)

timeDict = {}
for element in time_list:
    timeDict[(element[0],element[1])] = (float(element[2])-1)*99
    
def calculateTime(trip): # trip needs to contain intersections
    total_time = 0
    for i in trip:
        total_time += timeDict[road_ID_with_turn[i]]
    return total_time
######### information for calculating time ends ##########

######### information for calculating distance ##########
distance_list = []
with open("../../link_file.csv",'r') as f:
    distance_list = csv.reader(f)
    distance_list = list(distance_list)
    
distance_dict = {}
for element in distance_list:
    distance_dict[(element[0],element[1])] = int(element[2])
    
idToRoad =  []
with open("../../road_file.csv",'r') as f:
    idToRoad = csv.reader(f)
    idToRoad = list(idToRoad)
    
idToRoadDict = {}
for element in idToRoad:
    idToRoadDict[element[0]] = (element[1],element[2])
        

def calculateDist(trip):
    total_distance = 0
    for i in trip:
        if i in idToRoadDict:
            total_distance += distance_dict[idToRoadDict[i]]
    return total_distance   
######### information for calculating distance ends##########

######### information for calculating risk ##########
risk_list = None
with open("../../crash_drisk0320.csv",'r') as f:
    risk_list = csv.reader(f)
    risk_list = list(risk_list)
    
riskDict = {}
for element in risk_list:
    riskDict[(element[0],element[1])] = float(element[2])
    
def calculateRisk(trip):
    total_risk = 0
    for i in trip:
        total_risk += riskDict[road_ID_with_turn[i]]
    return total_risk

######### information for calculating risk ends ##########

######### Data Generation ##########
def trajectoryDataGenerator(trajectoryList,numberT): ## input 1. trajectory list for different routes 2. number of different routes
    trajectoryNum = numberT
    
    trajNames = [] #stores loop Name
    trajDict = {} # sotres the route without intersection
    trajDictShape = {} # stores the roads shape for plotting
    trajDict_w_intersection = {} # store the routes with intersection
    
    for i in range(trajectoryNum):
        s = 'l' + str(i+1)
        trajNames.append(s)
        trajDict[s] = []
        trajDictShape[s] = []
        trajDict_w_intersection[s] = [] 
        
    for r in trajectoryList:
        if 'intersection' not in r[0]:
            trajDict[r[1]].append(int(r[0]))
        trajDict_w_intersection[r[1]].append(r[0])
    
    return trajDict, trajDict_w_intersection 
######### Data Generation ends##########
######### Calculate Cost##########
def costVector(trajDictInterSect):
    costDict = {}
    for k in trajDictInterSect:
        temp =  []
        temp.append([calculateTime(trajDictInterSect[k]),calculateRisk(trajDictInterSect[k]),
                    calculateDist(trajDictInterSect[k]),calculateTurn(trajDictInterSect[k])])
        costDict[k] = temp
    return costDict
# construct cost dictionary

#def trajectoryCostGenerator(trajDictInterSect):



GlobalData,GlobalDataIntersect =  trajectoryDataGenerator(Global_T,500)
#LocalData,LocalDataIntersect = trajectoryDataGenerator(Local_T,50)

global_cost = costVector(GlobalDataIntersect)
#local_cost = costVector(LocalDataIntersect)
#print(len(GlobalData['l1']))
# store the cost vectors

# with open("global_cost_vectors_500.pk",'wb') as f:
#     pickle.dump(global_cost,f)
# with open("local_cost_vectors.pk",'wb') as f:
#     pickle.dump(local_cost,f)
# with open("global_trips_500.pk",'wb') as f:
#     pickle.dump(GlobalData,f)
# with open("local_trips.pk",'wb') as f:
#     pickle.dump(LocalData,f)   
# with open("global_cost_vectors_500_lRand.pk",'wb') as f:
#     pickle.dump(global_cost,f)

# with open("global_trips_500_lRand.pk",'wb') as f:
#     pickle.dump(GlobalData,f)

# with open(local_file[3:].split('.')[0]+'_cost.pk','wb') as f:
#     pickle.dump(local_cost,f)

# with open(local_file[3:].split('.')[0]+'_route.pk','wb') as f:
#     pickle.dump(LocalDataIntersect,f)
global_file[3:].split('.')[0]+'_cost.pk'



with open(global_file[3:].split('.')[0]+'_cost.pk','wb') as f:
    pickle.dump(global_cost,f)

with open(global_file[3:].split('.')[0]+'_route.pk','wb') as f:
    pickle.dump(GlobalData,f)