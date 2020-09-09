# -*- coding: utf-8 -*-

from KGs import KG, EmailKG, TextKG  # , intersect_persons

import json
from tqdm import tqdm

from declarations.corpus import EmailCorpus, Conversation
from declarations.entities import Person
from declarations.topics import TopicModel
import numpy.random as rand


#%% 1. load data and construct corpus, apply topic modeling

mailing_list = "public-credentials"

with open(f"email_data/{mailing_list}/all.json") as handle:
    mail_dicts = json.load(handle)


convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

convos_short = rand.permutation(convos)[:-1]

conversations = [Conversation.from_email_dicts(*tup) for tup in tqdm(convos_short)]

corpus = EmailCorpus.from_conversations(conversations, vectorise_default=True)


lda = TopicModel(corpus, 7, max_iter=500)

lda.assign_topics_to_conversations()
lda.assign_topics_to_emails()



#%% 2. extract EmailKG and TextKG

emailkg = EmailKG(corpus)
#emailkg.translate()

textkg = TextKG(corpus)
#textkg.translate()


lowercased_name = lambda p: p.instance_label.lower()


#%% 2.1 create IntersectKG by intersecting the Persons in EmailKG and TextKG

def intersect_persons(emailkg, textkg, getter_func=lambda x: x):
    is_person = lambda x: type(x) is Person
    emailkg_names = {getter_func(x) for x in emailkg.entities(is_person)}
    
    def keep(s, o, name_set):
        if not (is_person(s) or is_person(o)):
            return True
        
        if is_person(s) and is_person(o):
            if getter_func(s) in name_set or getter_func(o) in name_set:
                return True
        
        if is_person(s):
            if getter_func(s) in name_set:
                return True
        
        if is_person(o):
            if getter_func(o) in name_set:
                return True
        return False
    
    new_triples = []
    for s, p, o in textkg.triples:
        
        if keep(s, o, emailkg_names):
            new_triples.append((s, p, o))
    
    return KG(new_triples)




#intersectkg = KG.intersect_persons(emailkg, textkg, 
#                                   getter_func=lambda p: p.instance_label.lower())


intersectkg = intersect_persons(emailkg, textkg, getter_func=lowercased_name)


#%% 2.2 translate KGs in a unified manner

class Translator:
    @staticmethod
    def unified_translation(*kgs, attach=False):

        uni_e2i, uni_p2i = {}, {}

        for kg in kgs:
#            print(bool(uni_e2i), bool(uni_p2i))
            translated, uni_e2i, uni_p2i = kg.translate(uni_e2i, uni_p2i, attach=False)
#            print("from loop", uni_p2i)
            if attach:
                kg.translated = translated

        if attach:
            for kg in kgs:
                kg.entity2ind = uni_e2i
                kg.pred2ind = uni_p2i
        else:
            return uni_e2i, uni_p2i



Translator.unified_translation(intersectkg, textkg, emailkg, attach=True)


#%% 2.3 store and restore KGs

folder_name = f"KGs/{mailing_list}"

emailkg.store(folder_name + "/emailkg")
emailkg2 = EmailKG.restore(folder_name + "/emailkg")


textkg.store(folder_name + "/textkg")
textkg2 = TextKG.restore(folder_name + "/textkg")


intersect_name = folder_name + "/intersectkg"
intersectkg.store(intersect_name)
intersectkg2 = KG.restore(intersect_name)



#%% 3. instantiate RoleHeuristic 

from roles_new import MajorOrganisations, RolesfromGraphMeasure

mo = MajorOrganisations(emailkg, getter_func=lowercased_name)

mo_labels = mo.label(intersectkg, getter_func=lowercased_name, to_dict=True)


#roles = RolesfromGraphMeasure(emailkg, 4, RolesfromGraphMeasure.clustering_coeff,
#                              getter_func=lowercased_name)
#
#role_labels = roles.label(intersectkg, getter_func=lowercased_name)


entity2label = {intersectkg.entity2ind[e]: i for e, i in mo_labels.items()}


with open(intersect_name + ".ind2label.json", "w") as handle:
    json.dump(entity2label, handle)






