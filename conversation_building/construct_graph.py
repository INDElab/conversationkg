# -*- coding: utf-8 -*-

import json
from tqdm import tqdm
import multiprocessing as mp

from collections import Counter

from declarations.ledger import Universe
from declarations.entities import EntityUniverse, EntityInstance, Person
from declarations.corpus import EmailCorpus, Conversation
from declarations.emails import Email
from declarations.topics import TopicModel, TopicInstance
from declarations.entity_linking import EntityLinker


#%%

i = 10

mailinglist = "public-credentials" # "ietf-http-wg"

with open(f"email_data/{mailinglist}/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

convos = convos[:1000]

def to_conv(tup):
    return Conversation.from_email_dicts(*tup)

conversations = list(tqdm(map(to_conv, convos), total=len(convos)))

corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)
print(len(corpus), ", ", corpus.n_emails)
print(corpus.start_time, ", ", corpus.end_time)


#%%

lda = TopicModel(corpus, 20, max_iter=10)


#
#Universe.reset()
#EntityUniverse.reset()
#j = 50
#conversations = list(tqdm(map(to_conv, convos[:j]), total=j))
#corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)
lda.assign_topics_to_conversations(email_corpus=corpus)
lda.assign_topics_to_emails(email_corpus=corpus)


#%%

#Universe.reset()
#EntityUniverse.reset()
#
#conversations = list(tqdm(map(to_conv, convos[:50]), total=len(convos)))
#corpus = EmailCorpus.from_conversations(conversations,      
#                                        vectorise_default=True)


#%%

from neo4j import GraphDatabase
from neo4j_defs2 import put_conversation, put_email, put_entity, put_topic
from neo4j_defs2 import connect_conversation, connect_email, connect_person
from neo4j_defs2 import before

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "pwd"), encrypted=False)


#%% 


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

    
with driver.session() as session:
    session.write_transaction(clear)
    
    
    put_iter(put_conversation, corpus)
    
    put_iter(put_email, list(corpus.iter_emails()))
    
    put_iter(put_entity, EntityUniverse.entities.values())
    
    put_iter(put_topic, lda.topics)

    
    connect_iter(connect_conversation, corpus)
    
    connect_iter(connect_email, list(corpus.iter_emails()))
    
    connect_iter(connect_person, 
                 filter(lambda x: isinstance(x, Person), EntityUniverse.entities.values()))


    for conv1, conv2 in zip(corpus, corpus[1:]):
        session.write_transaction(before, conv1, conv2)
        
        
    for conv in tqdm(corpus, desc="before emails"):
        session.write_transaction(consists_of, conv)
        for e1, e2 in zip(conv, conv[1:]):
            session.write_transaction(before, e1, e2)    

