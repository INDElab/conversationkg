# -*- coding: utf-8 -*-


#%%
from tqdm import tqdm

import json
from declarations.corpus import EmailCorpus, Conversation
from declarations.entities import Person


#%%


class TripleExtractor:
    def __init__(self, email_corpus):
        self.triples = []
        
        for conv in email_corpus:
            
            
            for email in conv:
                self.triples.append((conv, "consists_of", email))
                
                self.triples.append((email.sender, "talked_to", email.receiver))
                
                self.triples.append((email.sender, "part_of", email.sender.organisation))
                self.triples.append((email.receiver, "part_of", email.receiver.organisation))
                
        
        
        for c1, c2 in zip(email_corpus, email_corpus[:1]):
            self.triples.append((c1, "before", c2))
            
            for e1, e2 in zip(c1, c1[:1]):
                self.triples.append((e1, "before", e2))
        
        
    def translate(self):
        i = j = 0
        ed, pd = {}, {}
        
        translated = []
            
        def put(d, x, i):
            if not x in d:
                d[x] = i
                i += 1
            return d[x], i
        
        for s, p, o in self.triples:
            s_prime, i = put(ed, s, i)
            o_prime, i = put(ed, o, i)
            p_prime, j = put(pd, p, j)
            
            translated.append((s_prime, p_prime, o_prime))
        
        self.translated = translated
        self.entity2ind = ed
        self.pred2ind = pd
        
        
    def store(self):
        with open("triples.json", "w") as handle:
            json.dump([((s.to_json(), type(s).__name__), 
                        p, 
                        (o.to_json(), type(o).__name__)) for o, p, s in self.triples], handle)
        
        with open("triples_inds.json", "w") as handle:
            json.dump(self.translated, handle)
        
        
        reversed_d = self.reverse_dict(self.entity2ind)
        json_d = {i:e.to_json() for i, e in reversed_d.items()}
        with open("ind2entity.json", "w") as handle:
            json.dump(json_d, handle)
            
    
    @staticmethod
    def reverse_dict(d):
        if not len(d) == len(set(d.values())):
            raise ValueError("Provided dict is not a bijective mapping!")
        return {v:k for k, v in d.items()}
            
            
#%%


with open("email_data/ietf-http-wg/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

convos_short = convos[:200]

conversations = [Conversation.from_email_dicts(*tup) for tup in tqdm(convos_short)]

corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)

            
te = TripleExtractor(corpus)
te.translate()



#%%
import networkx

import matplotlib.pyplot as plt
import seaborn as sns

G = networkx.DiGraph()

tuples = [(s, o) for s, p, o in te.triples]

G.add_edges_from(tuples)


people = set(e for t in tuples for e in t if type(e) is Person)


graph_f = networkx.algorithms.betweenness_centrality
#graph_f = networkx.algorithms.degree_centrality
#graph_f = networkx.algorithms.percolation_centrality
#
#
#
graph_f = networkx.algorithms.cluster.clustering



bc = graph_f(G, nodes=people)

bc_people = {e:v for e, v in bc.items() if type(e) is Person}
nodes, vals = list(zip(*bc_people.items()))




#%%

from sklearn.cluster import KMeans

import numpy as np

km = KMeans(n_clusters=3)

km.fit(np.reshape(vals, (-1, 1)))




        

