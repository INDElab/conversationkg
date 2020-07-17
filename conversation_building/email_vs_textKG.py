# -*- coding: utf-8 -*-

import json
from tqdm import tqdm
from declarations.corpus import EmailCorpus, Conversation

import spacy
nlp = spacy.load("en")

from neo4j import GraphDatabase


class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", 
                                      auth=("neo4j", "pwd"), encrypted=False)
        
    
    def clear(self, tx):
        tx.run("""MATCH (x)
                DETACH DELETE x""")
 
    
    def put_conversation(self, tx, conversation):
        subject_escaped = conversation.subject.replace('"', '\\"')
        subject_escaped = conversation.subject.replace("'", "\\")
        #    subject_escaped = conversation.subject.replace('\\', '\\')
        
        if not subject_escaped:
            print("NO SUBJECT:", hash(conversation))
        
        tx.run("""
               MERGE (c:Conversation {id:$h}) 
               ON CREATE SET c.subject = $subj
               ON CREATE SET c.length = $n_emails
               ON CREATE SET c.start = $start
               ON CREATE SET c.end = $end
               """,
               h=hash(conversation), #h=subject_escaped[:20] + "...", 
               subj=subject_escaped,
               n_emails=len(conversation),
               start=conversation.start_time.strftime("%d.%m.%Y, %H:%M"), 
               end=conversation.end_time.strftime("%d.%m.%Y, %H:%M"))
    
    
    def put_email(self, tx, conv, email):
        tx.run("""
                MATCH (c:Conversation {id:$h_c})
                MERGE (e:Email {id:$h})            
                ON CREATE SET e.time = $time
                ON CREATE SET e.subject = $subject            
                MERGE (c)-[rel:consists_of]->(e)
               """, 
                h_c=hash(conv),
                h = hash(email), time=email.time.strftime("%d.%m.%Y, %H:%M"),
               subject=email.subject)    
    
    
    def connect_email(self, tx, email, p):
        tx.run("""
            MATCH (e:Email {id:$h_e})
            MATCH (p:Person {label:$n})
            MERGE (e)-[rel2:mentions]->(p)
        """, h_e=hash(email), n=p)

    def connect_persons(self, tx, p1, p2):
        tx.run("""
            MATCH (p1:Person {label:$n1})       
            MATCH (p2:Person {label:$n2})
            MERGE (p1)-[rel:talked_to]->(p2)
        """, n1=p1, n2=p2)
        
    def before(self, tx, event1, event2):
        cls1, cls2 = event1.__class__.__name__, event2.__class__.__name__
        cmd = f"""
            MATCH (e1:{cls1} {{id: $h1}})
            MATCH (e2:{cls2} {{id: $h2}})
            MERGE (e1)-[rel:before]->(e2)
            """
        param_d = dict(h1=hash(event1), h2=hash(event2))
        tx.run(cmd, **param_d)



class EmailGraphBuilder(GraphBuilder):
    def __init__(self, corpus):
        super().__init__()
        
        with self.driver.session() as session:
            session.write_transaction(self.clear)
            
            for conversation in tqdm(corpus):
                session.write_transaction(self.put_conversation, conversation)
                for email in conversation:
                    session.write_transaction(self.put_email, conversation, email)
                    s, r = email.sender.instance_label, email.receiver.instance_label
                    
                    print(s, r)
                    
                    session.write_transaction(self.put_person, s)
                    session.write_transaction(self.put_person, r)
                    
                    session.write_transaction(self.connect_email, email, s)
                    session.write_transaction(self.connect_email, email, r)
                    
                    session.write_transaction(self.connect_persons, s, r)
    
    
            for conv1, conv2 in tqdm(zip(corpus, corpus[1:]), total=len(corpus),
                                     desc="before conversations"):
                session.write_transaction(self.before, conv1, conv2)
        
        
            for conv in tqdm(corpus, desc="before emails"):
                for e1, e2 in zip(conv, conv[1:]):
                    session.write_transaction(self.before, e1, e2)
    
    
    
    def put_person(self, tx, p):
        tx.run("""
            MERGE (p:Person {label:$l})       
        """, l=p)



class TextGraphBuilder(GraphBuilder):   
    def __init__(self, corpus):
        super().__init__()
        persons = self.collect_persons(corpus)
        
        with self.driver.session() as session:
            session.write_transaction(self.clear)
            session.write_transaction(TextGraphBuilder.put_persons, persons)
            
            for conversation, c in tqdm(zip(corpus, persons),
                                        total=len(corpus)):
                session.write_transaction(self.put_conversation, conversation)
                for email, em in zip(conversation, c):
                    session.write_transaction(self.put_email, conversation, email)
                    for ent1 in em:
                        session.write_transaction(self.connect_email,
                                                  email, ent1.text)
                        for ent2 in em:
                            if not ent2 == ent1:
                                session.write_transaction(self.connect_persons,
                                                          ent1.text, ent2.text)
                                
            for conv1, conv2 in tqdm(zip(corpus, corpus[1:]), total=len(corpus),
                                     desc="before conversations"):
                session.write_transaction(self.before, conv1, conv2)
        
        
            for conv in tqdm(corpus, desc="before emails"):
                for e1, e2 in zip(conv, conv[1:]):
                    session.write_transaction(self.before, e1, e2)
                    

    def get_entities(self, text):
        return nlp(str(text)).ents
        
             
    def collect_persons(self, corpus):
        return [[[e for e in self.get_entities(email.body) 
                  if e.label_ == "PERSON"] 
                  for email in conversation] for conversation in corpus]
    
    @staticmethod
    def put_persons(tx, person_lists):
        person_set = {e for conv in person_lists 
                        for email in conv for e in email}

        cmd = ""
        d = {}
        for j, person in enumerate(person_set):
            cmd += f"\n MERGE (p{j}:Person {{label:$name{j}}})"
            d[f"name{j}"] = person.text
        
        tx.run(cmd, **d)
        
        return cmd, d


if __name__ == "__main__":
    
    i = 10
    mailinglist = "public-credentials" # "ietf-http-wg"

    
    with open(f"email_data/{mailinglist}/all.json") as handle:
        mail_dicts = json.load(handle)
    
    convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                    for subj_str, mail_ls in subj_d.items()]    
    convos = convos[:i]    
    conversations = [Conversation.from_email_dicts(subj_str, mail_ls)
                        for subj_str, mail_ls in tqdm(convos, desc="Loading Conversations")]
    
    corpus = EmailCorpus.from_conversations(conversations, vectorise_default=False)


    current_KG = TextGraphBuilder  # EmailGraphBuilder
    
    
    kg = current_KG(corpus)
    