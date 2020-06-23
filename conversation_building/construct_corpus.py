# -*- coding: utf-8 -*-

import json

from tqdm import tqdm

from corpus_declarations.corpus import EmailCorpus, Conversation

import multiprocessing as mp

mailinglist = "ietf-http-wg"

with open(f"email_data/{mailinglist}/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]


#conversations = [Conversation(subj, mail_ds) for subj, mail_ds in tqdm(convos)]


def to_conv(tup):
    return Conversation(*tup)

with mp.Pool(4) as pool:
    conversations = list(tqdm(pool.imap_unordered(to_conv, convos),
                             total=len(convos)))

corpus = EmailCorpus.from_conversations(conversations)

print(len(corpus))
print(corpus.start_time)
print(corpus.end_time)



