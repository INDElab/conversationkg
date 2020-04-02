#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thur Apr 02 17:58:57 2020

@author: valentin
"""

import argparse

def parse_args():
    p = argparse.ArgumentParser()
    
    p.add_argument("--k", type=int)
    p.add_argument("--i", type=int)
    
    args = p.parse_args()
    return args.k, args.i

num_parts, part_i = parse_args() 
    
print("\t\t--- BERT_on_emails2.py ---")
print(f"\t\tcalled with k={num_parts}, i={part_i}")





from transformers import DistilBertTokenizer, DistilBertModel#, DistilBertConfig

import torch

import glob
import pickle
from tqdm.auto import tqdm

import logging
logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)


with torch.no_grad():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # LOAD TOKENIZER AND MODEL
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased')
    bert = DistilBertModel.from_pretrained('distilbert-base-cased')
    bert.eval()
    bert.to(device)
    
    
    def cut_up(mail_tensor, n=512):
        split_tens = mail_tensor.split(n)
    
        if split_tens[-1].nelement() == split_tens[0].nelement():
            return torch.stack(split_tens), None
        else:
            return torch.stack(split_tens[:-1]), split_tens[-1].unsqueeze(0)


    with open("emails_token_ids.pkl", "rb") as handle:
        mails_tokenised = pickle.load(handle)
        start = (len(mails_tokenised)//num_parts)*part_i
        end = (len(mails_tokenised)//num_parts)*(part_i+1)
        if part_i == (num_parts - 1): end = None
        print(f"\t\tstart={start}, end={end}")
        mails_tokenised = mails_tokenised[start:end]
        
    chunk_size = 512
        
    ls = []
    
    for mail in tqdm(mails_tokenised):
        chunks, end_chunk = cut_up(mail, chunk_size) 
        chunks = chunks[:50]
    
        chunks_cuda = chunks.to(device)
        outputs, *_ = bert(chunks_cuda)
  
        outputs_flattened = outputs.view(-1, outputs.shape[-1])
    
        if end_chunk is not None:
            end_cuda = end_chunk.to(device)
            end_output, *_ = bert(end_cuda)
            outputs_flattened = torch.cat((outputs_flattened, end_output.squeeze(0)), 0)

        ls.append(outputs_flattened.cpu())
    
    
    with open(f"emails_vectors_{part_i}.pkl", "wb") as handle:
        pickle.dump(ls, handle)