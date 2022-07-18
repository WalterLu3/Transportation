import networkx as nx

G = nx.DiGraph()


arcs = [("C","D",{"weight": 3}),
        ("D","F",{"weight": 4}),
        ("F","H",{"weight": 1}),
        ("C","E",{"weight": 2}),
        ("E","D",{"weight": 1}),
        ("E","F",{"weight": 2}),
        ("E","G",{"weight": 3}),
        ("G","H",{"weight": 2}),
        ("F","G",{"weight": 2})]

G.add_edges_from(arcs)

X = nx.shortest_simple_paths(G, "C", "H",weight = "weight")
k = 5
for counter, path in enumerate(X):
     print(path)
     if counter == k-1:
         break


