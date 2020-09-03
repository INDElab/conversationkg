# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse

from declarations.ledger import Universe


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
        
#    @classmethod
#    def to_json(cls, dumps=False):
#        entities_json = [e.to_json() for e in cls.entities.values()]
#        if dumps: json.dump(entities_json)
#        return entities_json
#    
#    @classmethod
#    def from_json(cls, json_dict):
#        cls.reset()
#        module = importlib.import_module("declarations_new.entities")
#        for entity_dict in json_dict:
#            class_ = getattr(module, entity_dict["class"])
#            yield class_.from_json(entity_dict)


class Entity:
#    arg_names = ["qid", "label", "description", "aliases", "edges", "types"]
    # TODO meaningful default args => "default entity"?
    def __init__(self, qid=None, label=None, description=None, aliases=None, edges=None, types=None):
        self.qid = qid
        
        self.label = label
        self.description = description      
        self.aliases = aliases
        
        self.edges = edges
        self.types = types
        
    def __hash__(self):
        return hash(self.qid)
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.qid == other.qid
    
    def __repr__(self):
        return f"{self.label} ({self.qid})"
        
    
    def to_json(self, dumps=False):
        d = {k:v for k, v in self.__dict__.items()}
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)
    
    
class EntityInstance(metaclass=EntityUniverse):
    @classmethod
    def from_tapioca_api(cls, text, result_dict, **kwargs):        
        start, end = result_dict["start"], result_dict["end"]
        instance_label = text[start:end]
        
        instance_nll = result_dict["log_likelihood"]
        
        best = max(result_dict["tags"], key=lambda d: d["score"])
        keys = ["id", "label", "desc", "aliases", "edges", "types"]
        entity_params = {k.replace("id", "qid").replace("desc", "description"): best[k] 
                                for k in keys}
        if len(entity_params["label"]) > 1:
            raise ValueError("More than one label!")
        entity_params["label"] = entity_params["label"][0]
        best_score, best_page_rank = best["score"], best["rank"]      
        
        rest = [(d["id"], d["score"], d["rank"]) for d in result_dict["tags"] if not d == best]        
        
        return cls(entity_params, instance_label, instance_nll,
                   best_score, best_page_rank, rest)
        
#        if result_dict["best_qid"]:
#            pass
#        else:
#            pass
        
        
    # TODO meaningful default args => "default entity"?
    def __init__(self, entity_params={}, instance_label=None, 
                 instance_score=None, score=None, page_rank=None, alternative_entities=None, **kwargs):
        self.entity = Entity(**entity_params)
        
        self.instance_label = instance_label
        self.instance_score = instance_score
        self.score = score
        self.page_rank = page_rank
        self.alternative_entities = alternative_entities # list of (QID, score)
                
    def __repr__(self):
        return repr(self.entity)
    
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return repr(self) == repr(other)
    
    def __hash__(self):
        return hash(self.entity)
        
    
    def to_json(self, dumps=False):
        d = {k:v for k, v in self.__dict__.items()}
#        print(self.__class__, self.instance_label, self.entity)
        
#        if isinstance(self.entity, dict):
#            d["entity"] = self.entity
##        else:
        d["entity"] = self.entity.to_json(dumps=False)
        if dumps: return json.dumps(d)
        return d
    

    @classmethod
    def from_json(cls, json_dict):
        ent = json_dict["entity"]
        del json_dict["entity"]
        entity_in_context = cls(**json_dict)
        entity_in_context.entity = Entity.from_json(ent)
        return entity_in_context

class Person(EntityInstance):
    def __init__(self, name, address, **entity_params):
        super().__init__(entity_params)
        
#        if not address: 
#            self.address = None
#            self.organisation = None
#        else:
            
        self.address = Address(address)        
        Universe.observe(self.address, self, "evidenced_by")        
        self.organisation = self.address.org_from_address
        
        
        if not name: name = ""        
        if name == self.address.instance_label.lower():
            name = ""
        name = name.strip("'").strip('"')
        self.instance_label = name
        
        
    def __repr__(self):
        return f"Person({self.instance_label if self.instance_label else 'NO_NAME'}, {self.address})"
    
    def __hash__(self):
        return hash((super().__hash__(), self.instance_label, self.address))
    
    
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
    def __init__(self, name, domain, **entity_params):
        super().__init__(entity_params=entity_params, 
             instance_label = name)
        
        self.domain = domain
        
    def __repr__(self):
        return f"Org({self.instance_label if self.instance_label else 'NO_NAME'}, {self.domain})"
    
    def __hash__(self):
        return hash((super().__hash__(), self.instance_label, self.domain))
    
    def to_json(self, dumps=False):
        d = super().to_json(dumps=False)
        d["domain"] = self.domain
        d["class"] = "Organisation"
        
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        name = json_dict["instance_label"]
        domain = json_dict["domain"]
        entity_params = json_dict["entity"]
        org = cls(name, domain, **entity_params)
        return org
    
    
class Address(EntityInstance, str):
    def __new__(cls, address, **entity_params):
        if not address: return str.__new__(cls, "")
        domain = address[address.rfind("@")+1:]
        if not domain: return str.__new__(cls, "")
        return str.__new__(cls, address)

    
    def __init__(self, address, **entity_params):
        EntityInstance.__init__(self, entity_params=entity_params,
                    instance_label=address)
        
        domain = address[address.rfind("@")+1:]
        self.domain = domain
        self.local_part = address[:address.rfind("@")]
        
        domain_prefix = domain[:domain.find(".")]
        self.org_from_address = Organisation(domain_prefix, domain)
        Universe.observe(self.org_from_address, self, "mentioned_in")
    
    
    def __repr__(self):
        return f"Address({self.instance_label})"

    def __hash__(self):
        return hash((super().__hash__(), self.instance_label))

    def to_json(self, dumps=False):
        d = super().to_json(dumps=False)
        d["org_from_address"] = self.org_from_address.to_json(dumps=False)
        
        d["class"] = "Address"
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        addr = json_dict["instance_label"]
        entity_params = json_dict["entity"]
        address = cls(addr, **entity_params)
        return address
        
    
    
class Link(EntityInstance):
    def __init__(self, url, **entity_params):        
        try:
            parsed = urlparse(url)
            self.domain = parsed.netloc
            self.path = parsed.path
        except ValueError:
            self.domain = None
            self.path = None
        
        super().__init__(entity_params=entity_params,
                 instance_label=url)
        
    def __repr__(self):
        return f"Link({self.instance_label})"
    
    def __hash__(self):
        return hash((super().__hash__(), self.instance_label))
    
    def to_json(self, dumps=False):
        d = super().to_json(dumps=False)
        
        d["class"] = "Link"
        
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        url = json_dict["instance_label"]
        entity_params = json_dict["entity"]
        link = cls(url, **entity_params)
        return link