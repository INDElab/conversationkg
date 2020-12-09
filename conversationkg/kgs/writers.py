from ..conversations.corpus import Conversation
from ..conversations.emails import Email



from collections import Counter
import matplotlib
import pandas as pd

import json


class JSONWriter:
    def __init__(self, kg):
        self.kg = kg
        self.entities = kg.entities()
        self.triples = kg.triples
        self.provenances = kg.provenances



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






class CSVWriter:
    def __init__(self, kg):
        self.kg = kg
        self.entities = kg.entities()
        self.triples = kg.triples
        self.provenances = kg.provenances
        
    def get_node_df(self):    
        records = []
        
        
        sorted_ents = sorted(self.entities, key=lambda x: (str(type(x)), str(x)))
        for i, e in enumerate(sorted_ents):                
            node_id = i  # hash(e)
            node_t = str(e)
            node_type = type(e).__name__
            node_u = f"icons/{node_type.lower()}.png"
            
            type_ = "LinkChart" if i == 0 else "0"
                
            if type(e) in {Conversation, Email}:
                node_dtopic = e.topic.topic.index
                node_dtopic_rate = round(e.topic.score, 5)
            else:
                node_dtopic = -1
                node_dtopic_rate = 1.0
                
            lat = lng = 0.0
            
            
            records.append(
                    (
                          type_, node_type, node_id, node_u, node_t, 
                          node_dtopic, node_dtopic_rate, lat, lng  
                    )
            )
            
            
        return pd.DataFrame.from_records(records, 
                                         columns= ['type', 
                                                   'node_type', 
                                                   'node_id', 
                                                   'node_u', 
                                                   'node_t', 
                                                   'node_dtopic',
                                                   'node_dtopic_rate', 
                                                   'lat', 
                                                   'lng']
                                         )
        
        
    def get_link_df(self):
        link_types = {p for s, p, o in self.triples}
        link_counts = Counter(self.triples)
        colours = dict(zip(link_types, list(matplotlib.colors.cnames.values())))
        
        sorted_ents = dict(zip(sorted(self.entities, key=str),
                               range(len(self.entities))))
        
        records = []
        for i, ((s, p, o), prov) in enumerate(zip(self.triples, self.provenances)):
            linkId = i  # hash((s, p, o))  # s.time.timestamp()
            end1 = sorted_ents[s]  # hash(s)
            end2 = sorted_ents[o]  # hash(o)
            linkcount = link_counts[(s,p,o)]
            linkcolor = colours[p]
            linktype = p
            itemID = prov
            
            rec = [linkId, 
                   end1, 
                   end2, 
                   linkcount,
                   linkcolor,
                   itemID,
                   linktype]
        
            records.append(rec)
        
        return pd.DataFrame.from_records(records, 
                                         columns=['linkId', 'end1', 'end2', 'linkcount', 'linkcolor', 'itemID', 'linktype'])
    
            
    def to_csv(self, save_path):
        node_df = self.get_node_df()
        link_df = self.get_link_df()
        
        node_df.to_csv(save_path + ".nodes.csv", 
                         index=False)
        link_df.to_csv(save_path + ".links.csv", 
                         index=False)
        
        
        






from neo4j import GraphDatabase      

class Neo4jWriter:
    
    def __init__(self, kg):
        self.kg = kg



    def to_neo4j(self):
        pass
    
    
    
    
    def run(self, clear=True):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", 
                                      auth=("neo4j", "pwd"), encrypted=False)

        if clear:
            tx.run("""MATCH (x)
                DETACH DELETE x""")
    
    