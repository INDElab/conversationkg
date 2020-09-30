# -*- coding: utf-8 -*-

from KGs import KG, EmailKG, TextKG  # , intersect_persons

import json
from tqdm import tqdm

from declarations.corpus import EmailCorpus, Conversation
from declarations.entities import Person
from declarations.topics import TopicModel
import numpy.random as rand

#lowercased_name = lambda p: p.instance_label.lower()
#
#lowercased_name = lambda p: p


#%% 1. load data and construct corpus, apply topic modeling


mailing_list = "public-credentials"  # "ietf-http-wg"

with open(f"email_data/{mailing_list}/all.json") as handle:
    mail_dicts = json.load(handle)


convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]
convos_short = rand.permutation(convos)[:-1]

conversations = [Conversation.from_email_dicts(*tup) for tup in tqdm(convos_short)]
corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)

lda = TopicModel(corpus, 7, max_iter=5)
lda.assign_topics_to_conversations()
lda.assign_topics_to_emails()



#%% 2. extract EmailKG and TextKG

emailkg = EmailKG(corpus)
#emailkg.translate()

textkg = TextKG(corpus)
#textkg.translate()



#%%

from KGs import OnlyNamePerson

len({p.instance_label.lower() for p in textkg.entities(lambda x: type(x) is OnlyNamePerson)} &\
 {p.instance_label.lower() for p in emailkg.entities(lambda x: type(x) is OnlyNamePerson)})




#%% 2.1 create IntersectKG by intersecting the Persons in EmailKG and TextKG


#intersectkg = KG.intersect_persons(emailkg, textkg, getter_func=lowercased_name)


#%% 2.2 translate KGs in a unified manner

KG.unified_translation(textkg, emailkg, attach=True)


#%% 2.3 store and restore KGs

folder_name = f"KGs/{mailing_list}"

emailkg.store(folder_name + "/emailkg")
emailkg2 = EmailKG.restore(folder_name + "/emailkg")


textkg.store(folder_name + "/textkg")
textkg2 = TextKG.restore(folder_name + "/textkg")


#intersect_name = folder_name + "/intersectkg"
#intersectkg.store(intersect_name)
#intersectkg2 = KG.restore(intersect_name)



#%% 3. instantiate RoleHeuristic 


#%% 3.1 load already saved KG

mailing_list = "public-credentials"
kg_path = f"KGs/{mailing_list}"
emailkg = KG.restore(f"{kg_path}/emailkg")
textkg = TextKG.restore(f"{kg_path}/textkg")
#intersect_name = f"KGs/{mailing_list}/intersectkg"
#intersectkg = KG.restore(intersect_name)

#%%


from roles import MajorOrganisations, RolesfromGraphMeasure,\
                SendersorReceivers, Senders, ConfirmedPerson

#roles = MajorOrganisations(emailkg, getter_func=lowercased_name)

#roles = SendersorReceivers(emailkg, sender=False, receiver=True, getter_func=lowercased_name)

#roles = RolesfromGraphMeasure(emailkg, 3, RolesfromGraphMeasure.clustering_coeff)  # , getter_func=lowercased_name)


roles = ConfirmedPerson(emailkg)  # , getter_func=lowercased_name)

#roles = Senders(emailkg, getter_func=lowercased_name)


role_labels = roles.label(textkg, to_dict=True)


ind2label = {textkg.entity2ind[e]: int(i) for e, i in role_labels.items()}


with open(f"KGs/{mailing_list}/textkg.{roles}.ind2label.json", "w") as handle:
    json.dump(ind2label, handle)




