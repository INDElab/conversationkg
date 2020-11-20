# -*- coding: utf-8 -*-

from tqdm import tqdm

def put_conversation(tx, conversation):
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


def put_email(tx, email):
    tx.run("""
            MERGE (e:Email {id:$h})            
            ON CREATE SET e.time = $time
            ON CREATE SET e.subject = $subject            
           """, 
           h = hash(email), time=email.time.strftime("%d.%m.%Y, %H:%M"),
           subject=email.subject)    
    
    
def put_entity(tx, entity):
    class_name = entity.__class__.__name__
    ent_dict = entity.to_json()
#    print(ent_dict)
    
    tx.run(f"""
            MERGE (x:{class_name} {{id:$h}})
            ON CREATE SET x.label = $name
    """, h=hash(entity), name=entity.instance_label)
    
    
def put_topic(tx, topic):
    tx.run("""
        MERGE (t:Topic {id:$topic_id})
        ON CREATE SET t.words = $words
    """,
    topic_id=topic.index, words=", ".join(topic.top_words(5)))
    
    
    
    
def connect_conversation(tx, conversation):
    cmd =  "MATCH (c:Conversation {id:$h})"
    
    param_d = dict(h=hash(conversation))
    

    for i, email in enumerate(conversation):
        cmd += "\n" + f"MATCH (e{i}:Email {{id:$mail_h{i}}})"
        param_d[f"mail_h{i}"] = hash(email)

    for i, p in enumerate(conversation.interlocutors):
        cmd += "\n" + f"MATCH (p{i}:Person {{id:$person_h{i}}})"
        param_d[f"person_h{i}"] = hash(p)
    
    for i, d in enumerate(conversation.documents):
        cls = d.__class__.__name__
        cmd += "\n" + f"MATCH (d{i}:{cls} {{id:$doc_h{i}}})"
        param_d[f"doc_h{i}"] = hash(d)
    
    if conversation.topic:
        cmd += "\n" + f"MATCH (t:Topic {{id:$topic_id}})"
        param_d["topic_id"] = conversation.topic.index
        
        cmd += "\n" + "MERGE (c)-[rel_topic:is_about]->(t)"
    
    
    for i, e in enumerate(conversation):
        cmd += "\n" + f"MERGE (c)-[rel_email{i}:consists_of]->(e{i})"
    
    for i, p in enumerate(conversation.interlocutors):
        cmd += "\n" + f"MERGE (p{i})-[rel_person{i}:interlocutor_in]->(c)"
            
    for i, d in enumerate(conversation.documents):
        cmd += "\n" + f"MERGE (d{i})-[rel_doc{i}:mentioned_in]->(c)"

    tx.run(cmd, **param_d)
    
    return cmd, param_d

    
def connect_email(tx, email):
    cmd = """
        MATCH (e:Email {id: $h}) 
          
        MATCH (p:Person {id: $sender_h})
        MATCH (p2:Person {id: $receiver_h})
    """
    
    param_d = dict(h=hash(email),
                   sender_h=hash(email.sender),
                   receiver_h=hash(email.receiver))
    
    
    if email.topic:
        cmd += "\n" + f"MATCH (t:Topic {{id:$topic_id}})"
        param_d["topic_id"] = email.topic.index
        
        cmd += "\n" + "MERGE (e)-[rel_topic:is_about]->(t)"
    
    
    cmd += """
        MERGE (p)-[rel_person:talked_to]->(p2)
    """
    
    
    tx.run(cmd, **param_d)
    
    return cmd, param_d

        
def connect_person(tx, person):
    tx.run("""
          MATCH (p:Person {id:$p_h})
          MATCH (a:Address {id:$a_h})
          MATCH (o:Organisation {id:$o_h})
          MERGE (a)-[rel_addr:of]->(p)
          MERGE (o)-[rel_org:of]->(p)
    """,
    p_h=hash(person), a_h=hash(person.address), o_h=hash(person.organisation))


def before(tx, event1, event2):
    cls1, cls2 = event1.__class__.__name__, event2.__class__.__name__
    
    cmd = f"""
        MATCH (e1:{cls1} {{id: $h1}})
        MATCH (e2:{cls2} {{id: $h2}})
        MERGE (e1)-[rel:before]->(e2)
    """

    param_d = dict(h1=hash(event1), h2=hash(event2))

    tx.run(cmd, **param_d)
    
#    print(cmd, param_d)
    
    return cmd, param_d


#%% FROM conversationkg_backup/conversation_building/construct_graph.py
    
#from neo4j import GraphDatabase
#from neo4j_defs2 import put_conversation, put_email, put_entity, put_topic
#from neo4j_defs2 import connect_conversation, connect_email, connect_person
#from neo4j_defs2 import before

#driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "pwd"), encrypted=False)


def clear(tx):
    tx.run("""MATCH (x)
            DETACH DELETE x""")

def put_iter(func, iterable):
    for item in tqdm(iterable, desc=func.__name__):
        session.write_transaction(func, item)
        
        
def connect_iter(func, iterable):
    for item in tqdm(iterable, desc=func.__name__):
        session.write_transaction(func, item)
        


def consists_of(tx, conversation):
    for email in conversation:
        tx.run("""
            MATCH (c:Conversation {id:$h})
            MATCH (e:Email {id:$h1})
            MERGE (c)-[rel:consists_of]->(e)
        """,
        h=hash(conversation), h1=hash(email))

    
#with driver.session() as session:
#    session.write_transaction(clear)
#    
#    
#    put_iter(put_conversation, corpus)
#    
#    put_iter(put_email, list(corpus.iter_emails()))
#    
#    put_iter(put_entity, EntityUniverse.entities.values())
#    
#    put_iter(put_topic, lda.topics)
#
#    
#    connect_iter(connect_conversation, corpus)
#    
#    connect_iter(connect_email, list(corpus.iter_emails()))
#
#    connect_iter(connect_person, 
#                 filter(lambda x: isinstance(x, Person), EntityUniverse.entities.values()))
#
#
#    for conv1, conv2 in zip(corpus, corpus[1:]):
#        session.write_transaction(before, conv1, conv2)
#        
#        
#    for conv in tqdm(corpus, desc="before emails"):
#        session.write_transaction(consists_of, conv)
#        for e1, e2 in zip(conv, conv[1:]):
#            session.write_transaction(before, e1, e2)    





#%% FROM conversationkg_backup/analytics/graph_builders.py
    


# -*- coding: utf-8 -*-


#import spacy
#nlp = spacy.load("en")
#
#from neo4j import GraphDatabase


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
            session.write_transaction(self.put_persons, persons)
            
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



