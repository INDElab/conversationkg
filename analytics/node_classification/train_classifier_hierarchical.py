from torch_RGCN.models import EmbeddingNodeClassifier

import torch
import numpy as np
from tqdm import tqdm
import json

from KGs import KG

from sklearn.metrics import accuracy_score, confusion_matrix


#%%

mailing_list = "ietf-http-wg"
kg_name = f"KGs/{mailing_list}/intersectkg"
kg = KG.restore(kg_name)

num_nodes = len(kg.entities())
num_rels = len(kg.predicates())


with open(kg_name + ".RolesfromGraphMeasure.ind2label.json") as handle:
    ind2cls = {int(i): c for i, c in json.load(handle).items()}



classes = torch.tensor([
           ind2cls[kg.entity2ind[e]] for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e])
        ], dtype=torch.long)


num_classes = (classes.max() + 1).item()
assert num_classes == len(set(ind2cls.values())),\
         f"Appar. some classes were not observed! {num_classes}, {set(ind2cls.values())}"


#%%
         
is_person = (classes < num_classes -2).long()

person_test = 0.9

person_test_idx = np.random.choice(num_nodes, size=int(num_nodes*person_test),
                            replace=False)
person_train_idx = np.asarray([i for i in range(num_nodes) if not i in person_test_idx])



#%%

person_nc, optimiser = setup_classifier(nclass=2)

criterion, person_train_metrics, person_eval_metrics = train_classifier(

        person_nc, is_person, person_train_idx, person_test_idx, 500, 10
        
        )


#%%

real_classes_idx = np.where(classes < num_classes-2)[0]

real_classes_test = 0.5

real_classes_test_idx = np.random.choice(real_classes_idx, 
                                         size=int(real_classes_idx.size*real_classes_test),
                                         replace=False)

real_classes_train_idx = np.asarray([i for i in real_classes_idx if not i in real_classes_test_idx])



#%%


class_nc, optimiser = setup_classifier()

criterion, class_train_metrics, class_eval_metrics = train_classifier(

        class_nc, classes, real_classes_train_idx, real_classes_test_idx, 1000, 200
        
        )



#%%

mean_pred_prob = lambda preds, true_inds: np.mean([row[c].item() for row, c in zip(preds, true_inds)])



def setup_classifier(**classifier_args):
    args = dict(
                nnodes=num_nodes,
                nrel=num_rels,
                nclass=num_classes,
                nemb=4
            )
    
    args.update(classifier_args)
    nc = EmbeddingNodeClassifier(kg.translated,
                                 **args)
    optimiser = torch.optim.Adam(nc.parameters())
    
    return nc, optimiser


def train_classifier(model, classes, train_idx, test_idx, epochs, evals):
    criterion = torch.nn.CrossEntropyLoss()

    train_metrics = {criterion:[], 
                     accuracy_score:[],
                     mean_pred_prob:[]}
    eval_metrics = {criterion:[], 
                    accuracy_score:[],
                    mean_pred_prob:[]}

    node_embedding_l2_penalty = 2.0

    eval_epochs = range(0, epochs, epochs//(evals-1))

    pbar = tqdm(range(epochs), desc=str(np.inf))
    for epoch in pbar:
        model.train()
        optimiser.zero_grad()
        
        preds = model()
            
        loss_raw = criterion(preds[train_idx, :], classes[train_idx])
        
        node_embedding_l2 = model.node_embeddings.pow(2).sum()
        loss = loss_raw + node_embedding_l2_penalty * node_embedding_l2
        
            
        loss.backward()
        optimiser.step()
            
        if epoch in eval_epochs:
            train_acc = accuracy_score(classes[train_idx], preds[train_idx, :].argmax(1))
            train_mean_p_hat = mean_pred_prob(preds[train_idx, :].softmax(0), classes[test_idx])
    
            train_metrics[criterion].append(loss.item())
            train_metrics[accuracy_score].append(train_acc)        
            train_metrics[mean_pred_prob].append(train_mean_p_hat)
            
            test_preds = preds[test_idx, :]
            test_acc = accuracy_score(classes[test_idx], test_preds.argmax(1))
            mean_p_hat = mean_pred_prob(test_preds.softmax(0), classes[test_idx])
            test_xent = criterion(test_preds, classes[test_idx]).item()
            
            eval_metrics[criterion].append(test_xent)
            eval_metrics[accuracy_score].append(test_acc)
            eval_metrics[mean_pred_prob].append(mean_p_hat)
        pbar.set_description(str(round(loss.item(), 3)) + 
                             " (" + str(round(loss_raw.item(), 3)) + ")")

        
        
    return criterion, train_metrics, eval_metrics
        
        

#%%
import seaborn as sns
import matplotlib.pyplot as plt


train_metrics, eval_metrics = class_train_metrics, class_eval_metrics

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
#plt.ylim((0.0, 0.001))
plt.show()



#%%

neg_sum, pos_sum = is_person.sum(), (1-is_person).sum()
confusion_matrix(is_person.tolist(), person_nc().argmax(1).tolist())/np.asarray([pos_sum, neg_sum])[:,None]


#%%
#
#embeddings = class_nc.node_embeddings.detach().numpy()
#
#with open("embeddings.tsv", "w") as handle:
#    for v in embeddings:
#        handle.write("\t".join(map(str, v)))
#        handle.write("\n")
#
#
#
#from declarations.entities import Person
#
#
##with open(kg_name + ".label2entity.json") as handle:
##    cls2entity = {int(i): s for i, s in json.load(handle).items()}
#
#
#with open("meta.tsv", "w") as handle:
#    handle.write("is_person\tnode_class\tinstance_label\n")
#    for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e]):
#        is_person = type(e) is Person
#        node_class = ind2cls[kg.entity2ind[e]]
#        
##        o = cls2entity[node_class]
#
##        o = e.organisation.instance_label if is_person else "None"
#        l = e.instance_label if is_person else str(e)
#        
#        l = l.replace("\n", " ")
#        
#        handle.write("\t".join((str(is_person), str(node_class), l)))
#        handle.write("\n")

#%%
        
        
        
embeddings = class_nc.node_embeddings.detach().numpy()[real_classes_idx, :]

with open("embeddings.tsv", "w") as handle:
    for v in embeddings:
        handle.write("\t".join(map(str, v)))
        handle.write("\n")



from declarations.entities import Person


#with open(kg_name + ".label2entity.json") as handle:
#    cls2entity = {int(i): s for i, s in json.load(handle).items()}

i = 0
with open("meta.tsv", "w") as handle:
    handle.write("is_person\tnode_class\tinstance_label\n")
    for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e]):
        
        if i in real_classes_test_idx:
            is_person = type(e) is Person
            node_class = ind2cls[kg.entity2ind[e]]
            
    #        o = cls2entity[node_class]
    
    #        o = e.organisation.instance_label if is_person else "None"
            l = e.instance_label if is_person else str(e)
            
            l = l.replace("\n", " ")
            
            handle.write("\t".join((str(is_person), str(node_class), l)))
            handle.write("\n")
        
        i += 1
        
        
#%% BASELINE 

from collections import Counter


cls_seq = classes[real_classes_train_idx].tolist()
cls_counts = Counter(cls_seq)
cls_priors = [c/sum(cls_counts.values()) for i, c in sorted(cls_counts.items())]

repeat = 10
baseline_guesses = np.random.choice(len(cls_counts), 
                                    size=(repeat, real_classes_test_idx.size),
                                    p=cls_priors)

accuracy_scores = [accuracy_score(classes[real_classes_test_idx], row)
                    for row in baseline_guesses]

baseline_accuracy = np.mean(accuracy_scores)




        