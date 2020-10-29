# -*- coding: utf-8 -*-

import numpy as np

import networkx as nx

from KGs import KG, Person
import matplotlib.pyplot as plt


import json

#%%

def load_and_get_data(kg_path, heuristic_name):
    kg = KG.restore(kg_path)

    num_nodes = len(kg.entities())
    num_rels = len(kg.predicates())

    with open(kg_path + f".{heuristic_name}.ind2label.json") as handle:
        ind2cls = {int(i): c for i, c in json.load(handle).items()}

    classes = np.asarray([
                ind2cls[kg.entity2ind[e]] for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e])
            ])


    num_classes = (classes.max() + 1).item()
    assert num_classes == len(set(ind2cls.values())),\
                 f"Appar. some classes were not observed! {num_classes}, {set(ind2cls.values())}"
                 
    return kg, classes, num_nodes, num_rels, num_classes


kg_name = "KGs/ietf-http-wg/textkg"
heuristic = "ConfirmedPerson"


kg, classes, num_nodes, num_rels, num_classes = load_and_get_data(kg_name, heuristic)

#%%

G = nx.DiGraph()
G.add_edges_from(kg.tuples())

adj_mat = nx.adjacency_matrix(G)



#%%
#
#G_multi = nx.MultiDiGraph()
#
#for s, p, o in kg.triples:
#    G_multi.add_edge(s, o, key=p)
#
#multi_adj_mat = nx.adjacency_matrix(G_multi)

#%%

m = np.zeros((num_nodes, num_nodes, num_rels))

for s, p, o in kg.triples:
    s_i, o_i = kg.entity2ind[s], kg.entity2ind[o]
    p_i = kg.pred2ind[p]
    m[s_i, o_i, p_i] = 1
    

#%%
    
from sklearn.semi_supervised import LabelPropagation


X = m.sum(-1)
y = classes

lp = LabelPropagation()
lp.fit(X, y)
    
    


#%%
G = nx.MultiDiGraph()
G.add_nodes_from([1,2,3])

for u, v, e in [(1,2, "a"), (1,2, "a"), (1,3, "a")]:
    G.add_edge(u, v)

#G.add_edges_from([(1,2,dict(key="a"))])
#G.add_edges_from([(1,2,dict(key="b"))])
#G.add_edges_from([(1,3,dict(key="b"))])
nx.draw(G)
nx.draw_networkx_edge_labels(G, pos=nx.spring_layout(G))



#%%


from sklearn.decomposition import NMF


X = adj_mat[:1000, :1000].toarray()



NMF()




#%%







