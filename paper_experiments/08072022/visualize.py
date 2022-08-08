import folium
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shapefile
import pickle
import random
#import gams_magic
import networkx as nx

def rgb_to_hex(r, g, b):
    return ('#{:X}{:X}{:X}').format(r, g, b)

pathFile = 'three_clusters.pk'

# read link data
road_file_path = os.path.join('..','..','road_file.csv')
road_file = pd.read_csv(road_file_path,names=["RDWY_LINK_ID","REF_SITE_FROM_ID","REF_SITE_TO_ID"])

# read road shape (shape file already converted using CRS in qgis)
shape_path = os.path.join('..',"..","transportation_data","Middleton_Cross_Plains","Features","Middleton_Road_New.shp")
shape = shapefile.Reader(shape_path)

# read crash shape
crash_path = os.path.join('..',"..","transportation_data","Middleton_Cross_Plains","Features","Crash_data_combined_2017_2020.shp")
crash = shapefile.Reader(crash_path)

# load reference point coordinate
reference_coordinate = None
reference_path = os.path.join('..',"..","reference_coordinate")


############# create road shape dictionary ############
road_vector = {}
for sp in shape.shapeRecords():
    # different road shape can share the same road id
    road_id = sp.record[43]
    

    x = [i[0] for i in sp.shape.points[:]]
    y = [i[1] for i in sp.shape.points[:]]
    
    segment = []
    for i in range(len(x)):
        segment.append((y[i],x[i]))
        
    if road_id in road_vector:
        road_vector[road_id].append(segment)
    else:
        road_vector[road_id] = [segment]


with open(reference_path, 'rb') as f:
    reference_coordinate = pickle.load(f)

# change id to road
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

with open(pathFile, 'rb') as f:
    group_optimal_path = pickle.load(f)

clusterNum = len(group_optimal_path)

optimal_roadIdList = []
for g in range(clusterNum):
    example_coordinate = []
    for ind in range(len(group_optimal_path[g])-1):
            #print((example_trip[ind],example_trip[ind+1]))
            example_coordinate += road_vector[int(roadToIdDict[group_optimal_path[g][ind],group_optimal_path[g][ind+1]])]    
    optimal_roadIdList.append(example_coordinate)

## plot out the optimal path and save it
colors = [rgb_to_hex(128, 128, 128),'red','green','blue','black']
for g in range(clusterNum):
    m = folium.Map(location=[43.0819, -89.5579])
    for loc in optimal_roadIdList[g]:
        folium.PolyLine(loc,
                    #color=rgb_to_hex(random.randint(1,256), random.randint(1,256), random.randint(1,256)),
                    color=colors[g],
                    weight=5.5-1*g,
                    opacity=0.8).add_to(m)

    
    m.save("three_clusters_optimal_visualization_{}.html".format(g))
