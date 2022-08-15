# cluster and yen's

import numpy as np
import matplotlib.pyplot as plt
import pickle
import csv
import networkx as nx
import scipy.stats as stats
import math

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

globalNumber = 500
clusterNumber = 3
writeFileName = 'three_clusters.pk'

# input cost vector to be visualzed
with open("../global_cost_vectors_500_lRand.pk",'rb') as f:
    global_cost = pickle.load(f)

# input trips detail
with open("../global_trips_500_lRand.pk",'rb') as f:
    global_dict = pickle.load(f)

# with open("global_trips.pk",'rb') as f:
#     global_dict = pickle.load(f)
with open("../local_cost_vectors.pk",'rb') as f:
    local_cost = pickle.load(f)

# read trip number from the dataset
globalNumber = len(global_cost.keys())

#clusterNumber = 5
########################################################
############## Normalization of global cost ############
########################################################
global_cost_list = []
time_list = []
risk_list = []

for k in global_cost:
    time_list.append(global_cost[k][0][0])
    risk_list.append(global_cost[k][0][1])
    
avgTime = np.mean(time_list)
stdTime = np.std(time_list)
avgRisk = np.mean(risk_list)
stdRisk = np.std(risk_list)

# normalized point
global_time_normalized = []
global_risk_normalized = []
for k in global_cost:
    temp = ((global_cost[k][0][0]-avgTime)/stdTime, (global_cost[k][0][1]-avgRisk)/stdRisk)
    global_time_normalized.append((global_cost[k][0][0]-avgTime)/stdTime)
    global_risk_normalized.append((global_cost[k][0][1]-avgRisk)/stdRisk)
    global_cost_list.append(temp)

# plot out the global result
plt.scatter(global_time_normalized, global_risk_normalized)
# 100 linearly spaced numbers
x = np.linspace(-0.9,5,100)
# the function, which is y = x^2 here
y = 1/(x+1)**2 -1.4
#y = 1/(x+1.2)**2 -1.6
plt.ylim([-2, 2])
plt.xlim([-1, 5])
plt.plot(x,y, 'r')
#plt.show()


#filtered out the Pareto optimal points

def func(x,y):
    return 1/(x+1)**2 -1.4 -y
greenX = []
greenY = []
global_cost_list = []
greenLoop = [] # stores the loop number

blueX = []
blueY =[]
for i in range(len(global_time_normalized)):
    if func(global_time_normalized[i],global_risk_normalized[i]) >= 0:
        greenX.append(global_time_normalized[i])
        greenY.append(global_risk_normalized[i])
        global_cost_list.append((global_time_normalized[i],global_risk_normalized[i]))
        greenLoop.append(i+1)
    else:
        blueX.append(global_time_normalized[i])
        blueY.append(global_risk_normalized[i])
        
# plot out pareto optimal point
plt.scatter(blueX, blueY,c ='b')
plt.scatter(greenX, greenY,c ='g')
# 100 linearly spaced numbers
x = np.linspace(-0.9,5,100)
# the function, which is y = x^2 here
y = 1/(x+1)**2 -1.4
plt.ylim([-2, 2])
plt.xlim([-1, 5])
plt.plot(x,y, 'r')
#plt.show()


########################################################
############## Normalization of local cost #############
########################################################

local_cost_list = []
time_list = []
risk_list = []

for k in local_cost:
    time_list.append(local_cost[k][0][0])
    risk_list.append(local_cost[k][0][1])
    
avgTime = np.mean(time_list)
stdTime = np.std(time_list)
avgRisk = np.mean(risk_list)
stdRisk = np.std(risk_list)
# normalized point
local_time_normalized = []
local_risk_normalized = []
for k in local_cost:
    temp = ((global_cost[k][0][0]-avgTime)/stdTime, (global_cost[k][0][1]-avgRisk)/stdRisk)
    local_time_normalized.append((local_cost[k][0][0]-avgTime)/stdTime)
    local_risk_normalized.append((local_cost[k][0][1]-avgRisk)/stdRisk)
    local_cost_list.append(temp)


########################################################
############## Calculation of cost ratio ###############
########################################################

# global ratio
global_ratio_list = []
ratio_list = []

for k in global_cost:
    ratio_list.append((global_cost[k][0][0]/global_cost[k][0][1]))
    
avgRatio = np.mean(ratio_list)
stdRatio = np.std(ratio_list)

# normalized point
global_Ratio_normalized = []
for e in ratio_list:
    global_ratio_list.append((e-avgRatio)/stdRatio)



# local ratio
local_ratio_list = []
ratio_list = []

for k in local_cost:
    ratio_list.append((local_cost[k][0][0]/local_cost[k][0][1]))
    
avgRatio = np.mean(ratio_list)
stdRatio = np.std(ratio_list)

# normalized point
local_Ratio_normalized = []
for e in ratio_list:
    local_ratio_list.append((e-avgRatio)/stdRatio)



#################################
### find suitable cluster num ###
#################################

# plot silouette score
points = global_cost_list
sil = []
kmax = 10

# dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
for k in range(2, kmax+1):
    kmeans = KMeans(
            init="random",
            n_clusters=k,
            n_init=10,
            max_iter=300,
            random_state=43
        )

    kmeans.fit(points)
    labels = kmeans.labels_
    sil.append(silhouette_score(points, labels, metric = 'euclidean'))

plt.plot(range(2, kmax+1), sil)
#plt.show()

# Plotting out the clusters

kmeans = KMeans(
    init="random",
    n_clusters=3,
    n_init=2,
    max_iter=300,
    random_state=10
)

kmeans.fit(global_cost_list)
color_labels = kmeans.labels_

color = [(0.5,0.5,0.5),(1,0,0),(0,1,0),(0,0,1),(0,0,0)]
color_list = []
for ind in range(len(greenX)):
    color_list.append(color[color_labels[ind]])
    
plt.scatter(greenX, greenY,c=color_list)
#plt.show()



#####################################################
############### Find path for each cluster###########
#####################################################

#### read road data
idToRoad =  []
with open("../../turning_network_linkID_updated.csv",'r') as f:
    idToRoad = csv.reader(f)
    idToRoad = list(idToRoad)
    
idToRoadDict = {}
roadToIdDict ={}
for element in idToRoad:
    idToRoadDict[element[0]] = (element[1],element[2])
    if "intersection" not in element[0]:
        roadToIdDict[element[1].split('_')[0],element[2].split('_')[0]] = element[0]

# get trip routes
global_trip_grouped = {}
for i in range(clusterNumber):
    global_trip_grouped[i] = []
    
for i in range(len(greenLoop)):
    key = "l" + str(greenLoop[i])
    global_trip_grouped[color_labels[i]].append(global_dict[key])

def pageRank(trips, origin = '1666494', destination = '1662728'): # input a bunch of trips, return a recommendation for route
    dualArcs = {} # store the arcs for dual graph
    originalG = nx.DiGraph()
    #print(len(trips))
    for t in trips:
        subG = nx.DiGraph()
        arcList = []
        for road in t:
            startNode = idToRoadDict[str(road)][0].split('_')[0]
            endNode = idToRoadDict[str(road)][1].split('_')[0]
            arcList.append((startNode,endNode))
        subG.add_edges_from(arcList)
        
        # find the path to be added to construct dual graph
        path = nx.shortest_path(subG, origin, destination)
        
        for ind in range(len(path)-2):
            #print((path[ind],path[ind + 1]))
            originalG.add_edges_from([(path[ind],path[ind + 1])])
            current_arc = path[ind]+'_to_'+path[ind + 1]
            next_arc = path[ind + 1]+'_to_'+path[ind + 2]
            if ind == 0:
                if not (path[0] in dualArcs):
                    dualArcs[path[0]] = {current_arc : 1}
                else:
                    if not(current_arc in dualArcs[path[0]]):
                        dualArcs[path[0]][current_arc] = 1
                    else:
                        dualArcs[path[0]][current_arc] += 1
            
            if not (current_arc in dualArcs):
                dualArcs[current_arc] = {next_arc : 1}
            else:
                if not (next_arc in dualArcs[current_arc]):
                    dualArcs[current_arc][next_arc] = 1
                else:
                    dualArcs[current_arc][next_arc] += 1

        last_arc = path[-2]+'_to_'+path[-1]
        originalG.add_edges_from([(path[-2],path[-1])])
        if not (last_arc in dualArcs):
                dualArcs[last_arc] = {path[-1] : 1}
        else:
            if not (path[-1] in dualArcs[last_arc]):
                dualArcs[last_arc][path[-1]] = 1
            else:
                dualArcs[last_arc][path[-1]] += 1
                
    for key in dualArcs:
        sumCount = 0
        for key2 in dualArcs[key]:
            sumCount += dualArcs[key][key2]
            
        for key2 in dualArcs[key]:
            dualArcs[key][key2] /= sumCount
        
    dualG = nx.DiGraph()
    
    dualArcList = []
    for key in dualArcs:
        for key2 in dualArcs[key]:
            dualArcList.append((key,key2,{'weight':dualArcs[key][key2]}))
            
    dualG.add_edges_from(dualArcList)
    dualG.add_edges_from([(destination,origin,{'weight':1})])
    #record pageRank result
    result = nx.pagerank(dualG, weight='weight', alpha=0.9)
    
    weightNode = {}
    for k in result:
        if '_to_' in k:
            startNode = k.split('_to_')[0]
            endNode = k.split('_to_')[1]
            #print(startNode,endNode)
            originalG[startNode][endNode]['weight'] = np.log(1/result[k])
            weightNode[(startNode,endNode)] = np.log(1/result[k])
    def returnWeight(start,end,weight):
        
        return weight['weight']
            
    optimalPath = nx.shortest_path(originalG,source=origin,target=destination,weight=returnWeight)
    #kPaths = list(nx.shortest_simple_paths(originalG, source=origin, target=destination, weight=returnWeight ))
    #print(originalG['1666494'])
    # return adj for top k paths
    adj = {}
    for i,j in originalG.edges:
        adj[i,j] = originalG[i][j]['weight']

    return optimalPath, adj

group_optimal_path = []
for g in range(clusterNumber):
    optimal_path, adj = pageRank(global_trip_grouped[g])
    group_optimal_path.append(pageRank(global_trip_grouped[g]))

    with open('topK_' + str(g),'wb') as f:
        pickle.dump(adj,f)

with open(writeFileName, 'wb') as f:
    pickle.dump(group_optimal_path,f)

#### KL - Divergence compare####
def KLDivergence(mean1,std1,mean2,std2):
    
    return np.log(std2/std1) + (std1**2 + (mean1-mean2)**2)/(2*std2**2) - 1/2
# global distriubtion
ratioDict = {}
for g in range(clusterNumber):
    ratioDict[g] = []
    
for idx in range(len(greenLoop)):
    k = 'l' + str(greenLoop[idx])
    ratioDict[kmeans.labels_[idx]].append(global_cost[k][0][0]/global_cost[k][0][1]) 

normalDistribution = {}

for g in range(clusterNumber):
    normalDistribution[g] =  {'mean': np.mean(ratioDict[g]) , 'std':np.std(ratioDict[g]) }

#local distribution

ratioLocal = []
    
for idx in range(1,51):
    k = 'l'+str(idx)
    ratioLocal.append(local_cost[k][0][0]/local_cost[k][0][1])

for g in range(clusterNumber):
    print('KL(group{},user) : {}'.format(g, KLDivergence(np.mean(ratioLocal),
                                                         np.std(ratioLocal), 
                                                         normalDistribution[g]['mean'], 
                                                         normalDistribution[g]['std'])
                                        ))