# -*- coding: utf-8 -*-

import json
from tqdm import tqdm
from declarations.corpus import EmailCorpus, Conversation
from declarations.entities import EntityUniverse
from declarations.entity_linking import EntityLinker
from declarations.topics import TopicModel

from graph_builders import TextGraphBuilder


if __name__ == "__main__":
    
    i = 500
    mailinglist = "public-credentials" # "ietf-http-wg"

    
    with open(f"../conversation_building/email_data/{mailinglist}/all.json") as handle:
        mail_dicts = json.load(handle)
    
    convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                    for subj_str, mail_ls in subj_d.items()]    
    convos = convos[:i]    
    conversations = [Conversation.from_email_dicts(subj_str, mail_ls)
                        for subj_str, mail_ls in tqdm(convos, desc="Loading Conversations")]
    
    corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)

    
    linker = EntityLinker()
    linker.to_WikiData_entities(list(EntityUniverse.entities.values()))
    linker.enrich_email_bodies(corpus)

    lda = TopicModel(corpus, 20, max_iter=10)
    lda.assign_topics_to_emails()
    lda.assign_topics_to_conversations()

    with open("corpus.json", "w") as handle:
        handle.write(corpus.to_json(dumps=True))
    
    current_KG = TextGraphBuilder  # EmailGraphBuilder
    
    kg = current_KG(corpus)
    