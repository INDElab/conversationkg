# -*- coding: utf-8 -*-

from declarations.entities import Person
from KGs import KG, EmailKG

import networkx
from sklearn.cluster import KMeans

import numpy as np
import json


#load graphs 

folder_name = "KGs"

emailkg = EmailKG.restore(folder_name + "/emailkg")


#textkg2 = TextKG.restore("KGs/textkg")


intersect_name = folder_name + "/intersectkg"
intersectkg = KG.restore(intersect_name)




# instantiate a networkx Graph

G = networkx.DiGraph()
G.add_edges_from(emailkg.tuples())


#%% compute graph algorithm 

graph_f = networkx.algorithms.cluster.clustering


print(f"computing {graph_f}...", end="\t")
value_mapping = graph_f(G)
print("done")


entity2value = {n: (v if type(n) is Person else -1)
                    for n, v in value_mapping.items()}

entities, values = list(zip(*entity2value.items()))


# KMeans clustering on the nodes' computed values

km = KMeans(n_clusters=4)
km.fit(np.reshape(values, (-1, 1)))

entity2class = {e:cl for e, cl in zip(entities, km.labels_)}


ind2value = {intersectkg.entity2ind[e]:float(v) for e, v in entity2value.items()}
ind2class = {intersectkg.entity2ind[e]:int(cl) for e, cl in entity2class.items()}


#%% save mappings



with open(intersect_name + ".ind2measure.json", "w") as handle:
    json.dump(ind2value, handle)
    

with open(intersect_name + ".ind2class.json", "w") as handle:
    json.dump(ind2class, handle)
    
    
  
    
