#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:58:57 2020

@author: valentin
"""

from transformers import DistilBertTokenizer, DistilBertModel, DistilBertConfig

import torch

import pickle
from tqdm import tqdm

import logging
logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)



# LOAD TOKENIZER AND MODEL
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')
model.eval()


# WRAPPER FOR TOKENIZER CALL
def email_to_ids(email_body):
    return torch.tensor(tokenizer.encode(email_body, add_special_tokens=True))


# WRAPPER FOR MODEL CALL
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


# CUTS A LIST OF TOKENS IDs INTO CHUNKS OF 512 IF LONGER
# ENSURES OVERLAP BETWEEN THE CHUNKS
def cut_up(mail_tensor, n=511, k=20):
    if mail_tensor.shape[0] <= n:
        return (mail_tensor, )
    
    unfolded = mail_tensor.unfold(0, n, n-k)
    covered = unfolded.shape[0]-unfolded.shape[1]
   
    return tuple(v for v in unfolded) + (mail_tensor[covered:],)
    




if __name__ == "__main__":               
    with open("emails_token_ids.pkl", "rb") as handle:
        ids = pickle.load(handle)
    
    
    length_adjusted = [cut_up(id_tens) for id_tens in ids]
    
    with torch.no_grad():    
        vecs = [[email_to_vec(v, to_id_first=False) for v in tt] for tt in tqdm(length_adjusted)]
    
    with open("LISA/vectors.pkl", "wb") as handle:
        pickle.dump(vecs, handle)