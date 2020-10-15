# -*- coding: utf-8 -*-

import torch
import numpy as np
from tqdm import tqdm

from KGs import KG


from train_utils import load_and_get_data, train_test_split,\
                        setup_training, train_classifier, L2_regularisation,\
                        grid_search

from train_utils import my_accuracy, my_macro_f1, mean_predicted_prob


#%% LOAD DATA

mailing_list = "public-credentials"  # "ietf-http-wg"
kg_name = f"KGs/{mailing_list}/textkg"
heuristic = "ConfirmedPerson"

kg, classes, num_nodes, num_rels, num_classes = load_and_get_data(kg_name, heuristic)


#classes = torch.tensor(np.random.randint(num_classes, size=classes.size(0)))

#%% TEST WITH LABEL IS_PERSON


#relevant_inds 

relevant_num_classes = 2

relevant_inds = np.arange(classes.size(0))


from KGs import OnlyNamePerson

classes = torch.tensor([(1 if type(e) is OnlyNamePerson else 0)
                    for e in sorted(kg.entities(), key=lambda e: kg.entity2ind[e])
                ], dtype=torch.long)



train_inds, test_inds = train_test_split(relevant_inds)



#%% GET RELEVANT CLASSIFICATION INDICES

relevant_num_classes = num_classes - 1
relevant_inds = np.where(classes < relevant_num_classes)[0]

train_inds, test_inds = train_test_split(relevant_inds)


#%% DEFINE TRAINING PARAMETER DICT


#    _, cs = classes[real_classes_idx].unique(return_counts=True)
#    n_cls = 3
#    major_prob = cs.max().true_divide(cs.sum())
#    weights = torch.tensor([major_prob/n_cls]*n_cls + [1-major_prob, 0.])
#    weights = torch.tensor([100]*n_cls + [1, 0]).true_divide(2*n_cls+1).float()


#weights = torch.tensor([3, 1]).float().softmax(0)
#
#params = {
#    "embedding_size": [4, 8, 16],
#     "num_layers": [2],
#     "epochs": [100],
#     "loss": [torch.nn.CrossEntropyLoss],
#     "loss_weights": [weights],
#     "regulariser": [L2_regularisation],
#     "regulariser_coeff": [0.5, 1., 5., 10.],
#     "optimiser": [torch.optim.Adam, torch.optim.AdamW, toch.optim.Adamax, torch.optim.SGD],
#     "optimiser_learning_rate": [1., 1e-2, 1e-4],
#     "optimiser_weight_decay": [0.0] # , 1.0, 2.0]
#     }


from collections import Counter
class_counts = Counter(classes[train_inds].tolist())

weights = np.asarray([class_counts[l]/classes[train_inds].size(0) for l in sorted(class_counts)])
#weights = (1/weights)/((1/weights).sum())
weights = (1-weights)/(classes[train_inds].unique().size(0)-1)
assert weights.sum() == 1.

params = {
    "embedding_size": [8],
     "num_layers": [2],
     "epochs": [500],
     "loss": [torch.nn.CrossEntropyLoss],
#     "loss_weights": [torch.tensor([p, 1-p]).float() for p in np.arange(0.9, 0.96, 0.01)],
     "loss_weights": [None, torch.tensor(weights).float()],
     "regulariser": [L2_regularisation],
     "regulariser_coeff": [0.1, 1.0],
     "optimiser": [torch.optim.Adam],
     "optimiser_learning_rate": [1e-1, 1e-2, 1e-3],
     "optimiser_weight_decay": [0.1, 1.0] # , 1.0, 2.0]
     }



params = {
    "embedding_size": [8, 16, 32],
     "num_layers": [2],
     "epochs": [1000],
     "loss": [torch.nn.CrossEntropyLoss],
#     "loss_weights": [torch.tensor([p, 1-p]).float() for p in np.arange(0.9, 0.96, 0.01)],
     "loss_weights": [None],
     "regulariser": [L2_regularisation],
     "regulariser_coeff": [2.0],
     "optimiser": [torch.optim.Adam],
     "optimiser_learning_rate": [1e-3],
     "optimiser_weight_decay": [0.1] # , 1.0, 2.0]
     }





#params = {
#    "embedding_size": 2,
#     "num_layers": 2,
#     "epochs": 500,
#     "loss": torch.nn.CrossEntropyLoss,
#     "loss_weights": weights,
#     "regulariser": L2_regularisation,
#     "regulariser_coeff": 1.,
#     "optimiser": torch.optim.Adam,
#     "optimiser_learning_rate": 1e-3,
#     "optimiser_weight_decay": 1.0
#        }


#%%

gs = grid_search(params, max_iter=3)


results = []

for param_d in gs:

    print("\n\n\n", param_d)
    
    model, optim, criterion = setup_training(kg.translated, num_nodes, num_rels, relevant_num_classes,
                              **param_d)

    metric_tracker = train_classifier(model, optim, criterion, 
                                      classes, train_inds, test_inds,
                                      **param_d)

    results.append((param_d, metric_tracker))


#%%


param_dicts, metrics = list(zip(*results))


for p, m in results:
    print("lr:", p["optimiser_learning_rate"])
    print("loss_weights:", p["loss_weights"])
    
    print(p)
    for f in m.eval_vals.keys():
        print(f.__str__(), max(m.eval_vals[f]))
#        print("_"*10 + "\n\n")
    
    m.plot_metrics()
    print("_"*10 + "\n\n")



#%%
    
from train_utils import get_baseline


baseline_model = get_baseline(class_sequence=classes[train_inds])

ent_seq = np.arange(num_nodes)

mean_vals = {f: np.mean([f(baseline_model(ent_seq)[test_inds], classes[test_inds])
                            for _ in range(500)])
             for f in (my_accuracy, my_macro_f1, mean_predicted_prob)}

    


for f in mean_vals.keys():
    print(f.__str__(), mean_vals[f])






#%%
    

TODO:
    
 - adapt TextKG:
     - add more NER types (orgs, locations, ...) -> connect people to them
     
     
     
 - adapt labelling:
     - fuzzy string matching
     - 
     
     
 - try simpler models: 
     - matrix factorization
     - label propagation
     - RDF2Vec
     
 
 
Brian:
    
    - pipeline to get EmailKG => thats our approach to transform email data 
      into a representation that we can answer ML questions over (e.g. clustering into topics)
      -> important info: JSON-format of email corpus that the KG extraction works on
    
    - mention: approach works for multi-lingual settings because it is to a large part language-independent
    