# -*- coding: utf-8 -*-

from tqdm import tqdm


class TripleExtractor:
    def __init__(self, email_corpus):
        self.triples = []
        
        
        for conv in tqdm(email_corpus, desc="Extracting Triples..."):
            
            self.triples.append((conv, "is_about", conv.topic.topic))

            for p in conv.interlocutors:
                self.triples.append((p, "part_of", conv))
            
            for o in conv.organisations:
                self.triples.append((o, "part_of", conv))
                
            for d in conv.documents:
                self.triples.append((conv, "mentions", d))
            
            
            for email in conv:
                
                self.triples.append((email, "part_of", conv))
                self.triples.append((email, "is_about", email.topic.topic))
                
                self.triples.append((email.sender, "talked_to", email.receiver))
                self.triples.append((email.sender, "evidences", email.sender.address))
                self.triples.append((email.receiver, "evidences", email.receiver.address))
                
                
                self.triples.append((email.sender.organisation, 
                                     "talked_to", email.receiver.organisation))
                self.triples.append((email.sender, "evidences",
                                     email.sender.organisation))
                self.triples.append((email.receiver, "evidences",
                                     email.receiver.organisation))
                
                for link in email.body.links:
                    self.triples.append((email, "mentions", link))
                for addr in email.body.addresses:
                    self.triples.append((email, "mentions", addr))
                for entity in email.body.addresses:
                    self.triples.append((email, "mentions", entity))
                
                
                
        for c1, c2 in zip(corpus, corpus[1:]):
            self.triples.append((c1, "before", c2))
            
            for e1, e2 in zip(c1, c1[1:]):
                self.triples.append((e1, "before", e2))
                
    def translate_id(self):
        i_e = 0
        i_p = 0
        e_dict = {}
        p_dict = {}
        translated_triples = []
        
        def put(d, x, i):
            if x in d:
                i_to_use = d[x]
                return i_to_use
            else:
                d[x] = i
                return i+1
        
        for s, p, o in self.triples:
            s_prime = put(e_dict, s, i_e)
            p_prime = put(p_dict, s, i_p)
            o_prime = put(e_dict, o, i_e)
            
            
            
#            s_prime = i_e
#            e_dict[s] = i_e
#            i_e += 1
#            
#            o_prime = i_e
#            e_dict[o] = i_e
#            i_e += 1
#            
#            p_prime = i_p
#            p_dict[p] = i_p
#            i_p += 1
#            
            translated_triples.append((s_prime, p_prime, o_prime))
            
        self.e_dict = e_dict
        self.p_dict = p_dict
        self.translated = translated_triples
            
        
        
        
#%%
        
import json
from declarations.corpus import EmailCorpus


with open("corpus.json") as handle:
    corpus = json.load(handle)
    corpus = EmailCorpus.from_json(corpus)
    
    
#%%
    
    
te = TripleExtractor(corpus)
te.translate_id()



