import os
import csv

dataNum = 500
users = []
for i in range(dataNum):
    temp = [i] # store the data
    # get height
    for attribute in ['height','width','lambda']:
        os.system("gdxdump user{}.gdx format=csv symb={} output=tempOut.csv".format(i,attribute))
        with open("tempOut.csv", 'r') as f:
            reader = list(csv.reader(f))  
            temp.append(float(reader[1][0]))
    users.append(temp)

with open("users.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerows(users)




trips = {}
tripsTable = []
for i in range(dataNum):
    for attribute in ['originLoop','destinationLoop','outDistance','outRisk']:
        os.system("gdxdump user{}.gdx format=csv symb={} output=tempOut.csv".format(i,attribute))
        with open("tempOut.csv", 'r') as f:
            reader = list(csv.reader(f))[1:]
            for element in reader:
                if element[0] not in trips:
                    trips[element[0]] = {}
                trips[element[0]][attribute] = element[1]
    for k in trips:
        tempTrips = [str('u{}_'.format(i)) + k]
        for k2 in ['originLoop','destinationLoop','outDistance','outRisk']:
            tempTrips.append(trips[k][k2])
        tempTrips.append(i)
        tripsTable.append(tempTrips)

with open("trips.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerows(tripsTable)

roads = set()
tripRoads = []
for i in range(dataNum):
    with open("user{}.csv".format(i), 'r') as f:
        reader = list(csv.reader(f))[1:]
        for element in reader:
            if element[0][0] != 'i':
                roads.add(element[0])
                tripRoads.append([str('u{}_'.format(i)) + element[1],element[0]])

with open("tripRoads.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerows(tripRoads)

roadsTable = []
for element in roads:
    roadsTable.append([element,element])

with open("roads.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerows(roadsTable)


