#from ..conversations.corpus import EmailCorpus, Conversation
#from ..conversations.emails import Email
#from ..conversations.topics import TopicModel
from ..conversations.entities import Person as WholePerson


from ..conversations import corpus, emails, entities  # , topics

conversations_modules = [corpus, emails, entities] # , topics]


import numpy as np

from tqdm import tqdm
import json

import Levenshtein
import spacy
nlp = spacy.load("en_core_web_md")




# distance threshold value of around 0.3 seems to capture identity quite well
class Person(WholePerson):
    def __init__(self, person):  #, distance_threshold=0.0):
        self.__dict__ = person.__dict__
        
        self.name = self.name.lower()

    def __repr__(self):
        return f"PersonNode({str(self)})"
        
    def __str__(self):
        return f"{self.name if self.name else '_'}"

    
    def distance_from(self, other):
        my_name, your_name = self.name, other.name
        
        if max(len(my_name), len(your_name)) == 0:
            return 0.
        
        d = Levenshtein.distance(my_name, your_name)
        
        return d/max(len(my_name), len(your_name))
    
    
    def __hash__(self):
#        raise NotImplementedError
        return hash(self.name)
        
   
    def __eq__(self, other):
        if not (type(self) == type(other)):
            return False
        return self.name == other.name


def put(d, x, i):
    if not x in d:
        d[x] = i
        i += 1
    return d[x], i

def put_based_on_eq(d, x, i):
    if not type(x) is Person:
        return put(d, x, i)
    
    print(x.name, end=", ")

    approx_matches = [other_x for other_x in d if x == other_x]
    
    if not approx_matches:
        d[x] = i
        i += 1
        return d[x], i
    else:
        found_i = d[np.random.choice(approx_matches)]
        return found_i, i




class KG:
    @classmethod
    def from_email_corpus(cls, email_corpus, triples=[], provenances=[]):    
        for conv in email_corpus:
            for email in conv:
                triples.append((email, "part_of", conv)) # both
                provenances.append(email.message_id)
                
                for link in email.body.links: 
                    triples.append((email, "mentions", link)) # both
                    provenances.append(email.message_id)

                for addr in email.body.addresses:
                    triples.append((email, "mentions", addr)) # both
                    provenances.append(email.message_id)
        
        
        for c1, c2 in zip(email_corpus, email_corpus[1:]):
            triples.append((c1, "before", c2))
            provenances.append(c2[0].message_id)
            
            for e1, e2 in zip(c1, c1[1:]):
                triples.append((e1, "before", e2))
                provenances.append(e2.message_id)

        
        return cls(triples, provenances)
    
    
    
    def __init__(self, triples, provenances):
        self.triples = triples
        self.provenances = provenances
    
    def translate(self, entity2ind=None, pred2ind=None, attach=False):
        if entity2ind or pred2ind:
            assert entity2ind and pred2ind, "Please provide both entity2ind and pred2ind or none!"
            i = max(entity2ind.values()) + 1
            j = max(pred2ind.values()) + 1
        else:
            i = j = 0
            entity2ind, pred2ind = {}, {}
        
        put_ = put
        
        translated = []
        for s, p, o in tqdm(self.triples, desc="translating"):
            s_prime, i = put_(entity2ind, s, i)
            o_prime, i = put_(entity2ind, o, i)
            p_prime, j = put_(pred2ind, p, j)
            
            translated.append((s_prime, p_prime, o_prime))
        
        
        if attach:
            self.translated = translated
            self.entity2ind = entity2ind
            self.pred2ind = pred2ind
        else:
            return translated, entity2ind, pred2ind


    @staticmethod
    def unified_translation(*kgs, attach=False):
        uni_e2i, uni_p2i = {}, {}
        for kg in tqdm(kgs, desc="unified translating"):
            translated, uni_e2i, uni_p2i = kg.translate(uni_e2i, uni_p2i, attach=False)
            if attach:
                kg.translated = translated

        if attach:
            for kg in kgs:
                kg.entity2ind = uni_e2i
                kg.pred2ind = uni_p2i
        else:
            return uni_e2i, uni_p2i
        
    
    def tuples(self):
        return [(s, o) for s, p, o in self.triples]
    
    def entities(self, filter_f=lambda x: True):
        return set(e for s, p, o in self.triples for e in (s, o) if filter_f(e))
    
    def predicates(self):
        return set(p for s, p, o in self.triples)
    
    def store(self, name, save_mapping=True):
        with open(f"{name}.json", "w") as handle:
            json.dump(self.translated, handle)
            
        with open(f"{name}.provenances.json", "w") as handle:
            json.dump(self.provenances, handle)
        
        if save_mapping:
            reversed_d = self.reverse_mapping(self.entity2ind)
            json_d = {i:e.to_json() for i, e in reversed_d.items()}
            
            with open(f"{name}.ind2entity.json", "w") as handle:
                json.dump(json_d, handle)
            
            reverse_d = self.reverse_mapping(self.pred2ind)
            with open(f"{name}.ind2pred.json", "w") as handle:
                json.dump(reverse_d, handle)
    
    
    @classmethod
    def restore(cls, name, load_mapping_of=None):
        def get_class(cls_name):
            for mod in conversations_modules:
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
        
        
        if load_mapping_of is None:
            load_mapping_of = name
        
        with open(f"{load_mapping_of}.ind2entity.json") as handle:
            loaded_entity_mapping = {int(i): d for i, d in json.load(handle).items()}
            ind2entity = {i:json_to_entity(d) for i, d in loaded_entity_mapping.items()}
        
        ind2entity = {i: (Person(x) if type(x) is WholePerson else x)
                        for i, x in ind2entity.items()}
        
        with open(f"{load_mapping_of}.ind2pred.json") as handle:
            ind2pred = {int(i): d for i, d in json.load(handle).items()}
        
        
        with open(f"{name}.json") as handle:
            loaded = json.load(handle)    
        
        restored_triples = [(ind2entity[s],
                             ind2pred[p],
                             ind2entity[o]) for s, p, o in loaded]
                
        
        with open(f"{name}.provenances.json") as handle:
            provenances = json.load(handle)
            
        
        kg = KG(restored_triples, provenances)
        
        kg.translated = loaded
        kg.entity2ind = kg.reverse_mapping(ind2entity)
        kg.pred2ind = kg.reverse_mapping(ind2pred)
        
        return kg
    
    
    @staticmethod
    def reverse_mapping(d):
        rev_d = {}
        
        for k, v in d.items():
            if not v in rev_d:
                rev_d[v] = k
            else:
                print("duplicate:", v)
                if not type(v) is Person:
                    raise ValueError("Non-bijective mapping!")
        
        return rev_d
    
    
    def to_csv(self, save_path):
        raise DeprecationWarning("Deprecated; Use:\nfrom kgs.writers import CSVWriter\n"
                                 "CSVWriter(kg).to_csv(save_path)")
        
        
    @staticmethod
    def _merge_nodes(kg, node_type, distance_threshold):
        entities = kg.entities(lambda x: type(x) is node_type)
        merge_with = {}
        for x in entities:
            matches = [x2 for x2 in entities
                       if x.distance_from(x2) <= distance_threshold 
                          and not x == x2]
            
            merge_with[x] = set(matches)

        sorted_d = sorted(merge_with.items(), 
                          key=lambda it: (len(it[1]), -len(it[0].name)), 
                          reverse=True)

        merging_f = {}
        donotmerge = set()
        alreadymerged = set()

        for x, s in sorted_d:
            if not x in alreadymerged:
                for x2 in s:
                    if not x2 in donotmerge:   
                        merging_f[x2] = x
                        donotmerge.add(x)
                        alreadymerged.add(x2)
        
        return merging_f
    
        
    @classmethod
    def merge_persons_of(cls, kg, distance_threshold):
        merging_f = cls._merge_nodes(kg, Person, distance_threshold)

        replace = lambda entity: merging_f[entity]\
                        if entity in merging_f else entity
        
        new_triples = []

        for s, p, o in kg.triples:
            s_, o_ = replace(s), replace(o)
    
            if s_ == o_:
                print(s, p, o)
            else:
                new_triples.append((s_, p, o_))


        old_provenances = kg.provenances
        new_kg = cls(new_triples, old_provenances)
        new_kg.merge_mapping = merging_f
        
        return new_kg
