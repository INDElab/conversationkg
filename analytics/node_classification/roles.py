# -*- coding: utf-8 -*-

import networkx
from collections import Counter

import numpy as np
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import seaborn as sns

from KGs import Person


class RoleHeuristic:
    def __init__(self, kg):
        self.unseen_label = max(self.entity2label.values()) + 1
        self.non_person_label = self.unseen_label + 1
        self.meaning_mapping[self.unseen_label] = "unseen"
        self.meaning_mapping[self.non_person_label] = "non-person entity"
    
    def get_label_approx(self, entity):
        approx_matches = [self.entity2label[other_e] for other_e in self.entity2label
                          if entity == other_e]
        
        if approx_matches:
            return np.random.choice(approx_matches)
        else:
            return None        
        
    def get_label_fast(self, entity):
        if entity in self.entity2label:
            return self.entity2label[entity]
        else:
            return None

    def label(self, kg, to_dict=False):  # matching_is_approx=False, to_dict=False):
#        get_label = self.get_label_approx if matching_is_approx else self.get_label_fast
        get_label = self.get_label_fast
        
        labels = []
        for e in kg.entities():
            if type(e) is Person:
                label = get_label(e)
                if label is not None:
                    labels.append(label)
                else:
                    labels.append(self.unseen_label)
            else:
                labels.append(self.non_person_label)
                
        if to_dict:
            return dict(zip(kg.entities(), labels))
        return labels
    
    def inspect(self):
        # distribution over classes (prior)
        # label_seq is always numeric (training labels)
        sns.distplot(self.label_seq, kde=False, norm_hist=False)
        plt.title("Distribution over assigned classes")
        plt.show()



class ConfirmedPerson(RoleHeuristic):
    def __repr__(self):
        return "ConfirmedPerson"
    
    def __init__(self, kg):
        persons = kg.entities(lambda p: type(p) is Person)
        self.entity2label = {p:0 for p in persons}
        
        self.mapping_meanings = {0: "confirmed"}
        
        super().__init__(kg)
        



class Senders(RoleHeuristic):
    def __repr__(self):
        return "Senders"
    
    def __init__(self, kg):        
        persons = kg.entities(lambda p: type(p) is Person)
        
        senders = {s for s, p, o in kg.triples if p == "talked_to"}    

        self.entity2label = {p: (1 if p in senders else 0)
                                for p in persons }
        
        self.mapping_meanings = {0: "non-sender",
                                 1: "sender"}
    
        super().__init__(kg)
                
        
class SendersOrReceivers(RoleHeuristic):
    def __repr__(self):
        return "SendersorReceivers"
    
    def __init__(self, kg, senders=False, receivers=False):        
        assert senders or receivers
        
        persons = kg.entities(lambda p: type(p) is Person)
        
        self.entity2label = {}
        for s, p, o in kg.triples:
            if p == "talked_to":
                if senders:
                    self.entity2label[s] = 0
                if receivers:
                    self.entity2label[o] = 0
                
        for p in persons:
            if not p in self.entity2label:
                self.entity2label[p] = 1
                
        
        if senders and not receivers:
            self.mapping_meanings = {1: "non-sender",
                                     0: "sender"}
        elif receivers and not senders:
            self.mapping_meanings = {1: "non-receiver",
                                     0: "receiver"}
        else:
            self.mapping_meanings = {1: "unseen",
                                     0: "confirmed"}            
                
        super().__init__(kg)
        


     
#%%
        
class MajorOrganisations(RoleHeuristic):
    def __repr__(self):
        return "MajorOrganisations"
    
    def __init__(self, kg, most_common=5):
        
        persons = kg.entities(lambda p: type(p) is Person)
        
        orgs = [p.organisation for p in persons]
        
        org_counts = Counter(orgs)
        
        self.org2label = {o: l for (o, c), l in zip(org_counts.most_common(most_common), 
                                                    range(1, most_common+1))}
                
        self.mapping_meanings = {0: "other organisation"} 
        self.mapping_meanings.update({l: o for o, l in self.org2label.items()})

        self.org2label.update({o: 0 for o, _ in org_counts.most_common()[most_common:]})
        
        self.entity2label = {p:self.org2label[p.organisation] for p in persons}
        
#        self.value_seq = orgs
#        self.label_seq = [self.org2label[o] for o in self.value_seq]
        
        super().__init__(kg)

        
        
#    def inspect(self):
#        # distribution over organisations
#        orgs = [(o.instance_label if l > 0 else "REST") 
#                for o, l in zip(self.value_seq, self.label_seq)]
#        sns.countplot(orgs)
#        
#        plt.title("Distribution over organisations")
#        plt.show()


#        super().inspect()
        
        
        # distribution over number of emails per organisation
        # could be obtained from triples
        # => reveals that major orgs have many people associated with them but not many emails
        # as compared to the rest
#        mails = [e.sender.organisation for e in corpus.iter_emails()]
#        mails = [n.instance_label if self.label_mapping[n] else "REST" for n in mails]
#        sns.countplot(mails)
        
        
        
class RolesfromGraphMeasure(RoleHeuristic):
    clustering_coeff = networkx.cluster.clustering
    
    def __repr__(self):
        return "RolesfromGraphMeasure"
        
    def __init__(self, kg, n_roles, graph_measure):
        G = networkx.DiGraph()
        G.add_edges_from(kg.tuples())
        
        d_items = sorted(graph_measure(G, kg.entities(lambda x: type(x) is Person)).items(),
                         key=lambda t: t[1])
        persons, self.values = list(zip(*d_items))
        
        km = KMeans(n_clusters=n_roles)
        km.fit(np.reshape(self.values, (-1, 1)))
        self.cluster_centres = km.cluster_centers_.flatten()
        self.labels = km.labels_
        
        
        relabels = []
        l = 0 
        cur_r = self.labels[0]
        for r in self.labels:
            if not r == cur_r:
                cur_r = r
                l += 1
            relabels.append(l)
        self.labels = relabels
        
        self.entity2label = {p: l for p, l in zip(persons, self.labels)}
        
        
        self.meaning_mapping = {
                    l: f"cluster around {c.round(3)}"
                    for l, c in zip(range(n_roles), self.cluster_centres)
                }
        
        super().__init__(kg)
        
        
    def _get_role_boundaries(self):        
        boundaries = [(c1+c2)/2 for c1, c2 in 
                      zip(self.cluster_centres, self.cluster_centres[1:])]

        return [0.] + boundaries + [1.]
        
    def inspect(self):
        values_per_class = {c: [] for c in set(self.label_seq)}
        for c, l in zip(self.label_seq, self.value_seq):
            values_per_class[c].append(l)
        
        
        # distribution over values per class (likelihood)
        for l, ls in values_per_class.items():
            sns.distplot(ls, label=str(l), norm_hist=False, kde=False)
        plt.ylim((0, Counter(self.value_seq).most_common(2)[1][1]))
        plt.legend()
        plt.title(f"Distributions over values from graph measure `{self.graph_measure.__name__}`\n over classes (see legend)")
        plt.show()
        
        
        # distribution over values from graph measure (evidence)
        sns.distplot(self.value_seq)
        plt.title(f"Distribution over values from graph measure `{self.graph_measure.__name__}`")
        plt.show()
        
        class_dist = Counter(self.entity2label.values())
        
        super().inspect()
        
        
        return values_per_class, class_dist