from torch_RGCN.models import EmbeddingNodeClassifier

import torch
import numpy as np
from tqdm import tqdm
import json

from KGs import KG

from sklearn.metrics import accuracy_score


#%%

mailing_list = "ietf-http-wg"
kg_name = f"KGs/{mailing_list}/intersectkg"
kg = KG.restore(kg_name)

num_nodes = len(kg.entities())
num_rels = len(kg.predicates())


with open(kg_name + ".ind2label.json") as handle:
    ind2cls = {int(i): c for i, c in json.load(handle).items()}



classes = torch.tensor([
           ind2cls[kg.entity2ind[e]] for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e])
        ], dtype=torch.long)


num_classes = (classes.max() + 1).item()
assert num_classes == len(set(ind2cls.values())),\
         f"Appar. some classes were not observed! {num_classes}, {set(ind2cls.values())}"


#%%



test = 0.9

#test_idx = np.random.choice(len(kg.translated), size=int(len(kg.translated)*test),
#                            replace=False)
#
#train_idx = np.asarray([i for i in range(len(kg.translated)) if not i in test_idx])
#
#
#train_T = [kg.translated[i] for i in train_idx]
#test_T = [kg.translated[i] for i in test_idx]





test_idx = np.random.choice(num_nodes, size=int(num_nodes*test),
                            replace=False)
train_idx = np.asarray([i for i in range(num_nodes) if not i in test_idx])


#%%

nc = EmbeddingNodeClassifier(kg.translated,
                    nnodes=num_nodes, 
                    nrel=num_rels, 
                    nclass=num_classes,
                    nemb=4)


optimiser = torch.optim.Adam(nc.parameters())
criterion = torch.nn.CrossEntropyLoss()
mean_pred_prob = lambda preds, true_inds: np.mean([row[c].item() for row, c in zip(preds, true_inds)])


train_preds = []
losses = []
train_metrics = {criterion:[], 
                accuracy_score:[],
                mean_pred_prob:[]}
eval_metrics = {criterion:[], 
                accuracy_score:[],
                mean_pred_prob:[]}

epochs = 500
eval_epochs = range(0, epochs, 10)


#%%



pbar = tqdm(range(epochs), desc=str(np.inf))
for epoch in pbar:
    nc.train()
    optimiser.zero_grad()
    
    preds = nc()[train_idx, :]
        
    loss = criterion(preds, classes[train_idx])
    pbar.set_description(str(round(loss.item(), 5)))
        
    loss.backward()
    optimiser.step()
        
    if epoch in eval_epochs:
        train_acc = accuracy_score(classes[train_idx], preds.argmax(1))
        train_mean_p_hat = mean_pred_prob(preds.softmax(0), classes[test_idx])

        train_metrics[criterion].append(loss.item())
        train_metrics[accuracy_score].append(train_acc)        
        train_metrics[mean_pred_prob].append(train_mean_p_hat)
        
        
        
        
        test_preds = nc()[test_idx, :]
        test_acc = accuracy_score(classes[test_idx], test_preds.argmax(1))
        mean_p_hat = mean_pred_prob(nc()[test_idx, :].softmax(0), classes[test_idx])
        test_xent = criterion(test_preds, classes[test_idx]).item()
        
        eval_metrics[criterion].append(test_xent)
        eval_metrics[accuracy_score].append(test_acc)
        eval_metrics[mean_pred_prob].append(mean_p_hat)
        
        
        

#%%
import seaborn as sns
import matplotlib.pyplot as plt

rng = list(range(len(eval_metrics[criterion])))
sns.scatterplot(rng, train_metrics[criterion], label="train")
sns.scatterplot(rng, eval_metrics[criterion], label="test")
plt.title(f"Loss: {criterion}")
plt.show()


sns.scatterplot(rng, train_metrics[accuracy_score], label="train")
sns.scatterplot(rng, eval_metrics[accuracy_score], label="test")
plt.title(f"Accuracy")
plt.show()


sns.scatterplot(rng, train_metrics[mean_pred_prob], label="train")
sns.scatterplot(rng, eval_metrics[mean_pred_prob], label="test")
plt.title(f"Mean Predicted Probability of True Label")
plt.ylim((0.0, 0.001))
plt.show()




#%%

embeddings = nc.node_embeddings.detach().numpy()

with open("embeddings.tsv", "w") as handle:
    for v in embeddings:
        handle.write("\t".join(map(str, v)))
        handle.write("\n")



from declarations.entities import Person


#with open(kg_name + ".label2entity.json") as handle:
#    cls2entity = {int(i): s for i, s in json.load(handle).items()}


with open("meta.tsv", "w") as handle:
    handle.write("is_person\tnode_class\tinstance_label\n")
    for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e]):
        is_person = type(e) is Person
        node_class = ind2cls[kg.entity2ind[e]]
        
#        o = cls2entity[node_class]

#        o = e.organisation.instance_label if is_person else "None"
        l = e.instance_label if is_person else str(e)
        
        l = l.replace("\n", " ")
        
        handle.write("\t".join((str(is_person), str(node_class), l)))
        handle.write("\n")

