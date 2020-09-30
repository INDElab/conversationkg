# -*- coding: utf-8 -*-

from tqdm import tqdm

import json

import numpy as np
import numpy.random as rand
import torch

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split


from KGs import KG

from torch_RGCN.models import EmbeddingNodeClassifier

from sklearn.metrics import accuracy_score, f1_score, balanced_accuracy_score

from itertools import product


def load_and_get_data(kg_path, heuristic_name):
    kg = KG.restore(kg_path)

    num_nodes = len(kg.entities())
    num_rels = len(kg.predicates())

    with open(kg_path + f".{heuristic_name}.ind2label.json") as handle:
        ind2cls = {int(i): c for i, c in json.load(handle).items()}

    classes = torch.tensor([
                ind2cls[kg.entity2ind[e]] for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e])
            ], dtype=torch.long)


    num_classes = (classes.max() + 1).item()
    assert num_classes == len(set(ind2cls.values())),\
                 f"Appar. some classes were not observed! {num_classes}, {set(ind2cls.values())}"
                 
    return kg, classes, num_nodes, num_rels, num_classes




def my_accuracy(preds, true_classes):
    return balanced_accuracy_score(true_classes, preds.argmax(1))
my_accuracy.__str__ = lambda :"accuracy score"

def mean_predicted_prob(preds, true_classes):
    true_one_hot = torch.nn.functional.one_hot(true_classes)
    return  (preds.softmax(1)*true_one_hot).sum(1).mean().item()
mean_predicted_prob.__str__ = lambda : "$mean_{x \in data} \hat{P}(true~c | x)$"

def my_macro_f1(preds, true_classes):
    return f1_score(true_classes, preds.argmax(1), average="macro")
my_macro_f1.__str__ = lambda :"macro f1 score"



def L2_regularisation(model):
    return model.node_embeddings.pow(2).sum()





def setup_training(triples, num_nodes, num_rels, num_classes, 
                   embedding_size=0, 
                   optimiser=torch.optim.Adam, 
                   optimiser_learning_rate=0.001,
                   optimiser_weight_decay=0.01,
                   loss=torch.nn.CrossEntropyLoss,
                   loss_weights=None, **unused_args):
    
    nc = EmbeddingNodeClassifier(triples,
                                 nnodes=num_nodes,
                                 nrel=num_rels,
                                 nclass=num_classes,
                                 nemb=embedding_size)
    
    
    optimiser = optimiser(nc.parameters(), lr=optimiser_learning_rate, 
                          weight_decay=optimiser_weight_decay)
        
    criterion = loss
    criterion = criterion(weight=loss_weights)
    
    
    return nc, optimiser, criterion


def train_classifier(model, optim, criterion, 
                     classes, train_idx, test_idx, 
                     epochs=1, num_evals=None,
                     regulariser=L2_regularisation, regulariser_coeff=1.0, **unused_args):

    mt = MetricsTracker(train_idx, test_idx, 
                        criterion, my_accuracy, mean_predicted_prob, my_macro_f1)
    

    if not num_evals:
        num_evals = max(epochs//10, 1)
    eval_epochs = range(0, epochs, epochs//(num_evals-1))

    pbar = tqdm(range(epochs), desc=str(np.inf))
    for epoch in pbar:
        model.train()
        optim.zero_grad()
        
        preds = model()
        
        loss_raw = criterion(preds[train_idx, :], classes[train_idx])
        
        
        regularisation = regulariser(model)
        
        loss = loss_raw + regulariser_coeff * regularisation
        
            
        loss.backward()
        optim.step()
            
        if epoch in eval_epochs:
            mt.track(preds, classes)
                  
        pbar.set_description(str(round(loss.item(), 3)) + 
                             " (" + str(round(loss_raw.item(), 3)) + ")")
        
    return mt





class MetricsTracker:
    def __init__(self, train_inds, test_inds, *metric_funcs):
        self.train_inds, self.test_inds = train_inds, test_inds
        self.metrics = metric_funcs
        self.train_vals, self.eval_vals = self.init_metrics()
        
    def init_metrics(self):
        return {m:[] for m in self.metrics}, {m:[] for m in self.metrics}


    def track(self, preds, true):
        for m in self.metrics:
            self.train_vals[m].append(m(preds[self.train_inds, :], true[self.train_inds]))
            self.eval_vals[m].append(m(preds[self.test_inds, :], true[self.test_inds]))


    def plot_metrics(self):
        for metric in self.metrics:
            train_vals, eval_vals = self.train_vals[metric], self.eval_vals[metric]
    
            rng = list(range(len(train_vals)))
            sns.scatterplot(rng, train_vals, label="train")
            sns.scatterplot(rng, eval_vals, label="eval")
            plt.title(metric.__str__())
            
            plt.show()



def grid_search(params_dict, max_iter=10):
    keys, values = list(zip(*params_dict.items()))
    grid = list(product(*values))
        
    iteration_order = rand.permutation(len(grid))
    print(iteration_order)
    
    for i in range(max_iter):
        yield dict(zip(keys, grid[iteration_order[i]]))
        
     
        
        
from collections import Counter
    
        
def get_baseline(class_sequence):
    v = np.asarray(class_sequence)
    cls_counts = Counter(v)
    cls_priors = [c/sum(cls_counts.values()) for i, c in sorted(cls_counts.items())]


    def pred(x, to_distribution=True):
        preds = np.random.choice(len(cls_counts), 
                                    size=x.shape[0],
                                    p=cls_priors)
        
        if not to_distribution:
            return torch.tensor(preds)
        
        dist = np.zeros((preds.size, preds.max()+1))
        dist[np.arange(preds.size), preds] = 1
        return torch.tensor(dist)

    return pred


#    repeat = 10
#    baseline_guesses = np.random.choice(len(cls_counts), 
#                                    size=(repeat, real_classes_test_idx.size),
#                                    p=cls_priors)
#
#accuracy_scores = [accuracy_score(classes[real_classes_test_idx], row)
#                    for row in baseline_guesses]
#
#baseline_accuracy = np.mean(accuracy_scores)
#
#
#
#def get_baseline_classifier(train_classes):
#    cls_seq = classes[real_classes_train_idx].tolist()
#    cls_counts = Counter(cls_seq)
#    cls_priors = np.asarray([c/sum(cls_counts.values()) for i, c in sorted(cls_counts.items())])
#    
#    def prior_prob(x):
#        return cls_priors
#    return prior_prob

    
    
    
    