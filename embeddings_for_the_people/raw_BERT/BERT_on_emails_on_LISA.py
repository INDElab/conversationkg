#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:58:57 2020

@author: valentin
"""

from transformers import DistilBertTokenizer, DistilBertModel#, DistilBertConfig

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
def email_to_vec(email_body_ids, to_id_first=False):
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
    


import argparse

def parse_args():
    p = argparse.ArgumentParser()
    
    p.add_argument("--k", type=int)
    p.add_argument("--i", type=int)
    
    args = p.parse_args()
    return args.k, args.i



if __name__ == "__main__":   
    num_parts, part_i = parse_args() 
    
    
    
    print("\t\t--- BERT_on_emails_on_LISA.py ---")
    print(f"\t\tcalled with k={num_parts}, i={part_i}")
    
            
    with open("emails_token_ids.pkl", "rb") as handle:
        ids = pickle.load(handle)
        
    start = (len(ids)//num_parts)*part_i
    end = (len(ids)//num_parts)*(part_i+1)
    if part_i == (num_parts -1): end = None
    small = ids[start:end]
    
    print(f"\t\tstart={start}, end={end}")
    
    
    length_adjusted = [cut_up(id_tens) for id_tens in small]
            
    with torch.no_grad():
        vecs = [[email_to_vec(v, to_id_first=False) for v in tt]
                    for tt in tqdm(length_adjusted)]
    
    with open(f"vectors_{part_i}.pkl", "wb") as handle:
        pickle.dump(vecs, handle)
        
        
        
        
#    import multiprocessing as mp
#    with mp.Pool() as p:
#        with torch.no_grad():    
#            vecs = []
#            for tt in tqdm(length_adjusted):
#                print(tt)
#                map_result = p.map_async(email_to_vec, tt)
#                
#                map_result.wait()
#                
#                
#                cur_mail_vecs = [p.get() for p in map_result]
#                
#                vecs.append(cur_mail_vecs)
#                
#                print(type(map_result))
#                print(map_result[0])
#                print(map_result.shape)
#                
#    
#    
#    
#    exit(13)