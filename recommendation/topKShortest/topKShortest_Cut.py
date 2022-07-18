import networkx as nx
import gurobipy as gp
from gurobipy import GRB
G = nx.DiGraph()

# adding directed edges inferred from the example (NetworkX adds nodes automatically)
arcs = [("C","D",{"weight": 3}),
        ("D","F",{"weight": 4}),
        ("F","H",{"weight": 1}),
        ("C","E",{"weight": 2}),
        ("E","D",{"weight": 1}),
        ("E","F",{"weight": 2}),
        ("E","G",{"weight": 3}),
        ("G","H",{"weight": 2}),
        ("F","G",{"weight": 2})]

weights = {}

for a in arcs:
    weights[a[0],a[1]] = a[2]["weight"]


G.add_edges_from(arcs)

# defining the model and variables
m = gp.Model()
x = gp.tupledict()
for (v1, v2) in G.edges:
    x[v1, v2] = m.addVar(vtype="B", name="edge_"+v1+v2)

obj = gp.quicksum( weights[v1,v2] * x[v1,v2]  
                    for (v1, v2) in G.edges )

# set objectives
m.setObjective(obj,GRB.MINIMIZE)

for v in G.nodes:
    # we need to skip the source (0) and the sink (7)
    if v not in ["C","H"]:
        # we collect the predecessor variables
        expr1 = gp.quicksum(x[i,v] for i in G.predecessors(v))
        
        # we collect the successor variables 
        expr2 = gp.quicksum(x[v, j] for j in G.successors(v))
        
        # we add the constraint
        m.addLConstr(expr1 - expr2 == 0)
    elif v == "C":
        # we collect the predecessor variables
        expr1 = gp.quicksum(x[i,v] for i in G.predecessors(v))
        
        # we collect the successor variables 
        expr2 = gp.quicksum(x[v, j] for j in G.successors(v))
        
        # we add the constraint
        m.addLConstr(expr2 - expr1 == 1)
    elif v == "H":
        # we collect the predecessor variables
        expr1 = gp.quicksum(x[i,v] for i in G.predecessors(v))
        
        # we collect the successor variables 
        expr2 = gp.quicksum(x[v, j] for j in G.successors(v))
        
        # we add the constraint
        m.addLConstr(expr2 - expr1 == -1)

result = []
for k in range(7):
    m.optimize()
    temp = []
    check_solution = {}
    total_sum = 0
    total_distance = 0
    for (v1, v2) in G.edges:
        if x[v1,v2].x > 0.5:
            check_solution[v1,v2] = 1
            total_sum += 1
            total_distance += weights[v1,v2]
            temp.append("{}_{}".format(v1,v2))
            #print("{}_{}".format(v1,v2))
        else:
            check_solution[v1,v2] = 0
    temp.append(total_distance)
    result.append(temp)
    expr = gp.quicksum(x[v1, v2] * check_solution[v1,v2] for (v1, v2) in G.edges)
    m.addLConstr(expr <= total_sum - 0.5)
    print("-----------------")


print(result)