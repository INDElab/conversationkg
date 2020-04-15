import torch

from transformers import DistilBertTokenizer, DistilBertModel#, DistilBertConfig
# from transformers import BertTokenizer, BertModel
# BERTTokenizer = DistilBertTokenizer
# BERT = DistilBertModel

import torch

import pickle
from tqdm import tqdm

# import logging
# logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)


from defs_classifier2 import CosineSimilarityClassifierCell, Classifier


def gen_X(train_X, tknsd_emails):
    for i1, i2 in train_X:
        yield tknsd_emails[i1], tknsd_emails[i2]
        
def gen_Y(train_Y, tknsd_emails):
    return iter(train_Y)

def generate_forever(iter_func, iter_args):
    iter_instance = iter_func(*iter_args)
    while True:
        yield from finite_iter
        iter_instance = iter_func(*iter_args)

def data_to_gen():
    with open("data/train_inds.pkl", "rb") as handle:
        train_data = pickle.load(handle)
    pairs = train_data[:, :-1]
    true = train_data[:, -1]
    
    with open("data/emails_token_ids.pkl", "rb") as handle:
        emails = pickle.load(handle)
        
    return gen_X(pairs, emails), gen_Y(true, emails)



def data_to_ls():
    pair_gen, true_gen = data_to_gen()
    return list(pair_gen), list(true_gen)
    
    
    




if __name__ == "__main__":
    
    bert = DistilBertModel.from_pretrained("distilbert-base-uncased")
    bert.eval()

    for param in bert.parameters():
        param.requires_grad = False

    bert.to(device)

    
    
    c = Classifier(bert, word_emb_size=bert.config.dim, lstm_hidden_size=int(2**10), lstm_num_layers=2, 
               clssfr_cell_type=CosineSimilarityClassifierCell, clssfr_hidden_size=0)
    c.to(device)

    
    pairs, true_labels = data_to_list()
    
    
    
    c.fit(pair, true_labels, epochs=100, num_checkpoints
    
    
    
        
    


