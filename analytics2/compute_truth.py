from tqdm import tqdm
import json

import matplotlib.pyplot as plt

import networkx

from declarations.corpus import Conversation
from declarations.emails import Email
from declarations.entities import Person, Organisation


import importlib
corpus_ = importlib.import_module("declarations.corpus")
emails_ = importlib.import_module("declarations.emails")
entities_ = importlib.import_module("declarations.entities")

with open("triples_inds.json") as handle:
    triples = json.load(handle)
    
    triples = [()]
    
    
#%%
    
G = networkx.DiGraph()

tuples = [(s, o) for s, p, o in triples]

G.add_edges_from(tuples)

nodes, vals = list(zip(*networkx.algorithms.betweenness_centrality(G).items()))

