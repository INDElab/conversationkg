import declarations.corpus
import declarations.topics

from declarations.corpus import EmailCorpus, Conversation
from declarations.topics import TopicModel
from declarations.entities import Person

import spacy
nlp = spacy.load("en_core_web_md")

from tqdm import tqdm
import json



import Levenshtein

# distance threshold value of around 0.3 seems to capture identity quite well
class OnlyNamePerson(Person):
    def __init__(self, person, distance_threshold=0.0):
        self.__dict__ = person.__dict__
        
        self.instance_label = self.instance_label.lower()
        self.thr = distance_threshold
    
    
    def distiance_from(self, other):
        my_name, your_name = self.instance_label, other.instance_label
        
        if max(len(my_name), len(your_name)) == 0:
            return 0.
        
        d = Levenshtein.distance(my_name, your_name)
        
        return d/max(len(my_name), len(your_name))
    
    
    def __hash__(self):
#        raise NotImplementedError
        return hash(self.instance_label)
        
    def __repr__(self):
        return f"OnlyNamePerson({self.instance_label if self.instance_label else 'NO_NAME'})"
        
    
    def __eq__(self, other):
        if not (type(self) == type(other)):
            return False
        return self.instance_label == other.instance_label
    
#    def __eq__(self, other):
#        if not (type(self) == type(other)):
#            return False
#        
##        if not self.instance_label and not other.instance_label:
##            return True
#        
#        return self.distiance_from(other) <= self.thr

    
#    def to_json(self, dumps=False):
#        json_d = super().to_json()
#        
#        json_d["class"] = "OnlyNamePerson"
#        
#        return json_d
#    
#    @classmethod    
#    def from_json(cls, json_dict):
#        print(json_dict)
#        print(super().from_json)
#        print(super())
#        person = super().from_json(json_dict)
#        print()
#        return cls(person)
        
    
import numpy as np



def put(d, x, i):
    if not x in d:
        d[x] = i
        i += 1
    return d[x], i
OnlyNamePerson

def put_based_on_eq(d, x, i):
    if not type(x) is OnlyNamePerson:
        return put(d, x, i)
    
    print(x.instance_label, end=", ")

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
    def from_email_corpus(cls, email_corpus, triples=[], distance_threshold=0.0):
        print(cls, type(email_corpus), type(triples))


#        if not self.triples:
#            raise NotImplementedError("Please instantiate KG via one of its subclasses!")
#        
        for conv in email_corpus:  # tqdm(email_corpus, desc="Iterating Conversations in KG"):
            
            for d in conv.documents:
                triples.append((conv, "mentions", d)) # both
            
            for email in conv:
                triples.append((email, "part_of", conv)) # both
                
                for link in email.body.links: 
                    triples.append((email, "mentions", link)) # both
                for addr in email.body.addresses:
                    triples.append((email, "mentions", addr)) # both
                for entity in email.body.entities: 
                    triples.append((email, "mentions", entity)) # both
        
        
        for c1, c2 in zip(email_corpus, email_corpus[1:]):
            triples.append((c1, "before", c2))
            
            for e1, e2 in zip(c1, c1[1:]):
                triples.append((e1, "before", e2))
        
        return cls(triples, distance_threshold)
    
    
    
    def __init__(self, triples, distance_threshold):
        self.triples = triples
        self.distance_threshold = distance_threshold
        
    
    def translate(self, entity2ind=None, pred2ind=None, attach=False):
        if entity2ind or pred2ind:
            assert entity2ind and pred2ind, "Please provide both entity2ind and pred2ind or none!"
            i = max(entity2ind.values()) + 1
            j = max(pred2ind.values()) + 1
        else:
            i = j = 0
            entity2ind, pred2ind = {}, {}
        
        put_ = put_based_on_eq
        
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
    def restore(cls, name, distance_threshold=0.0):
        def get_class(cls_name):
#            if cls_name == "OnlyNamePerson":
#                return OnlyNamePerson
            
            for mod in [declarations.corpus, declarations.emails, 
                        declarations.entities, declarations.topics]:
                try:
                    cls = getattr(mod, cls_name)
                    return cls
                except AttributeError:
                    pass
            raise AttributeError(f"{cls_name} could not be found in any of the modules!")
        
        
        def json_to_entity(json_dict):
#            print(json_dict)
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
        
        ind2entity = {i: (OnlyNamePerson(x, distance_threshold=distance_threshold) if type(x) is Person else x)
                        for i, x in ind2entity.items()}
        
        with open(f"{name}.ind2pred.json") as handle:
            ind2pred = {int(i): d for i, d in json.load(handle).items()}
        
        
        with open(f"{name}.json") as handle:
            loaded = json.load(handle)    
        
        restored_triples = [(ind2entity[s],
                             ind2pred[p],
                             ind2entity[o]) for s, p, o in loaded]
        
        kg = KG(restored_triples, distance_threshold=distance_threshold)
        
        kg.translated = loaded
        kg.entity2ind = kg.reverse_mapping(ind2entity)
        kg.pred2ind = kg.reverse_mapping(ind2pred)
        
        return kg
    
    
    @staticmethod
    def reverse_mapping(d):
#        if not len(d) == len(set(d.values())):
#            raise ValueError("Provided dict is not a bijective mapping!")
        
        rev_d = {}
        
        for k, v in d.items():
            if not v in rev_d:
                rev_d[v] = k
            else:
                print("duplicate:", v)
                if not type(v) is OnlyNamePerson:
                    raise ValueError("Non-bijective mapping!")
        
        
        
        return rev_d  # {v:k for k, v in d.items()}
    

    @staticmethod
    def intersect_persons(emailkg, textkg, getter_func=lambda x: x):
        is_person = lambda x: type(x) is Person
        emailkg_names = {getter_func(x) for x in emailkg.entities(is_person)}
    
        def keep(s, o, name_set):
            if not (is_person(s) or is_person(o)):
                return True
            
            if is_person(s) and is_person(o):
                if getter_func(s) in name_set or getter_func(o) in name_set:
                    return True
        
            if is_person(s):
                if getter_func(s) in name_set:
                    return True
        
            if is_person(o):
                if getter_func(o) in name_set:
                    return True
            return False
    
        new_triples = []
        for s, p, o in textkg.triples:
            
            if keep(s, o, emailkg_names):
                new_triples.append((s, p, o))
    
        return KG(new_triples)
    

#%%
        
    
    
class EmailKG(KG):
    def __new__(cls, email_corpus, distance_threshold=0.0):
        triples = []
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in EmailKG"):
            for p in conv.interlocutors:
                triples.append((OnlyNamePerson(p), "part_of", conv))
            
            for o in conv.organisations:
                triples.append((o, "part_of", conv))
            
            
            for email in conv:
                sender, receiver = OnlyNamePerson(email.sender, distance_threshold=distance_threshold),\
                                        OnlyNamePerson(email.receiver, distance_threshold=distance_threshold)
                
                triples.append((sender, "talked_to", receiver))
                triples.append((sender, "evidences", sender.address))
                triples.append((receiver, "evidences", receiver.address))
                
                
                triples.append((sender.organisation, 
                                     "talked_to", receiver.organisation))
                triples.append((sender, "evidences",
                                     sender.organisation))
                triples.append((receiver, "evidences",
                                     receiver.organisation))
        
        return KG.from_email_corpus(email_corpus, triples, distance_threshold)



class TextKG(KG):
    def __new__(cls, email_corpus, distance_threshold=0.0):
        triples = []
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in TextKG"):
            triples.append((conv, "is_about", conv.topic.topic))
            
            for email in conv:
                triples.append((email, "is_about", email.topic.topic))
                
                mentioned_people
                
                
                mentioned_people = [OnlyNamePerson(Person(str(e), "None"), distance_threshold=distance_threshold) 
                                    for e in nlp(str(email.body)).ents if e.label_ == "PERSON"]
                for person in mentioned_people:
                    triples.append((email, "mentions", person))
                    
                    for person2 in mentioned_people:
                        if not person == person2:
                            triples.append((person, "talked_to", person2))
        
        return KG.from_email_corpus(email_corpus, triples, distance_threshold)

    
#%%
        
    


#class EmailKG(KG):
#    def __new__(cls, email_corpus):
#        triples = []
#        
#        for conv in tqdm(email_corpus, desc="Iterating Conversations in EmailKG"):
#            for p in conv.interlocutors:
#                triples.append((p, "part_of", conv))
#            
#            for o in conv.organisations:
#                triples.append((o, "part_of", conv))
#            
#            
#            for email in conv:
#                triples.append((email.sender, "talked_to", email.receiver))
#                triples.append((email.sender, "evidences", email.sender.address))
#                triples.append((email.receiver, "evidences", email.receiver.address))
#                
#                
#                triples.append((email.sender.organisation, 
#                                     "talked_to", email.receiver.organisation))
#                triples.append((email.sender, "evidences",
#                                     email.sender.organisation))
#                triples.append((email.receiver, "evidences",
#                                     email.receiver.organisation))
#        
#        return KG.from_email_corpus(email_corpus, triples)
#
#
#
#class TextKG(KG):
#    def __new__(cls, email_corpus):
#        triples = []
#        
#        for conv in tqdm(email_corpus, desc="Iterating Conversations in TextKG"):
#            triples.append((conv, "is_about", conv.topic.topic))
#            
#            for email in conv:
#                triples.append((email, "is_about", email.topic.topic))
#                
#                mentioned_people = [Person(str(e), "None") for e in nlp(str(email.body)).ents 
#                                    if e.label_ == "PERSON"]
#                for person in mentioned_people:
#                    triples.append((email, "mentions", person))
#                    
#                    for person2 in mentioned_people:
#                        if not person == person2:
#                            triples.append((person, "talked_to", person2))
#        
#        return KG.from_email_corpus(email_corpus, triples)