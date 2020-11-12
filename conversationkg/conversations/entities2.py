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
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict["name"])
    
    
class EntityInstance(metaclass=EntityUniverse):
    def __init__(self, label, score):
        self.entitiy = Entity(label)
        self.label = label
        self.score = score
        
    def __eq__(self, other):
        if not isinstance(other, EntityInstance):
            return False
        return (self.entity, self.score) == (other.entity, other.score)
    
    def __hash__(self):
        return hash((self.entity, self.score))
    
    def repr(self):
        return f"EntityInstance({self.label}, {self.score})"
    
    
    def to_json(self, dumps=False):
        d = dict(entity=self.entity.to_json(dumps=False),
                 label=self.label, score=self.score)
        if dumps: return json.dumps(d)
        return d
    
    
    @classmethod
    def from_json(cls, json_dict):
#        entity = Entity.from_json(json_dict["entity"])
        label, score = json_dict["label"], json_dict["score"]
        return cls(label, score)
    
    
class Person(EntityInstance):
    
    def __init__(self, name, address, score=None):
        if not name: name = ""        
        name = name.strip("'").strip('"').replace("\n", " ")

        if name == self.address.lower():
            name = ""
        self.name = name
        self.address = Address(address)
        Universe.observe(self.address, self, "evidenced_by")        
        self.organisation = self.address.org_from_address

        super().__init__(name, score=None)


    def __repr__(self):
        return f"Person({self.name if self.name else 'NO_NAME'}, {self.address})"
    
    def __hash__(self):
        return hash((super().__hash__(), self.address))
    
    
    def __eq__(self, other):
        if not (type(self) == type(other) == Person):
            return False
        return hash(self) == hash(other)
    
    def to_json(self, dumps=False):
        d = super().to_json(dumps=False)
        d["address"] = self.address.instance_label
        d["organisation"] = self.organisation.to_json(dumps=False) if self.organisation is not None else None
        d["class"] = "Person"
        if dumps: return json.dumps(d)
        return d
        
    @classmethod
    def from_json(cls, json_dict):
        name = json_dict["instance_label"]
        address = json_dict["address"]
        
        entity_params = json_dict["entity"]
        
        person = cls(name, address, **entity_params)
        return person
    
    
class Organisation(EntityInstance):
    def __init__(self, name, domain, score=None):
        pass
    
class Address(EntityInstance, str):
    def __init__(self, address):
        pass
    

class Link(EntityInstance):
    def __init__(self, url):
        pass