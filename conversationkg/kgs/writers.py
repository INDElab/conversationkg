from ..conversations.corpus import Conversation
from ..conversations.emails import Email



from collections import Counter
import matplotlib
import pandas as pd


class CSVWriter:
    
    def __init__(self, kg):
        self.kg = kg
        self.entities = kg.entities()

        
    def get_node_df(self):    
        records = []
        
        
        sorted_ents = sorted(self.entities, key=str)
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
    
    