# -*- coding: utf-8 -*-

from declarations.entities import Person

from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np

import networkx
from sklearn.cluster import KMeans


class RoleHeuristic:
    def __init__(self, kg):
        pass
    
    
    
    def label(self, kg, getter_func=lambda x: x, to_dict=False):
        labels = []
        
        unclassified_person_label = max(self.entity2label.values()) + 1
        nonperson_label = unclassified_person_label + 1
        
        for e in kg.entities():
            if type(e) is Person:
                if getter_func(e) in self.entity2label:
                    labels.append(self.entity2label[getter_func(e)])
                else:
                    labels.append(unclassified_person_label)
            else:
                labels.append(nonperson_label)
        if to_dict:
            return dict(zip(kg.entities(), labels))
        return labels
    
    
    
    def inspect(self):
        # distribution over classes (prior)
        # label_seq is always numeric (training labels)
        sns.distplot(self.label_seq, kde=False, norm_hist=False)
        plt.title("Distribution over assigned classes")
        plt.show()

    
    
class MajorOrganisations(RoleHeuristic):
    def __init__(self, kg, most_common=5, getter_func=lambda x: x):
        
        persons = kg.entities(lambda p: type(p) is Person)
        
        orgs = [p.organisation for p in persons]
        
        org_counts = Counter(orgs)
        
        self.org2label = {o: l for (o, c), l in zip(org_counts.most_common(most_common), range(1, most_common+1))}
        self.label2class = {0: "REST"} 
        self.label2class.update({l: o for o, l in self.org2label.items()})

        self.org2label.update({o: 0 for o, _ in org_counts.most_common()[most_common:]})
        
        self.entity2label = {getter_func(p):self.org2label[p.organisation] for p in persons}
        
        
    def inspect(self):
        # distribution over organisations
        orgs = [(o.instance_label if l > 0 else "REST") 
                for o, l in zip(self.value_seq, self.label_seq)]
        sns.countplot(orgs)
        
        plt.title("Distribution over organisations")
        plt.show()


#        super().inspect()
        
        
        # distribution over number of emails per organisation
        # could be obtained from triples
        # => reveals that major orgs have many people associated with them but not many emails
        # as compared to the rest
#        mails = [e.sender.organisation for e in corpus.iter_emails()]
#        mails = [n.instance_label if self.label_mapping[n] else "REST" for n in mails]
#        sns.countplot(mails)
        
#%%
        
        
class RolesfromGraphMeasure(RoleHeuristic):
    clustering_coeff = networkx.cluster.clustering
    def __init__(self, kg, n_roles, graph_measure, getter_func=lambda x: x):
        G = networkx.DiGraph()
        G.add_edges_from(kg.tuples())
        
        d_items = sorted(graph_measure(G, kg.entities(lambda x: type(x) is Person)).items(),
                         key=lambda t: t[1])
        persons, self.values = list(zip(*d_items))
        
        km = KMeans(n_clusters=n_roles)
        km.fit(np.reshape(self.values, (-1, 1)))
        self.labels = km.labels_
        
#        grouped = 
#        self.label2class = 
        
        self.entity2label = {getter_func(p): l for p, l in zip(persons, self.labels)}
        
        
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
        
        
        
        