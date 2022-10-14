# take the routes in gdx form and 

#from gdx import File
import csv
import sys
import os
import pandas as pd
import shapefile
import pickle
import folium

f = sys.argv[1]
orderNum = sys.argv[2]

## read in the route file
with open(f,'r') as f:
    read = csv.reader(f)
    content = list(read)

roads = []
for row in content[1:]:
    if row[0][0] != 'i':
        roads.append(int(row[0]))

roads = list(set(roads))

## read in the information needed to create graph

# read link data
road_file_path = os.path.join('..','..','road_file.csv')
road_file = pd.read_csv(road_file_path,names=["RDWY_LINK_ID","REF_SITE_FROM_ID","REF_SITE_TO_ID"])

# read road shape (shape file already converted using CRS in qgis)
shape_path = os.path.join("..",'..',"transportation_data","Middleton_Cross_Plains","Features","Middleton_Road_New.shp")
shape = shapefile.Reader(shape_path)

# read crash shape
crash_path = os.path.join("..",'..',"transportation_data","Middleton_Cross_Plains","Features","Crash_data_combined_2017_2020.shp")
crash = shapefile.Reader(crash_path)

# load reference point coordinate
reference_coordinate = None
reference_path = os.path.join("..",'..',"reference_coordinate")

with open(reference_path, 'rb') as f:
    reference_coordinate = pickle.load(f)

# create road shape dictionary
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

trajShape = []
for roadID in roads:
    trajShape += road_vector[roadID]


m = folium.Map(location=[43.0819, -89.5579])
for loc in trajShape:
    folium.PolyLine(loc,
                #color=rgb_to_hex(random.randint(1,256), random.randint(1,256), random.randint(1,256)),
                color='black',
                weight=1.5,
                opacity=0.8).add_to(m)
    
m.save("user{}.html".format(orderNum))



print(len(roads))