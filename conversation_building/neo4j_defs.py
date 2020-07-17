# -*- coding: utf-8 -*-

def add_conversation(tx, conversation):
    subject_escaped = conversation.subject.replace('"', '\\"')
    subject_escaped = conversation.subject.replace("'", "\\")
#    subject_escaped = conversation.subject.replace('\\', '\\')
    
    tx.run("""
           MERGE (c:Conversation {id:$h}) 
           ON CREATE SET c.subject = $subj
           ON CREATE SET c.length = $n_emails
           ON CREATE SET c.start = $start
           ON CREATE SET c.end = $end
           """,
           subj=subject_escaped, n_emails=len(conversation), h=hash(conversation),
           start=conversation.start_time, end=conversation.end_time)
    
    
def add_person(tx, person):
    if person.org == "" or person.org == None:
        print("org is blank")
        tx.run("MERGE (p:Person {name: $name}) ON CREATE SET p.address = $address",
           name=person.name, address=person.address)
    else:
        tx.run("""MERGE (p:Person {name: $name}) ON CREATE SET p.address = $address
           MERGE (o:Organization {name: $org})
           MERGE (p)-[rel:belongs_to]->(o)""",
           name=person.name, address=person.address, org=person.org)


def add_named_entities(tx, email):
    for entity_dict in email.body.entities:
        tx.run("""
               MERGE (e:NamedEntity {name:$name})  
               ON CREATE SET e.type = $etype
               """, name=entity_dict["text"], etype=entity_dict["type"])

def add_documents(tx, conversation):
    for doc in conversation.mentioned_links:
        tx.run("MERGE (d:Document {docid: $docid})", docid=doc.url)


def add_talked_to(tx, sender, receiver):
    tx.run("""MATCH (s:Person {name: $sname}) 
              MATCH (r:Person {name: $rname})
             MERGE (s)-[rel:talked_to]->(r)""", sname=sender.name, rname=receiver.name)
    
    
def connect_conversation(tx, person, conversation):
    tx.run("""MATCH (p:Person {name: $name}) 
              MATCH (c:Conversation {id: $h})
              MERGE (p)-[rel:involved_in]->(c)""", name=person, h=hash(conversation))

def add_mentions(tx, conversation):
    for doc in conversation.mentioned_links:
        tx.run("""MATCH (d:Document {docid: $docid}) 
              MATCH (c:Conversation {id: $h})
              MERGE (c)-[rel:mentions]->(d)""", docid=doc.url, h=hash(conversation))
    
    

def add_earlier_than(tx, c1, c2):
    tx.run("""
        MATCH (c1:Conversation {id:$h1})       
        MATCH (c2:Conversation {id:$h2})
        MERGE (c1)-[rel:earlier_than]->(c2)""", h1=hash(c1), h2=hash(c2))