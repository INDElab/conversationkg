# -*- coding: utf-8 -*-

from torch_RGCN.models import EmbeddingNodeClassifier

import torch
import numpy as np
from tqdm import tqdm
import json

from KGs import KG

kg_name = "KGs/intersectkg"
kg = KG.restore(kg_name)


num_nodes = max(kg.entity2ind.values()) + 1
num_rels = max(kg.pred2ind.values()) + 1

with open(kg_name + ".ind2class.json") as handle:
    ind2cls = {int(i): c for i, c in json.load(handle).items()}
    

# FIX KeyErrors!!
labels = [ind2cls[i] if i in ind2cls else 0 for i in kg.entity2ind.values()]



#labels = [ind2cls[i] if i in ind2measure else 0
#            for i in kg.entity2ind.values()
#        ]


classes = torch.tensor(labels,
                       dtype=torch.long)

#%%

num_classes = 4

nc = EmbeddingNodeClassifier(kg.translated, 
                    nnodes=num_nodes, 
                    nrel=num_rels, 
                    nclass=num_classes,
                    nemb=4)


#%%

optimiser = torch.optim.Adam(nc.parameters())

pbar = tqdm(range(500), desc=str(np.inf))
for epoch in pbar:
    criterion = torch.nn.CrossEntropyLoss()
    nc.train()
    optimiser.zero_grad()

    preds = nc()[:, :]
    loss = criterion(preds, classes)
    pbar.set_description(str(round(loss.item(), 5)))
    

    loss.backward()
    optimiser.step()
    
print(classes)
print(nc().argmax(1))
#print(nc())

#for n in range(num_nodes):
#    print(nc.node_embeddings[n, :])
#    
#    print("\n\n")
#    
    
#embeddings = nc.node_embeddings.detach().numpy()
#
#with open("embeddings.tsv", "w") as handle:
#    for v in embeddings:
#        handle.write("\t".join(map(str, v)))
#        handle.write("\n")
