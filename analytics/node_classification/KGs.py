# -*- coding: utf-8 -*-

import declarations.corpus
import declarations.topics

from declarations.corpus import EmailCorpus, Conversation
from declarations.entities import Person

import spacy
nlp = spacy.load("en_core_web_md")

from tqdm import tqdm
import json


class KG:
    @classmethod
    def from_email_corpus(cls, email_corpus, triples=[]):
        print(cls, type(email_corpus), type(triples))
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in KG"):
            triples.append((conv, "is_about", conv.topic.topic)) # both

            for d in conv.documents:
                triples.append((conv, "mentions", d)) # both
            
            for email in conv:
                triples.append((email, "part_of", conv)) # both
                triples.append((email, "is_about", email.topic.topic)) # bith
                
                for link in email.body.links: 
                    triples.append((email, "mentions", link)) # both
                for addr in email.body.addresses:
                    triples.append((email, "mentions", addr)) # both
                for entity in email.body.addresses: 
                    triples.append((email, "mentions", entity)) # both
    
    
        for c1, c2 in zip(email_corpus, email_corpus[1:]):
            triples.append((c1, "before", c2))
            
            for e1, e2 in zip(c1, c1[1:]):
                triples.append((e1, "before", e2))

        return cls(triples)
    
    
    
    def __init__(self, triples):
        self.triples = triples
    
    
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
    
    def tuples(self):
        return [(s, o) for s, p, o in self.triples]
    
    def entities(self, filter_f=lambda x: True):
        return set(e for s, p, o in self.triples for e in (s, o) if filter_f(e))
      
    def predicates(self):
        return set(p for s, p, o in self.triples)
    
    def store(self, name):
        with open(f"{name}.json", "w") as handle:
            json.dump(self.translated, handle)
        
        reversed_d = self.reverse_mapping(self.entity2ind)
        json_d = {i:e.to_json() for i, e in reversed_d.items()}
        
        with open(f"{name}.ind2entity.json", "w") as handle:
            json.dump(json_d, handle)
            
        reverse_d = self.reverse_mapping(self.pred2ind)
        with open(f"{name}.ind2pred.json", "w") as handle:
            json.dump(reverse_d, handle)
            
            
    @classmethod
    def restore(cls, name):
        def get_class(cls_name):
            for mod in [declarations.corpus, declarations.emails, 
                        declarations.entities, declarations.topics]:
                try:
                    cls = getattr(mod, cls_name)
                    return cls
                except AttributeError:
                    pass
            raise AttributeError(f"{cls_name} could not be found in any of the modules!")
                
        
        def json_to_entity(json_dict):
            try:
                json_dict["class"]
            except KeyError:
                print(json_dict.keys())
                raise
                
            cls_name = json_dict["class"]
            cls = get_class(cls_name)
            return cls.from_json(json_dict)
        
        
        with open(f"{name}.ind2entity.json") as handle:
            loaded_entity_mapping = {int(i): d for i, d in json.load(handle).items()}
            ind2entity = {i:json_to_entity(d) for i, d in loaded_entity_mapping.items()}
            
        with open(f"{name}.ind2pred.json") as handle:
            ind2pred = {int(i): d for i, d in json.load(handle).items()}
        
        
        with open(f"{name}.json") as handle:
            loaded = json.load(handle)    
        
        restored_triples = [(ind2entity[s],
                             ind2pred[p],
                             ind2entity[o]) for s, p, o in loaded]
        
        kg = KG(restored_triples)
        
        kg.translated = loaded
        kg.entity2ind = kg.reverse_mapping(ind2entity)
        kg.pred2ind = kg.reverse_mapping(ind2pred)
        
        return kg
    
    
    @staticmethod
    def reverse_mapping(d):
        if not len(d) == len(set(d.values())):
            raise ValueError("Provided dict is not a bijective mapping!")
        return {v:k for k, v in d.items()}
        
        


class EmailKG(KG):
    def __new__(cls, email_corpus):
        triples = []

        for conv in tqdm(email_corpus, desc="Iterating Conversations in EmailKG"):
            for p in conv.interlocutors:
                triples.append((p, "part_of", conv))
            
            for o in conv.organisations:
                triples.append((o, "part_of", conv))
                
                
            for email in conv:
                triples.append((email.sender, "talked_to", email.receiver))
                triples.append((email.sender, "evidences", email.sender.address))
                triples.append((email.receiver, "evidences", email.receiver.address))
                
                
                triples.append((email.sender.organisation, 
                                     "talked_to", email.receiver.organisation))
                triples.append((email.sender, "evidences",
                                     email.sender.organisation))
                triples.append((email.receiver, "evidences",
                                     email.receiver.organisation))
                                
        return KG.from_email_corpus(email_corpus, triples)


class TextKG(KG):
    def __new__(cls, email_corpus):
        triples = []
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in TextKG"):
            for email in conv:
                mentioned_people = [Person(str(e), "None") for e in nlp(str(email.body)).ents 
                                    if e.label_ == "PERSON"]
                for person in mentioned_people:
                    triples.append((email, "mentions", person))
                    
                    for person2 in mentioned_people:
                        if not person == person2:
                            triples.append((person, "talked_to", person2))
        
        return KG.from_email_corpus(email_corpus, triples)
        

def intersect_persons(emailkg, textkg):
    is_person = lambda x: type(x) is Person
    emailkg_names = {x.instance_label for x in emailkg.entities(is_person)}
    
    def keep(s, o, name_set):
        if not (is_person(s) or is_person(o)):
            return True
        
        if is_person(s) and is_person(o):
            if s.instance_label in name_set or o.instance_label in name_set:
                return True
            
        if is_person(s):
            if s.instance_label in name_set:
                return True
        
        if is_person(o):
            if o.instance_label in name_set:
                return True
        
        return False

    new_triples = []
    for s, p, o in textkg.triples:
        
        if keep(s, o, emailkg_names):
            new_triples.append((s, p, o))
    
    
    new_kg = KG(new_triples)
    
    return new_kg


def dict_union(d1, d2, densify=False):
    new_d = {**d1}
    i = max(new_d.values()) + 1
    for k in d2.keys() - new_d.keys():
        new_d[k] = i
        i += 1
        
    return new_d




def unify_translations(kg1, kg2):
    unified_entity_map = dict_union(kg1.entity2ind, kg2.entity2ind)
    unified_pred_map = dict_union(kg1.pred2ind, kg2.pred2ind)
    
    return unified_entity_map, unified_pred_map






def unified_translation(*kgs, do_retranslation=False):
    all_ents = set.union(*[kg.entities() for kg in kgs])
    
    all_preds = set.union(*[kg.predicates() for kg in kgs])
    
    e2i = dict(zip(all_ents, range(len(all_ents))))
    p2i = dict(zip(all_preds, range(len(all_ents))))
    
    if retranslate:
        for kg in kgs:
            retranslate(kg, e2i, p2i)
    
    return e2i, p2i


def retranslate(kg, ent2ind, pred2ind):
    
    kg.translated = [(ent2ind[s], pred2ind[p], ent2ind[o])
                        for s, p, o in kg.triples]
    
    kg.entity2ind = ent2ind
    kg.pred2ind = pred2ind
