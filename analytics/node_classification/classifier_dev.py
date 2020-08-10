from torch_RGCN2.models import NodeClassifier, EmbeddingNodeClassifier
from torch_RGCN2.data import load_node_classification_data

import torch
import numpy as np
from tqdm import tqdm

#triples, (n2i, i2n), (r2i, i2r), train, test = load_node_classification_data(
#        'aifb', use_test_set=False, prune=False)
#
#print(train)
#
#exit(13)


##classes = set([int(l) for l in test_lbl] + [int(l) for l in train_lbl])
#num_classes = 2 # len(classes)
#num_nodes = len(n2i)
#num_relations = len(r2i)
#
#
#
#ss, pp, oo = list(zip(*triples))
#
#print(len(triples))
#print(len(set(ss)), num_nodes)
#print(len(set(oo)), num_nodes)
#print(len(set(ss).union(oo)), num_nodes)
#print(len(set(pp)), num_relations)
#
#print(min(ss), max(ss))
#print(min(oo), max(oo))
#print(min(pp), max(pp))



triples = [[0, 0, 1], 
           [0, 0, 2]]

n_samples = 1000
num_nodes = 100
num_rels = 50
num_classes = 10

#nodes = np.arange(num_nodes)
#rels = np.arange(num_rels)

triples = [(s, p, o) for s, p, o in 
           zip(np.random.choice(num_nodes, size=n_samples),
               np.random.choice(num_rels, size=n_samples),
               np.random.choice(num_nodes, size=n_samples))]


ss, pp, oo = list(zip(*triples))

print(len(set(ss)))
print(len(set(pp)))
print(len(set(oo)))


classes = torch.tensor(np.random.choice(num_classes, size=num_nodes),
                       dtype=torch.long)


nc = EmbeddingNodeClassifier(triples, 
                    nnodes=num_nodes, 
                    nrel=num_rels, 
                    nclass=num_classes,
                    nemb=4)


optimiser = torch.optim.Adam(nc.parameters())

pbar = tqdm(range(10000), desc=str(np.inf))
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
print(nc())

for n in range(num_nodes):
    print(nc.node_embeddings[n, :])
    
    print("\n\n")
    
    
embeddings = nc.node_embeddings.detach().numpy()

with open("embeddings.tsv", "w") as handle:
    for v in embeddings:
        handle.write("\t".join(map(str, v)))
        handle.write("\n")

