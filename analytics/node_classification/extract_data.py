# -*- coding: utf-8 -*-

import json
from tqdm import tqdm

import numpy.random as rand

from sklearn.feature_extraction.text import TfidfVectorizer

from conversationkg.conversations import EmailCorpus, Conversation, TopicModel
from conversationkg.kgs import KG, EmailKG, TextKG # , Person

from conversationkg import sample_data_raw

#%% 1. load data and construct corpus, apply topic modeling

mailing_list = "ietf-http-wg"

#with open(f"email_data/{mailing_list}/all.json") as handle:
#    mail_dicts = json.load(handle)


mail_dicts = sample_data_raw(mailing_list)


convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]
convos_short = rand.permutation(convos)[:100]


corpus = EmailCorpus.from_email_dicts(convos_short)
corpus.vectorise(vectoriser_algorithm=TfidfVectorizer, max_df=0.7, min_df=5)

print(len(corpus.vectoriser.get_feature_names()))

lda = TopicModel(corpus, 7, max_iter=200)
lda.assign_topics_to_conversations()
lda.assign_topics_to_emails()




#%%

mailing_list = "ietf-http-wg"

with open(f"email_data/{mailing_list}/all.json") as handle:
    mail_dicts = json.load(handle)


convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]
convos_short = rand.permutation(convos)[:100]

conversations = [Conversation.from_email_dicts(*tup) for tup in tqdm(convos_short)]
corpus = EmailCorpus.from_conversations(conversations, vectorise_default=False)
corpus.vectorise(vectoriser_algorithm=TfidfVectorizer, max_df=0.7, min_df=5)

print(len(corpus.vectoriser.get_feature_names()))

lda = TopicModel(corpus, 7, max_iter=200)
lda.assign_topics_to_conversations()
lda.assign_topics_to_emails()



#%% 2. extract EmailKG and TextKG

emailkg = EmailKG(corpus)

textkg = TextKG(corpus)


#%% 2.1 merge node in TextKG based on string distance

mergedkg = KG.merge_persons_of(textkg, distance_threshold=0.5)


#%% 2.2 compute unified translation for both KGs

KG.unified_translation(textkg, emailkg, attach=True)
mergedkg.translate(textkg.entity2ind, textkg.pred2ind, attach=True)


#%% 2.3 store and restore KGs

folder_name = f"KGs_dev/{mailing_list}"

emailkg.store(folder_name + "/emailkg")
emailkg2 = EmailKG.restore(folder_name + "/emailkg")


textkg.store(folder_name + "/textkg", save_mapping=False)
textkg2 = TextKG.restore(folder_name + "/textkg",
                         load_mapping_of=folder_name + "/emailkg")

mergedkg.store(folder_name + "/mergedkg", save_mapping=False)
mergedkg2 = TextKG.restore(folder_name + "/mergedkg",
                           load_mapping_of=folder_name + "/emailkg")


#%% 2.4 write out graphs to USAF CSV

emailkg.to_csv(folder_name + "/emailkg")
textkg.to_csv(folder_name + "/textkg")


#%% 3.0 load already saved KG

mailing_list = "ietf-http-wg"
kg_path = f"KGs/{mailing_list}"
emailkg = KG.restore(f"{kg_path}/emailkg")
textkg = TextKG.restore(f"{kg_path}/textkg")

#%% 3. instantiate RoleHeuristic 
    

from roles import MajorOrganisations, RolesfromGraphMeasure,\
                SendersOrReceivers, Senders, ConfirmedPerson

#roles = MajorOrganisations(emailkg)

#roles = SendersorReceivers(emailkg, sender=False, receiver=True)

roles = RolesfromGraphMeasure(emailkg, 3, RolesfromGraphMeasure.clustering_coeff)

#roles = ConfirmedPerson(emailkg)

#roles = Senders(emailkg, getter_func=lowercased_name)


role_labels = roles.label(mergedkg, to_dict=True)


ind2label = {textkg.entity2ind[e]: int(i) for e, i in role_labels.items()}


with open(f"KGs/{mailing_list}/mergedkg.{roles}.ind2label.json", "w") as handle:
    json.dump(ind2label, handle)

        
    
    
    
