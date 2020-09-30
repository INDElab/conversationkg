# -*- coding: utf-8 -*-

import networkx
from collections import Counter

import numpy as np
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import seaborn as sns

from declarations.entities import Person
from KGs import OnlyNamePerson


#class RoleMapping(dict):
#    def __getitem__(self, item):
#        if not 



class RoleHeuristic:
    def __init__(self, kg, getter_func):
        self.getter_func = getter_func
    
    
    
#    @staticmethod
#    def make_total(mapping):
#        
    
    
    def label(self, kg, getter_func=None, to_dict=False):
        if not getter_func: 
            getter_func = self.getter_func
            
        labels = []
        
        unclassified_person_label = max(self.entity2label.values()) + 1
        nonperson_label = unclassified_person_label + 1
        
        for e in kg.entities():
            if type(e) is OnlyNamePerson:
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



class ConfirmedPerson(RoleHeuristic):
    def __repr__(self):
        return "ConfirmedPerson"
    
    def __init__(self, kg, getter_func=lambda x:x):
        persons = kg.entities(lambda p: type(p) is OnlyNamePerson)
        self.entity2label = {getter_func(p):0 for p in persons}
        
        
        
        super().__init__(kg, getter_func)






class Senders(RoleHeuristic):
    def __repr__(self):
        return "Senders"
    
    def __init__(self, kg, getter_func=lambda x:x):        
        persons = kg.entities(lambda p: type(p) is OnlyNamePerson)
        
        senders = {s for s, p, o in kg.triples if p =="talked_to"}    

        self.entity2label = {getter_func(p): (1 if p in senders else 0)
                                for p in persons }
        
    
        super().__init__(kg, getter_func)
                
        
class SendersorReceivers(RoleHeuristic):
    def __repr__(self):
        return "SendersorReceivers"
    
    def __init__(self, kg, sender=False, receiver=False, getter_func=lambda x: x):
#        assert sender_or_receiver in {"sender", "receiver", "both"}
        
        assert sender or receiver
        
        persons = kg.entities(lambda p: type(p) is OnlyNamePerson)
        
        self.entity2label = {}
        for s, p, o in kg.triples:
            if p == "talked_to":
                if sender:
                    self.entity2label[getter_func(s)] = 1
                if receiver:
                    self.entity2label[getter_func(o)] = 1
                
        for p in persons:
            if not getter_func(p) in self.entity2label:
                self.entity2label[getter_func(p)] = 0        
                
                
        super().__init__(kg, getter_func)
        
        
        
class MajorOrganisations(RoleHeuristic):
    def __repr__(self):
        return "MajorOrganisations"
    
    
    def __init__(self, kg, most_common=5, getter_func=lambda x: x):
        
        persons = kg.entities(lambda p: type(p) is OnlyNamePerson)
        
        orgs = [p.organisation for p in persons]
        
        org_counts = Counter(orgs)
        
        self.org2label = {o: l for (o, c), l in zip(org_counts.most_common(most_common), range(1, most_common+1))}
        self.label2class = {0: "REST"} 
        self.label2class.update({l: o for o, l in self.org2label.items()})

        self.org2label.update({o: 0 for o, _ in org_counts.most_common()[most_common:]})
        
        self.entity2label = {getter_func(p):self.org2label[p.organisation] for p in persons}
        
        self.value_seq = orgs
        self.label_seq = [self.org2label[o] for o in self.value_seq]
        
        super().__init__(kg, getter_func)

        
        
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
        
        
        
class RolesfromGraphMeasure(RoleHeuristic):
    clustering_coeff = networkx.cluster.clustering
    
    def __repr__(self):
        return "RolesfromGraphMeasure"
        
    def __init__(self, kg, n_roles, graph_measure, getter_func=lambda x: x):
        G = networkx.DiGraph()
        G.add_edges_from(kg.tuples())
        
        d_items = sorted(graph_measure(G, kg.entities(lambda x: type(x) is OnlyNamePerson)).items(),
                         key=lambda t: t[1])
        persons, self.values = list(zip(*d_items))
        
        km = KMeans(n_clusters=n_roles)
        km.fit(np.reshape(self.values, (-1, 1)))
        self.labels = km.labels_
        
#        grouped = 
#        self.label2class = 
        
        self.entity2label = {getter_func(p): l for p, l in zip(persons, self.labels)}
        
        super().__init__(kg, getter_func)
        
        
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