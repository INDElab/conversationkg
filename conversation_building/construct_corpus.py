H# -*- coding: utf-8 -*-
import json

from tqdm import tqdm

import multiprocessing as mp

from declarations.corpus import EmailCorpus, Conversation
from declarations.emails import Email
from declarations.entities import EntityUniverse
from declarations.ledger import Universe

from declarations.entity_linking import EntityLinker

from declarations.topics import TopicModel, TopicInstance



mailinglist = "public-credentials" # "ietf-http-wg"

with open(f"email_data/{mailinglist}/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

convos = convos[:50]

#%%

#conversations = [Conversation(subj, mail_ds) for subj, mail_ds in tqdm(convos)]


def to_conv(tup):
    return Conversation.from_email_dicts(*tup)

#with mp.Pool(4) as pool:
#    conversations = tuple(tqdm(pool.map(to_conv, convos),
#                             total=len(convos)))
    
conversations = list(tqdm(map(to_conv, convos), total=len(convos)))

corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)

print(len(corpus))
print(corpus.start_time)
print(corpus.end_time)
print(len(Universe.evidenced_by), len(Universe.mentioned_in), len(EntityUniverse.entities))



#%%

from joblib import Parallel, delayed

conversations = []

with Parallel(n_jobs=4) as parallel:
    for i in range(0, len(convos), 4):
        cur_conversations = parallel(delayed(to_conv)(tup) for tup in convos[i:i+4])
        conversations.extend(cur_conversations)
        print(len(Universe.evidenced_by), len(Universe.mentioned_in), len(EntityUniverse.entities))


        
#%%

linker = EntityLinker()

linker.to_WikiData_entities(list(EntityUniverse.entities.values()))
linker.enrich_email_bodies(corpus)


#%%


lda = TopicModel(corpus, 20, max_iter=10)

lda.assign_topics_to_emails()
lda.assign_topics_to_conversations()



#%%

emails_per_topic = {t: [] for t in lda.topics}
convos_per_topic = {t: [] for t in lda.topics}

for k, v_ls in Universe.evidenced_by.items():
    if isinstance(k, TopicInstance):
        for v in v_ls:
            if isinstance(v, Conversation):
                convos_per_topic[k.topic].append(v)
            elif isinstance(v, Email):
                emails_per_topic[k.topic].append(v)
            else:
                raise ValueError("Neither Conversation or Email!")
    
#%%

with open("corpus.json", "w", encoding="utf-8") as handle:
    json.dump(corpus.to_json(dumps=False), handle)


#%%
    
with open("corpus.json", "r", encoding="utf-8") as handle:
    json_dict = json.load(handle)    
    
    corpus2 = EmailCorpus.from_json(json_dict)
