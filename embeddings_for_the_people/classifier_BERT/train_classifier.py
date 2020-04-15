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


from defs_classifier import CosineSimilarityClassifierCell, Classifier


def gen_X(train_X, tknsd_emails):
    for i1, i2 in train_X:
        yield tknsd_emails[i1], tknsd_emails[i2]
        
#         yield torch.tensor(tknsd_emails[i1], dtype=torch.long),\
#               torch.tensor(tknsd_emails[i2], dtype=torch.long)
        
def gen_Y(train_Y, tknsd_emails):
    return iter(torch.tensor(train_Y, dtype=torch.float))

def generate_forever(iter_func, iter_args):
    iter_instance = iter_func(*iter_args)
    while True:
        yield from finite_iter
        iter_instance = iter_func(*iter_args)

def data_to_gen():
    with open("data/train_inds.pkl", "rb") as handle:
        train_data = pickle.load(handle)
    pairs = train_data[:, :-1]
    true = train_data[:, -1:]
    
    with open("data/emails_token_ids.pkl", "rb") as handle:
        emails = pickle.load(handle)
        
    return gen_X(pairs, emails), gen_Y(true, emails)

def data_to_ls():
    pair_gen, true_gen = data_to_gen()
    return list(pair_gen), list(true_gen)
    
    
if __name__ == "__main__":
    """
        data
    
    """
    pairs, true_labels = data_to_ls()
    
    
    """
        parameters
    """
    epochs = 100
    checkpoints = 10
    
    sentence_vector_len = int(2**10)
    

    
    """
        initialisation 
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    
    bert = DistilBertModel.from_pretrained("distilbert-base-uncased")
    bert.eval()

    for param in bert.parameters():
        param.requires_grad = False

    bert.to(device)

    
    c = Classifier(bert, word_emb_size=bert.config.dim, rnn_hidden_size=int(2**10), rnn_num_layers=2, 
               clssfr_cell_type=CosineSimilarityClassifierCell, clssfr_hidden_size=0)
    c.to(device)

    
    
    """
        training
    """
    
    preds, losses = c.fit(pairs, true_labels, epochs=100, num_checkpoints=10)
    
    
    with open(c.checkpoint_folder + "train_predictions.pkl") as handle:
        pickle.dump(preds)
                    
    with open(c.checkpoint_folder + "train_losses.pkl") as handle:
        pickle.dump(losses)
                    
    
    
    
        
    


