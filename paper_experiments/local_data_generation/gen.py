# Input 1. radius (need to consider the whole scale of the problem)
# Input 2. random middle point
# Input 3. always middle point vs random(specific 
# points instead of all over the place). See if the O-D pairs are close to each other
# Input 4. wandering around or random
import pickle as pk
import sys
import os
import random
from scipy.stats import poisson

# Input Order
orderNum = sys.argv[1]

# range
GRIDRANGE = 20

# Step 1. read in all the reference point
with open(os.path.join('..','..','reference_coordinate'), 'rb') as f:
    reference_coordinate = pk.load(f)

# Step 2. randomly picked one
keys = list(reference_coordinate.keys())
chosen_key = random.choice(keys)

# Step 3. randomly pick a radius
# calculate the range of the map
lat_list = []
long_list = []
for key in reference_coordinate:
    lat_list.append(reference_coordinate[key][0])
    long_list.append(reference_coordinate[key][1])

width = (max(lat_list) - min(lat_list))/GRIDRANGE
height = (max(long_list) - min(long_list))/GRIDRANGE

width_bound = 0
height_bound = 0
while width_bound == 0 or height_bound == 0:
    width_bound = poisson.rvs(mu=8, size=1)[0]
    height_bound = poisson.rvs(mu=8, size=1)[0]

# Step 4. choose the possible points
candidate_reference = []
for key in reference_coordinate:
    if abs(reference_coordinate[key][0] - reference_coordinate[chosen_key][0]) < width * width_bound  \
        and abs(reference_coordinate[key][1] - reference_coordinate[chosen_key][1]) < height * height_bound:
        candidate_reference.append(key)


# Step 5. Create candidate for route generations 
candidate_string =''
count = 0
for c in candidate_reference:  
    if count != 0:
        candidate_string = candidate_string + ','
    candidate_string = candidate_string + '\'' + str(c) + '_1\'' 
    count += 1


with open('candidate_reference.gms' ,'w') as f:
    f.write("set originTest(nodes)/{}/;\n".format(candidate_string))
    f.write("set destTest(nodes)/{}/;\n".format(candidate_string))

# Random Lambda
lambdaVal = random.uniform(0,1)

# Run generation code in gams
os.system('gams generates_random_local_trajectories_neighbor_adjusted.gms --lambda={} --width={} --height={}'.format(lambdaVal, width_bound,height_bound))

os.system('mv trajectories_local.gdx local/user{}.gdx'.format(orderNum))

os.system('gdxdump local/user{}.gdx format=csv symb=roadChosenIntermediate output=local/user{}.csv'.format(orderNum,orderNum))





