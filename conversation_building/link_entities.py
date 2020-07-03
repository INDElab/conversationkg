# -*- coding: utf-8 -*-

import json
from tqdm import tqdm

from corpus_declarations.corpus import Conversation, EmailCorpus
from corpus_declarations.entities2 import EntityUniverse
from corpus_declarations.entity_linking2 import EntityLinker


mailinglist = "ietf-http-wg"

with open(f"email_data/{mailinglist}/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()][:100]
convos = [Conversation(*tup) for tup in tqdm(convos)]

corpus = EmailCorpus.from_conversations(convos, vectorise_default=True)
print(len(corpus))
print(corpus.start_time)
print(corpus.end_time)

#%%




el = EntityLinker()

el.to_WikiData_entities(list(EntityUniverse.entities.values()))