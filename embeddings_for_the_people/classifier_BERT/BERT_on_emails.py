#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:58:57 2020

@author: valentin
"""

from transformers import DistilBertTokenizer, DistilBertModel#, DistilBertConfig

import torch

import glob
import pickle
from tqdm.auto import tqdm

import logging
logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# LOAD TOKENIZER AND MODEL
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased')
bert = DistilBertModel.from_pretrained('distilbert-base-cased')
bert.eval()
bert.to(device)


# WRAPPER FOR TOKENIZER CALL
def email_to_ids(email_body):
    return torch.tensor(tokenizer.encode(email_body, add_special_tokens=True))

# 
def cut_up(mail_tensor, n=512):
    split_tens = mail_tensor.split(n)
    
    if split_tens[-1].nelement() == split_tens[0].nelement():
        return torch.stack(split_tens), None
    else:
        return torch.stack(split_tens[:-1]), split_tens[-1].unsqueeze(0)


# WRAPPER FOR MODEL CALL
def email_to_vec(email_body_ids, to_id_first=False, chunk_size=512):
    if to_id_first:
        input_ids = email_to_ids(email_body_ids)
    else:
        input_ids = email_body_ids
        
    chunks, end_chunk = cut_up(input_ids, chunk_size)
    
    chunks_cuda = chunks.to(device)
    outputs, *_ = bert(chunks_cuda)
    
    outputs_flattened = outputs.view(-1, outputs.shape[-1])
    
    if end_chunk is not None:
        end_cuda = end_chunk.to(device)
        end_output, *_ = bert(end_cuda)
        outputs_flattened = torch.cat((outputs_flattened, end_output.squeeze(0)), 0)
        
    return outputs_flattened.cpu()


if __name__ == "__main__":
    if not glob.glob("./emails_token_ids.pkl"):
        print("TOKENISING FIRST...")
        with open("emails.pkl", "rb") as handle:
            mails = pickle.load(handle)
        
        mails_tokenised = [email_to_ids(e.body_raw) for e in tqdm(mails)]
    
        with open("emails_token_ids.pkl", "wb") as handle:
            pickle.dump(mails_tokenised, handle)
    else:
        with open("emails_token_ids.pkl", "rb") as handle:
            mails_tokenised = pickle.load(handle)
    
    print("TOKENISATION/LOADING DONE...")
    print("="*30)
        
    with torch.no_grad():
        ls = []
        for mail_tens in tqdm(mails_tokenised):
            mail_vec = email_to_vec(mail_tens)
            ls.append(mail_vec)
            
        with open("emails_vectors.pkl", "wb") as handle:
            pickle.dump(ls, handle)