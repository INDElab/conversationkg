#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:58:57 2020

@author: valentin
"""

from transformers import DistilBertTokenizer, DistilBertModel, DistilBertConfig
from transformers import BertTokenizer, BertModel, BertConfig

import torch
import numpy as np

import pickle
from tqdm import tqdm

from collections import Counter
import matplotlib.pyplot as plt

import logging
logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)




tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

model.eval()


def email_to_ids(email_body):
    return torch.tensor(tokenizer.encode(email_body, add_special_tokens=True))

def email_to_vec(email_body_ids, to_id_first=True):
    if to_id_first:
        input_ids = email_to_ids(email_body_ids)
    else:
        input_ids = email_body_ids
        
    input_ids = input_ids.unsqueeze(0)
    outputs = model(input_ids)
    return outputs
    
#     last_hidden_states = outputs[0][0]
#     return last_hidden_states.mean(0)  # mean vs sum


def cut_up(mail_tensor, n=511, k=20):
   unfolded = mail_tensor.unfold(0, n, n-k)
   covered = unfolded.shape[0]-unfolded.shape[1]
   
   return tuple(v for v in unfolded) + (mail_tensor[covered:],)
    


import os


if __name__ == "__main__":               
    with open("emails_token_ids.pkl", "rb") as handle:
        ids = pickle.load(handle)
    
    
    length_adjusted = [cut_up(id_tens) for id_tens in ids]
    
    with torch.no_grad():    
        vecs = [[email_to_vec(v, to_id_first=False) for v in tt] for tt in tqdm(cut_up)]
    
    with open("LISA/vectors.pkl", "wb") as handle:
        pickle.dump(vecs, handle)