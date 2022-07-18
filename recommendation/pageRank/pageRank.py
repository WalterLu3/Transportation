import networkx as nx

G = nx.DiGraph()


arcs = [("A","AB",{"weight": 0.2}),
        ("A","AE",{"weight": 0.8}),
        ("AB","BC",{"weight": 0.5}),
        ("AB","BF",{"weight": 0.5}),
        ("AE","EF",{"weight": 1}),
        ("BC","CD",{"weight": 1}),
        ("BF","FD",{"weight": 1}),
        ("EF","FD",{"weight": 1}),
        ("CD","D",{"weight": 1}),
        ("FD","D",{"weight": 1}),
        ("D","A",{"weight": 1})]

G.add_edges_from(arcs)

result = nx.pagerank(G,max_iter=100, tol=1e-06)
print(result)