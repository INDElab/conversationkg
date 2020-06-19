# -*- coding: utf-8 -*-


import os
import json

from tqdm import tqdm


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


#%% QUOTED TEXT


from email_reply_parser import EmailReplyParser
import quotequail
import talon
from talon import quotations


for e in convos[1]:
    email = EmailReplyParser.read(e.body)
    print(email.text)
    
    print("\n###")
    print(email.reply)

    print("------------------------------------------------------------\n\n")