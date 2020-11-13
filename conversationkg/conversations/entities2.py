# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse

from .ledger import Universe


class EntityUniverse(type, metaclass=Universe):
    entities = dict()
    n_duplicates = 0
    duplicates = set()
    
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)  

        if hash(obj) in EntityUniverse.entities:
            EntityUniverse.n_duplicates += 1
            EntityUniverse.duplicates.add(obj)
            return EntityUniverse.entities[hash(obj)]
        else:
            EntityUniverse.entities[hash(obj)] = obj
            return obj
    
    @classmethod
    def reset(cls):
        cls.entities = dict()
        cls.n_duplicates = 0
        cls.duplicates = set()


class Entity(metaclass=EntityUniverse):
    def __init__(self, name):
        self.name = name
        
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.name == other.name
    
    def __repr__(self):
        return f"Entity({self.name})"
    
    def to_json(self, dumps=False):
        d = dict(name=self.name)
        d["class"] = "Entity"
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict["name"])
    
    
class EntityInstance(metaclass=EntityUniverse):
    def __init__(self, label, score, entity=None):
        self.entitiy = Entity(label) if not entity else entity
        self.label = label
        self.score = score
    
    def __eq__(self, other):
        if not isinstance(other, EntityInstance):
            return False
        return (self.entity, self.label, self.score) == (other.entity, other.label, other.score)
    
    def __hash__(self):
        return hash((self.entity, self.score))
    
    def repr(self):
        return f"EntityInstance({self.label}, {self.score})"
    
    def to_json(self, dumps=False):
        d = dict(entity=self.entity.to_json(dumps=False),
                 label=self.label, 
                 score=self.score)
        d["class"] = "EntityInstance"
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        entity = Entity.from_json(json_dict["entity"])
        label, score = json_dict["label"], json_dict["score"]
        return cls(label, score, entity)
    
    
class Person(EntityInstance):
    def __init__(self, name, address): # , **kwargs):
        self._name = name
        if not name: name = ""        
        name = name.strip("'").strip('"').replace("\n", " ")

        if name == self.address.lower():
            name = ""
        self.name = name
        self.address = Address(address)
        self.organisation = self.address.org_from_address
        super().__init__(name, **kwargs)

    def __repr__(self):
        return f"Person({self.name if self.name else 'NO_NAME'}, {self.address})"
    
    def __hash__(self):
        return hash((super().__hash__(), self.address))
    
    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        return super().__eq__(other) and self.address == other.address
    
    def to_json(self, dumps=False):
        d = super().to_json(dumps=False)
        d["address"] = self.address.to_json(dumps=False)
        d["class"] = "Person"
#        d["organisation"] = self.organisation.to_json(dumps=False) if self.organisation is not None else None
        if dumps: return json.dumps(d)
        return d

# TODO: 
#    @classmethod
#    def from_json(cls, json_dict):
#        name = json_dict["label"]
#        address = json_dict["address"]
#        entity_instance = EntityInstance.from_json(json_dict)
#        
#        
#        name = json_dict["instance_label"]
#        address = json_dict["address"]
#        
#        entity_params = json_dict["entity"]
#        
#        person = cls(name, address, **entity_params)
#        return person

class Address(EntityInstance, str):
    def __new__(cls, address):
        self = str.__new__(cls, address)
        return self
        
    def __init__(self, address, score=None):
        self.local_part = address[:address.rfind("@")]

        domain_prefix = domain[:domain.find(".")]
        domain = address[address.rfind("@")+1:]
        self.domain = domain        
        self.org_from_address = Organisation(domain_prefix, domain)
        
        EntityInstance.__init__(self, address, score)
        
    def __repr__(self):
        return f"Address({str(self)})"
    
    def __hash__(self):
        return hash(super().__hash__(), str(self))
    
    def __eq__(self, other):
        return super().__eq__(other) and str(self) == str(other)
    
    def to_json(self, dumps=False):
        pass
    
    @classmethod
    def from_json(cls, json_dict):
        pass        

    
class Organisation(EntityInstance):
    def __init__(self, name, domain, score=None):
        pass
    
    
    def __repr__(self):
        pass
    
    def __hash(self):
        pass
    
    def __eq__(self, other):
        pass
    
    def to_json(self, dumps=False):
        pass
    
    @classmethod
    def from_json(cls, json_dict):
        pass
    
    

class Link(EntityInstance, str):
    def __new__(cls, url):
        self = str.__new__(cls, url)
        return self
        
    def __init__(self, url):
        pass
    
    
    def __repr__(self):
        pass
    
    def __hash(self):
        pass
    
    def __eq__(self, other):
        pass
    
    def to_json(self, dumps=False):
        pass
    
    @classmethod
    def from_json(cls, json_dict):
        pass
    
    
    
class KeyWord(EntityInstance, str):
    def __new__(cls, phrase):
        self = str.__new__(cls, phrase)
        return self
        
    def __init__(self, phrase):
        pass
    
    
    def __repr__(self):
        pass
    
    def __hash(self):
        pass
    
    def __eq__(self, other):
        pass
    
    def to_json(self, dumps=False):
        pass
    
    @classmethod
    def from_json(cls, json_dict):
        pass