import torch
import torch.nn as nn

from time import time, strftime

import os

import pickle
from tqdm import tqdm
import numpy as np

class CosineSimilarityClassifierCell(nn.Module):
    def __init__(self, input_size, hidden_size=None, dropout=0.):
        super(CosineSimilarityClassifierCell, self).__init__()
        self.similarity = nn.CosineSimilarity(dim=1, eps=1e-08)
        self.sigmoid = nn.Sigmoid()
        self.min_p, self.max_p = self.sigmoid(torch.tensor([-1., 1.]))
    
    
    def forward(self, inputs):
        vec1, vec2 = inputs
        sim = self.similarity(vec1, vec2)
        prob = self.sigmoid(sim)
        return (prob - self.min_p) / (self.max_p - self.min_p)


class InnerProductClassifierCell(nn.Module):
    def __init__(self, input_size, hidden_size=None, dropout=0.):
        super(InnerProductClassifierCell, self).__init__()        
        self.sig = nn.Sigmoid()
        
    
    def forward(self, inputs):
        vec1, vec2 = inputs
        # inner product instead of concatenation
        dot = torch.mm(vec1, vec2.transpose(1,0))
        return self.sig(dot)


class BasicClassifierCell(nn.Module):
    def __init__(self, input_size, hidden_size=None, dropout=0.):
        super(BasicClassifierCell, self).__init__()        
        self.dout = nn.Dropout(dropout)
        self.l = nn.Linear(2*input_size, 1)
        self.sig = nn.Sigmoid()
        
    
    def forward(self, inputs):
        vec1, vec2 = inputs
        # inner product instead of concatenation
        concated = self.dout(torch.cat((vec1, vec2), -1))
        return self.sig(self.l(concated))


class ClassifierCell(nn.Module):
    def __init__(self, input_size, hidden_size=128, dropout=0.):
        super(ClassifierCell, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.dout = nn.Dropout(dropout)
        self.l2 = nn.Linear(2*hidden_size, 1)
        self.sig = nn.Sigmoid()
        
    
    def forward(self, inputs):
        vec1, vec2 = inputs
        a11 = self.relu1(self.l1(vec1))
        a12 = self.relu1(self.l1(vec2))
        concated = self.dout(torch.cat((a11, a12), -1))
        return self.sig(self.l2(concated))






device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# device = torch.device("cpu")

def cut_up(mail_tensor, n=512):
    if mail_tensor.size(0) <= n:
        return mail_tensor.unsqueeze(0), None

    split_tens = mail_tensor.split(n)

    # if split_tens[-1].nelement() == split_tens[0].nelement():
    if mail_tensor.size(0) % n == 0:
        return torch.stack(split_tens), None
    else:
        return torch.stack(split_tens[:-1]), split_tens[-1].unsqueeze(0)       
            
        
class Classifier(nn.Module):    
    def __init__(self, bert_instance, word_emb_size, rnn_hidden_size, rnn_num_layers, clssfr_cell_type, clssfr_hidden_size):
        super(Classifier, self).__init__()
        
        self.bert = bert_instance
        # self.bert.eval()
        
        self.is_bidirectional = True
        self.rnn_hidden_size = rnn_hidden_size
        self.rnn = nn.GRU(input_size=word_emb_size, 
                            hidden_size=rnn_hidden_size, 
                            num_layers=rnn_num_layers,
                            dropout=0.2, bidirectional=self.is_bidirectional)
        
        self.clssfr = clssfr_cell_type(rnn_hidden_size, 
                                       hidden_size=clssfr_hidden_size,
                                       dropout=0.2)#.to(device)
        
        self.chunk_size = 512
    
    def bert_embed(self, text_inds):
        # print("embedding...")
        # print("\t0 ", text_inds.shape)
        with torch.no_grad():
            chunks, end_chunk = cut_up(text_inds, self.chunk_size) 
            chunks = chunks[:20]
    
            chunks_cuda = chunks.to(device)
            outputs, *_ = self.bert(chunks_cuda)
            # outputs = outputs.to("cpu")
  
            outputs_flattened = outputs.view(-1, outputs.shape[-1])
    
            # print("\t1 ", outputs.shape)

            if end_chunk is not None:
                end_cuda = end_chunk.to(device)
                end_output, *_ = self.bert(end_cuda)
                # end_output = end_output.to("cpu")
                # print("\t2 ", end_output.shape)
                # outputs = torch.cat((outputs, end_output), 1)
                outputs_flattened = torch.cat((outputs_flattened, end_output.squeeze(0)), 0)

            # print("\t3 ", outputs_flattened.shape)

            return outputs_flattened
            
                        
    
    
    def encode(self, seq, h_0=None, c_0=None):
        # print("encoding...")
        outs, _ = self.rnn(seq) #(h_n, c_n)
        
        # print("\tlstm output:", outs.shape)
        if self.is_bidirectional:
            forward_out = outs[-1, :, :self.rnn_hidden_size]
            # print("\tforward: ", forward_out.shape)
            backward_out = outs[0, :, self.rnn_hidden_size:]
            # print("\tbackward: ", backward_out.shape)
            return (forward_out+backward_out)/2
        else:
            return outs[-1]
        
    def forward(self, embedded_inputs):
        seq1, seq2 = embedded_inputs        
        enc1, enc2 = self.encode(seq1), self.encode(seq2)
        # print("classifying...")
        # print("\tlstm encoded: ", enc1.shape)
        return self.clssfr((enc1, enc2))

    
    
    def fit(self, inputs, true_outputs, epochs=10, batch_size=32, num_checkpoints=1, validation_data=None, save_to="./"):
        loss_f = torch.nn.BCELoss()
        optim = torch.optim.Adam(self.parameters(), lr=0.01, amsgrad=False, weight_decay=0.05)
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optim, patience=2, threshold=0.001, verbose=True)

        checkpoint_epochs, path_prefix = self.init_checkpoints(epochs, num_checkpoints, save_to)
        
        losses, preds = [], []
    
        for i in tqdm(range(1, epochs+1)):
            permutation_inds = np.random.permutation(len(inputs))
            permuted_inputs = [inputs[i] for i in permutation_inds]
            permuted_true_outputs = torch.tensor([true_outputs[i] for i in permutation_inds])
            
            for j in tqdm(list(range(0, len(inputs), batch_size)), desc="Epoch " + str(i)):
                batch_inputs = permuted_inputs[j:j+batch_size]
                batch_true_outputs = permuted_true_outputs[j:j+batch_size].to(device)
                batch_preds = torch.zeros(len(batch_inputs)).to(device)
                for k, (e1, e2) in list(enumerate(batch_inputs)):
                    embedded_e1, embedded_e2 = self.bert_embed(e1).unsqueeze(1), self.bert_embed(e2).unsqueeze(1)
                    pred = self.forward((embedded_e1, embedded_e2))
                    
                    batch_preds[k] = pred
                    preds.append(pred.cpu())
                    
                loss = loss_f(batch_preds, batch_true_outputs)
                losses.append(loss.cpu())
                
                optim.zero_grad()
                loss.backward()
                optim.step()
            if i in checkpoint_epochs:
                mean_val_loss = self.checkpoint(i, optim, losses, preds, 
                                                validation_data=validation_data, loss_f=loss_f, path=path_prefix)
            
                scheduler.step(mean_val_loss)
        return preds, losses
    
    def validate(self, val_data, loss_f):
        pairs, labels = val_data
        k = len(pairs)
        with torch.no_grad():
            vecs1 = torch.zeros((k, self.rnn_hidden_size)).to(device)
            vecs2 = torch.zeros((k, self.rnn_hidden_size)).to(device)
            probs = torch.zeros(k).to(device)
            losses = torch.zeros(k).to(device)
            
            with torch.no_grad():
                for j, (e1, e2) in tqdm(enumerate(pairs), total=k, desc="\tValidating"):
                    embedded_e1, embedded_e2 = self.bert_embed(e1).unsqueeze(1), self.bert_embed(e2).unsqueeze(1)
                    encoded_e1, encoded_e2 = self.encode(embedded_e1), self.encode(embedded_e2)
                    prob = self.clssfr((encoded_e1, encoded_e2))
                    
                    val_loss = loss_f(prob, labels[j].to(device))

                    vecs1[j] = encoded_e1
                    vecs2[j] = encoded_e2
                    probs[j] = prob
                    losses[j] = val_loss
        
        return vecs1.cpu(), vecs2.cpu(), probs.cpu(), losses.cpu()
        

    def init_checkpoints(self, epochs, num_checkpoints, save_to="./"):
        checkpoint_epochs = {epochs-i*(epochs//num_checkpoints) for i in reversed(range(num_checkpoints))}
        foldername = save_to + "checkpoints_" + strftime("%Y%m%d-%H%M") + "/"

        self.checkpoint_folder = foldername
        os.mkdir(foldername)
        return checkpoint_epochs, foldername

    
    def checkpoint(self, epoch, optimizer, losses, preds, validation_data=None, loss_f=None, path=""):        
        if validation_data:
            vecs1, vecs2, val_probs, val_losses = self.validate(validation_data, loss_f)
            with open(path + f"validation_epoch_{epoch:02d}.pth", "wb") as handle:
                pickle.dump({
                    "vecs1": vecs1,
                    "vecs2": vecs2,
                    "probs": val_probs,
                    "losses": val_losses}, handle)
            print("\nStd. Dev. Validation Probs:\t", round(torch.var(val_probs).item()**.5, 4), flush=True)
            print("Avg. Validation Loss:\t", round(torch.mean(val_losses).item(), 4), flush=True)
            
        
        with open(path + "train_losses.pkl", "wb") as handle:
            pickle.dump(losses, handle)
        
        with open(path + "train_preds.pkl", "wb") as handle:
            pickle.dump(preds, handle)
        
        filename = path + f"Classifier_epoch_{epoch:02d}.pth"
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': losses[-1]}, 
            filename)
        
        if validation_data:
            return torch.mean(losses)
        else:
            return None


    @classmethod
    def from_checkpoint(cls, chkpt_dir, model_params, chkpt_name="best", load_params=(None, )):
        if chkpt_name == "best":
            loaded_model = None
            lowest_loss = 10**6
            for f in tqdm(os.listdir(chkpt_dir)):
                cur_loaded = torch.load(chkpt_dir + f, *load_params)
                if cur_loaded["loss"] < lowest_loss:
                    lowest_loss = cur_loaded["loss"]
                    loaded_model = cur_loaded
        elif chkpt_name == "latest":
            latest_fname = [f for f in sorted(os.listdir(chkpt_dir)) if f.startswith("Classifier_epoch_")][-1]
            loaded_model = torch.load(chkpt_dir + latest_fname, *load_params)
        else:
            loaded_model = torch.load(chkpt_dir + chkpt_name, *load_params)
            
        print("Loaded", flush=True)
        print("\tepoch: ", loaded_model["epoch"], flush=True)
        print("\tloss: ", loaded_model["loss"], flush=True)
                                      
                                      
        c = cls(*model_params)
        c.load_state_dict(loaded_model['model_state_dict'])
        return c, loaded_model
    
    
    
    def resume_fit(self, inputs, true_outputs, optimizer_state, initial_epoch, 
                   epochs=10, batch_size=32, num_checkpoints=1, validation_data=None, save_to="./"):
        
        loss_f = torch.nn.BCELoss()
        optim = torch.optim.AdamW(self.parameters(), lr=0.001, amsgrad=True, weight_decay=0.01)
        optim.load_state_dict(optimizer_state)
        print("Optimizer: AdamW lr=0.001, amsgrad=True, weight_decay=0.01", flush=True)

        path_prefix = save_to
        checkpoint_epochs = {epochs-i*(epochs//num_checkpoints) for i in reversed(range(num_checkpoints))}
        
        with open(path_prefix + "train_losses.pkl", "rb") as handle:
            losses = pickle.load(handle)
        
        with open(path_prefix + "train_preds.pkl", "rb") as handle:
            preds = pickle.load(handle)
        
#         losses, preds = [], []
    
        for i in tqdm(range(1, epochs+1)):
            permutation_inds = np.random.permutation(len(inputs))
            permuted_inputs = [inputs[i] for i in permutation_inds]
            permuted_true_outputs = torch.tensor([true_outputs[i] for i in permutation_inds])
            
            for j in tqdm(list(range(0, len(inputs), batch_size)), desc="Epoch " + str(i)):
                batch_inputs = permuted_inputs[j:j+batch_size]
                batch_true_outputs = permuted_true_outputs[j:j+batch_size].to(device)
                batch_preds = torch.zeros(len(batch_inputs)).to(device)
                for k, (e1, e2) in list(enumerate(batch_inputs)):
                    embedded_e1, embedded_e2 = self.bert_embed(e1).unsqueeze(1), self.bert_embed(e2).unsqueeze(1)
                    pred = self.forward((embedded_e1, embedded_e2))
                    
                    batch_preds[k] = pred
                    preds.append(pred.cpu())
                    
                loss = loss_f(batch_preds, batch_true_outputs)
                losses.append(loss.cpu())
                
                optim.zero_grad()
                loss.backward()
                optim.step()
            if i in checkpoint_epochs:
                self.checkpoint(i+initial_epoch, optim, losses, preds, 
                                validation_data=validation_data, loss_f=loss_f, path=path_prefix)
                
        return preds, losses

    

    

    
# ======================
#  OLD FITTING FUNCTION    
# ======================
    
#     def fit(self, inputs, true_outputs, epochs=10, batch_size=32, num_checkpoints=1, validation_data=None, save_to="./"):
#         loss_f = torch.nn.BCELoss()
#         optim = torch.optim.AdamW(self.parameters(), lr=0.001, amsgrad=True, weight_decay=0.01)
# #         scheduler = ReduceLROnPlateau(optim, verbose=True)

#         checkpoint_epochs, path_prefix = self.init_checkpoints(epochs, num_checkpoints, save_to)

#         losses, preds = [], []


#         for i in tqdm(range(1, epochs+1)):
#             for (e1, e2), y in tqdm(list(zip(inputs, true_outputs)), desc="Epoch " + str(i)):
#                 embedded_e1, embedded_e2 = self.bert_embed(e1).unsqueeze(1), self.bert_embed(e2).unsqueeze(1)
#                 pred = self.forward((embedded_e1, embedded_e2))
#                 preds.append(pred.cpu())

#                 loss = loss_f(pred, y.to(device))
#                 # print(loss)

#                 losses.append(loss.cpu())

#                 optim.zero_grad()
#                 loss.backward()
#                 optim.step()
#                 # scheduler.step(loss)
#                 # print("--"*30, "\n\n")

#             # print(loss)
#             if i in checkpoint_epochs:
#                 self.checkpoint(i, optim, losses, preds, 
#                                 validation_data=validation_data, loss_f=loss_f, path=path_prefix)
#         return preds, losses