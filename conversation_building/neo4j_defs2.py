# -*- coding: utf-8 -*-

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


#def put_person(tx, person):
#    tx.run("""
#            MERGE (p:Person {id:$h})
#            ON CREATE SET p.name = $name
#    """, 
#    h=hash(person), name=person.name)
#    
#def put_address(tx, address):
#    tx.run("""
#        MERGE (a:Address {id:$h})
#        ON CREATE SET a.name = $addr
#    """,
#    h=hash(address), addr=address.instance_label)
#
#def put_link(tx, link):
#    tx.run("""
#        MERGE (l:Link {id:$h})
#        ON CREATE SET l.name = $lnk
#    """,
#    h=hash(link), lnk=link.instance_label)
#    
#def put_organisation(tx, organisation):
#    tx.run("""
#        MERGE (o:Organisation {id:$h})
#        ON CREATE SET o.name = $name
#    """,
#    h=hash(organisation), name=organisation.name)















#def add_conversation(tx, conversation):
#    subject_escaped = conversation.subject.replace('"', '\\"')
#    subject_escaped = conversation.subject.replace("'", "\\")
##    subject_escaped = conversation.subject.replace('\\', '\\')
#    
#    tx.run("""
#           MERGE (c:Conversation {id:$h}) 
#           ON CREATE SET c.subject = $subj
#           ON CREATE SET c.length = $n_emails
#           """,
#           subj=subject_escaped, n_emails=len(conversation), h=hash(conversation))
#    
#    
#def add_person(tx, person):
#    if person.org == "" or person.org == None:
#        print("org is blank")
#        tx.run("MERGE (p:Person {name: $name}) ON CREATE SET p.address = $address",
#           name=person.name, address=person.address)
#    else:
#        tx.run("""MERGE (p:Person {name: $name}) ON CREATE SET p.address = $address
#           MERGE (o:Organization {name: $org})
#           MERGE (p)-[rel:belongs_to]->(o)""",
#           name=person.name, address=person.address, org=person.org)
#
#
#def add_named_entities(tx, email):
#    for entity_dict in email.body.entities:
#        tx.run("""
#               MERGE (e:NamedEntity {name:$name})  
#               ON CREATE SET e.type = $etype
#               """, name=entity_dict["text"], etype=entity_dict["type"])
#
#def add_documents(tx, conversation):
#    for doc in conversation.mentioned_links:
#        tx.run("MERGE (d:Document {docid: $docid})", docid=doc.url)
#
#
#def add_talked_to(tx, sender, receiver):
#    tx.run("""MATCH (s:Person {name: $sname}) 
#              MATCH (r:Person {name: $rname})
#             MERGE (s)-[rel:talked_to]->(r)""", sname=sender.name, rname=receiver.name)
#    
#    
#def connect_conversation(tx, person, conversation):
#    tx.run("""MATCH (p:Person {name: $name}) 
#              MATCH (c:Conversation {id: $h})
#              MERGE (p)-[rel:involved_in]->(c)""", name=person, h=hash(conversation))
#
#def add_mentions(tx, conversation):
#    for doc in conversation.mentioned_links:
#        tx.run("""MATCH (d:Document {docid: $docid}) 
#              MATCH (c:Conversation {id: $h})
#              MERGE (c)-[rel:mentions]->(d)""", docid=doc.url, h=hash(conversation))
#    
#    
#
#def add_earlier_than(tx, c1, c2):
#    tx.run("""
#        MATCH (c1:Conversation {id:$h1})       
#        MATCH (c2:Conversation {id:$h2})
#        MERGE (c1)-[rel:earlier_than]->(c2)""", h1=hash(c1), h2=hash(c2))