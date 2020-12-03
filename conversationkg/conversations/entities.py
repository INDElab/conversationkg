# -*- coding: utf-8 -*-

from .ledger import Universe

from urllib.parse import urlparse

import numpy as np


#%%

#class Universe(type):
#    def __call__(cls, *args, **kwargs):
#        obj = type.__call__(cls, *args, **kwargs)
#        return obj


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
#        for name, val in other_properties:
#            setattr(self, name, val)

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        return self.name == other.name
    
    # hash __class__ to ensure different entity types are discernible by hash
    def __hash__(self):
        return hash((self.__class__, self.name)) 
  
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    
    def __str__(self):
        return f"{self.name}"
    
    def to_json(self):
        d = dict(name=self.name)
        d["class"] = self.__class__.__name__
#        d["class"] = "Entity"
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        if not cls.__name__ == json_dict["class"]:
            raise ValueError(f"Passed JSON dict for class {json_dict['class']} "
                             f"to {cls.__name__}")
        
        return cls(json_dict["name"])
        
        
    
class Person(Entity):
    def __init__(self, name, address):            
        self.address = Address(address)               
        self.organisation = self.address.org_from_address
        
        if not name: name = ""        
        name = name.strip("'").strip('"').replace("\n", " ")
        if name == self.address.name.lower():
            name = ""        
        
        super().__init__(name)
    
    def __eq__(self, other):
        return super().__eq__(other) and self.address == other.address
    
    def __hash__(self):
        return hash((super().__hash__(), self.address))
    
    def __repr__(self):
        return f"Person({self.name}, {self.address.name})"
    
    def __str__(self):
        return f"{self.name} <{self.address.name}>"
    
    def to_json(self):
        d = super().to_json()
        d["address"] = self.address.name
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict["name"],
                   json_dict["address"])
        
        
class Organisation(Entity):
    def __init__(self, name, domain):
        self.domain = domain
        super().__init__(name)
        
    def __eq__(self, other):
        return super().__eq__(other) and self.domain == other.domain
    
    def __hash__(self):
        return hash((super().__hash__(), self.domain))
        
    
    def __repr__(self):
        return f"Organisation({self.name}, {self.domain})"
    
    def __str__(self):
        return f"{self.name} <{self.domain}>"

    def to_json(self):
        d = super().to_json()
        d["domain"] = self.domain
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict["name"],
                   json_dict["domain"])



# could also be called SimpleEntity, 
# since it really only consists of a name (and is of type str)
class StringEntity(Entity, str):
    def __new__(cls, string):
        return str.__new__(cls, string)
    
    def __init__(self, string):
        Entity.__init__(self, string)
          
    
class Address(StringEntity):
    def __new__(cls, address):
        if not address: address = ""
        domain = address[address.rfind("@")+1:]
        if not domain: address = ""
        return super().__new__(cls, address)

    def __init__(self, address):
        domain = address[address.rfind("@")+1:]
        self.domain = domain
        self.local_part = address[:address.rfind("@")]
        
        domain_prefix = domain[:domain.find(".")]
        self.org_from_address = Organisation(domain_prefix, domain)
        super().__init__(address)
        
        

class Link(StringEntity):
    def __init__(self, url):
        try:
            parsed = urlparse(url)
            self.domain = parsed.netloc
            self.path = parsed.path
        except ValueError:
            self.domain = None
            self.path = None
        super().__init__(url)

        
class KeyWord(StringEntity, str):
    pass



class Topic(Entity):
    def __init__(self, index, word_dist, words=None):
        self.index = index
        self.word_dist = np.asarray(word_dist)
        self.word_dist.flags.writeable = False
        self.words = words if words else range(self.word_dist.size)
        self.sorted_words = tuple(self.words[i] for i in self.word_dist.argsort())
        
        super().__init__(str(index))
        
        
    def top_words(self, n, include_probs=False):
        if include_probs:
            return [(self.word_dist[i], KeyWord(self.words[i])) 
                    for i in self.word_dist.argsort()[:n]]
        return [KeyWord(w) for w in self.sorted_words[:n]]
    
    def __str__(self):
        return f"Topic {self.index}: " + f"{list(map(str, self.top_words(5)))}"[1:-1]
    
    def __repr__(self):
        probs, words = list(zip(*self.top_words(5, include_probs=True)))
        return f"Topic({self.index}, {probs}, {words})"
    
    def __hash__(self):
        return hash((self.index, self.word_dist.tostring()))
    
    def __eq__(self, other):
        if not isinstance(other, Topic):
            return False
        return self.index == other.index and np.array_equal(self.word_dist, other.word_dist)
    
    
    def to_json(self):
        return {"class": self.__class__.__name__,
                "index": self.index,
                "words": self.words,
                "word_dist": self.word_dist.tolist()}
    
    @classmethod
    def from_json(cls, json_dict):
        params = [json_dict[k] for k in ["index", "word_dist", "words"]]
        return cls(*params)


class TopicInstance:  
    def __init__(self, topic, confidence):
        self.topic = topic
        self.index = topic.index
        self.score = confidence
        
    def __str__(self):
        return f"Prob[{self.topic}] = {self.score:0.3f}"
    
    def __repr__(self):
        return f"TopicInstance({repr(self.topic)}, {self.score})"
    
    def __eq__(self, other):
        if isinstance(other, Topic):
            return self.topic == other
        elif isinstance(other, TopicInstance):
            return self.topic == other.topic
        else:
            return False
        
    def __hash__(self):
        return hash(self.topic)
    
    def to_json(self):
        d = {"class":self.__class__.__name__, "score":self.score}
        d["topic"] = self.topic.to_json(dumps=False)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        topic = Topic.from_json(json_dict["topic"])
        score = json_dict["score"]
        return cls(topic, score)
    


    

    
#class DynamicEntity(metaclass=EntityUniverse):
    
    
        