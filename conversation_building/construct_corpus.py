# -*- coding: utf-8 -*-


import json

from tqdm import tqdm

from corpus_declarations.corpus import EmailCorpus, Conversation

import multiprocessing as mp


mailinglist = "public-credentials" # "ietf-http-wg"

with open(f"email_data/{mailinglist}/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

#convos = convos[:5]


#conversations = [Conversation(subj, mail_ds) for subj, mail_ds in tqdm(convos)]


def to_conv(tup):
    return Conversation.from_email_dicts(*tup)

with mp.Pool(4) as pool:
    conversations = list(tqdm(pool.imap_unordered(to_conv, convos),
                             total=len(convos)))


corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)

print(len(corpus))
print(corpus.start_time)
print(corpus.end_time)


#%%

corpus_json = corpus.to_json(dumps=False)



#%%

from corpus_declarations.topics import TopicModel

lda = TopicModel(corpus, max_iter=1)

lda.assign_topics_to_emails()
lda.assign_topics_to_conversations()


#%%

with open("corpus.json", "w", encoding="utf-8") as handle:
    json.dump(corpus.to_json(dumps=False), handle)




#%%
    
with open("corpus.json", "r", encoding="utf-8") as handle:
    json_dict = json.load(handle)    
    
    corpus2 = EmailCorpus.from_json(json_dict)
    
    
#%%

from corpus_declarations.entities import EntityUniverse
from corpus_declarations.entity_linking import EntityLinker

linker = EntityLinker()

linker.to_WikiData_entities(list(EntityUniverse.entities.values()))
linker.enrich_email_bodies(corpus)


