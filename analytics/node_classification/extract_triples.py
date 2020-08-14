# -*- coding: utf-8 -*-

from KGs import KG, EmailKG, TextKG, intersect_persons, unified_translation

import json
from tqdm import tqdm

from declarations.corpus import EmailCorpus, Conversation
from declarations.entities import Person
from declarations.topics import TopicModel
import numpy.random as rand


# load data and construct corpus, apply topic modeling

with open("../../analytics2/email_data/ietf-http-wg/all.json") as handle:
    mail_dicts = json.load(handle)

convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

convos_short = rand.permutation(convos)[:500]

conversations = [Conversation.from_email_dicts(*tup) for tup in tqdm(convos_short)]

corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)


lda = TopicModel(corpus, 10, max_iter=100)

lda.assign_topics_to_conversations()
lda.assign_topics_to_emails()


# construct EmailKG and TextKG from the corpus

emailkg = EmailKG(corpus)
emailkg.translate()

textkg = TextKG(corpus)
textkg.translate()


# intersect graphs and recompute indexing

intersectkg = intersect_persons(emailkg, textkg)

e2i, p2i = unified_translation(emailkg, textkg, intersectkg, do_retranslation=True)


# sotre all KGs (restore just for testing)


folder_name = "KGs"

emailkg.store(folder_name + "/emailkg")
emailkg2 = EmailKG.restore(folder_name + "/emailkg")


textkg.store(folder_name + "/textkg")
textkg2 = TextKG.restore(folder_name + "/textkg")


intersect_name = folder_name + "/intersectkg"
intersectkg.store(intersect_name)
intersectkg2 = KG.restore(intersect_name)


















