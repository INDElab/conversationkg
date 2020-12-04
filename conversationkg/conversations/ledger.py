# -*- coding: utf-8 -*-

import json
import importlib



#%%


#class Universe(type):
#    d = {}
#    
#    def __call__(cls, *args, **kwargs):
#        obj = type.__call__(cls, *args, **kwargs)
#        
#        if hash(obj) in Universe.d:
#            print(f"found {obj} in d")
#            return Universe.d[hash(obj)]
#        
#        else:
#            print(f"{obj} not in d")
#            Universe.d[hash(obj)] = obj
#            return obj
#        
#        
#class X(metaclass=Universe):
#    def __init__(self, x):
#        self.x = x
#    
#    def __hash__(self):
#        return hash(self.x)
        
#%%


import datetime

class Universe(type):
    current_timer = None
    current_time = datetime.datetime(1, 1, 1)
    observed = dict()
    
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        return obj
    
#        obj = type.__call__(cls, *args, **kwargs)
#        
#        if hasattr(obj, "time"):
#            Universe.current_timer = obj
#            Universe.current_time = obj.time
##            print(f"obj of type {obj.__class__.__name__}")
#
#        if hash(obj) in Universe.observed:
#            return Universe.observed[hash(obj)]
#        else:
#            if not hasattr(obj, "time_first_observed"):
#                obj.time_first_observed = []
#            obj.time_first_observed.append(Universe.current_time)
#            Universe.observed[hash(obj)] = obj
#            return obj
            
    @classmethod
    def observe(cls, obj, witness, mode):
        pass






# a.k.a. Ledger, FactUniverse
#class Universe(type):        
#    mentioned_in = dict()
#    evidenced_by = dict()
#    
#    nothing_to_register = []
#    def __call__(cls, *args, **kwargs):
#        obj = type.__call__(cls, *args, **kwargs)
#        
#        if "evidenced_by" in kwargs:
#            witness = kwargs["evidenced_by"]
#            Universe.observe(obj, witness, "evidenced_by")
#            
#        elif "mentioned_in" in kwargs:
#            witness = kwargs["mentioned_in"]
#            Universe.observe(obj, witness, "mentioned_in")
#            
#        else:
#            Universe.nothing_to_register.append(obj)
#
#        return obj
#    
#    @classmethod
#    def reset(cls):
#        cls.mentioned_in = dict()
#        cls.evidenced_by = dict()
#        
#    @classmethod 
#    def observe(cls, obj, witness, mode):    
##        print(obj, mode)
#        
#        mode_dict = getattr(cls, mode)    
##        obj_cls = type(obj)
##        witness_cls = type(witness)
#        k, v = obj, witness
#        if not k in mode_dict:
#            mode_dict[k] = []
#        mode_dict[k].append(v)
        
#    @classmethod
#    def to_json(cls, dumps=False):
#        raise NotImplementedError()
#    
#    @classmethod
#    def from_json(cls, json_dict):
#        raise NotImplementedError()
        
        
#%%        
        
"""
IDEA

instantiate Universe in an object, make ledgers object specific and override the __call__ function to 


"""
        
# a.k.a. Ledger, FactUniverse
class Universe2(type):        
    mentioned_in = dict()
    evidenced_by = dict()
    nothing_to_register = []
    
    name = "Universe"
    bases = object,
    
    def __new__(cls, *args):
        print(args)
        return super().__new__(cls, cls.name, cls.bases, dict())
    
    def __init__(self, *args):
        self.mentioned_in = {}
        self.evidenced_by = {}
        self.nothing_to_register = []
        
        print(self)
        self.__class__.__call__ = self.call_self #self.get_call_self()
    
    def call_self(self, *args, **kwargs):
        print("SELF:", self)
        obj = type.__call__(self.__class__, *args, **kwargs)
        self.evidenced_by[hash(obj)] = obj
        return obj
        

    
    
    
    def get_call_self(self):
        def call_self(cls, *args, **kwargs):
            obj = cls.__call__(*args, **kwargs)
            return obj
        return call_self
            
    def __call__(cls, *args, **kwargs):
        print(args)
        universe_obj = cls
        if "self" in kwargs:
            print("SELF:", kwargs["self"])
            universe_obj = kwargs["self"]
            
        print(cls, isinstance(cls, Universe))
        obj = type.__call__(cls, *args, **kwargs)
        
        universe_obj[hash(obj)] = obj
#        
#        if "evidenced_by" in kwargs:
#            witness = kwargs["evidenced_by"]
#            universe_obj.observe(obj, witness, "evidenced_by")
#            
#        elif "mentioned_in" in kwargs:
#            witness = kwargs["mentioned_in"]
#            universe_obj.observe(obj, witness, "mentioned_in")
#            
#        else:
#            universe_obj.nothing_to_register.append(obj)

        return obj
    
    @classmethod
    def reset(cls):
        cls.mentioned_in = dict()
        cls.evidenced_by = dict()
        
    @classmethod 
    def observe(cls, obj, witness, mode):        
        mode_dict = getattr(cls, mode)    
        k, v = obj, witness
        if not k in mode_dict:
            mode_dict[k] = []
        mode_dict[k].append(v)
        
    @classmethod
    def to_json(cls, dumps=False):
        raise NotImplementedError()
    
    @classmethod
    def from_json(cls, json_dict):
        raise NotImplementedError()

#%%        


#class X(metaclass=Universe):
#    def __new__(cls, x):
#        print("new", x)
#        self = super().__new__(cls)
#        return self
#    
#    def __init__(self, x):
#        print("hello", x)
#        self.x = x
#        
#    def __hash__(self):
#        return hash((self.__class__.__name__, self.x))
        
#%%




#class Conversation(tuple):
#    def __new__(cls, email_args):
#        self =  super().__new__(cls, (Email(*args) for args in email_args))
#        for email in self:
#            Universe.observe(email, self, "evidenced_by")
#        return self
#    
#    
#
#
#
#class Email(metaclass=Universe):
#    def __init__(self, body, sender, receiver):        
#        self.body = Body(body, evidenced_by=self)
#        
#        self.entities = [Person(w, "", mentioned_in=self.body) for w in self.body.split(" ")]
#        
#        self.sender = Person(*sender, evidenced_by=self)
#        self.receiver = Person(*receiver, evidenced_by=self)
#        
#    def __hash__(self):
#        return hash((self.body, self.sender, self.receiver))
#
#
#class EntityUniverse(Universe):
#    entities = set()
#    def __call__(cls, *args, **kwargs):
#        obj = Universe.__call__(cls, *args, **kwargs)
#        
#        EntityUniverse.entities.add(obj)
#        
#        return obj
#
#
#class Entity(metaclass=EntityUniverse):
#    def __init__(self, name, **kwargs):
#        self.name = name
#        
#        
#    def __hash__(self):
#        return hash(self.name)
#
#    def __str__(self):
#        return repr(self)
#        
#    def __repr__(self):
#        return str(self.name)
#
#
#class Person(Entity):
#    def __init__(self, name, address, **kwargs):
#        super().__init__(name)
#        
#        self.address = address
#
#    def __hash__(self):
#        return hash((self.name, self.address))
#    
#        
#class Body(str, metaclass=Universe):
#    def __new__(cls, body, **kwargs):
#        return super().__new__(cls, body)
#        
#    def __init__(self, body, **kwargs):
#        pass
