# -*- coding: utf-8 -*-

import networkx as nx

from KGs import KG


kg_path = "KGs/public-credentials/textkg"
kg = KG.restore(kg_path)


G = nx.DiGraph()
G.add_edges_from(kg.tuples())



#%%

adj_mat 


#%%


from sklearn.decomposition import NMF


X = 