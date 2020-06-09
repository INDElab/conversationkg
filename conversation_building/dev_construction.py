# -*- coding: utf-8 -*-


import os
import json

import re

from email.utils import parseaddr


sender_re = re.compile(r"[^@]+@[^@]+\.[^@]+")

#%%


with open("email_data/ietf-http-wg/all.json") as handle:
    mail_dicts = json.load(handle)
    
#%%
    
    
for period, subject_d in mail_dicts.items():
    print(period)
    for subject, mail_ls in subject_d.items():
        print("\t", subject, len(mail_ls))
        
        
#%%
        
keys = set(k for period, subj_d in mail_dicts.items() 
            for subj, ls in subj_d.items() for m_d in ls for k in m_d)


convos = [(subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                for subj_str, mail_ls in subj_d.items()]

mails = [m for subj_d in mail_dicts.values() for ls in subj_d.values() 
            for m in ls]
#%%


def merge_reported_subjects(subject, subject_from_meta):
    same = subject == subject_from_meta
    
    if same:
        return subject
    
    return subject

    
def merge_reported_authors(author, from_, name, email):
    if sender_re.match(from_):
        from_name, from_email = parseaddr(from_)
        if not from_name:
            pass
        else:
            pass
    else:
        pass
    
    
def merge_reported_ids(id_, id_from_body):
    if not id_from_body:
        pass
