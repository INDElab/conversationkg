import torch
import torch.nn as nn

from time import time, strftime

import os

import pickle
from tqdm import tqdm

class CosineSimilarityClassifierCell(nn.Module):
    def __init__(self, input_size, hidden_size=None, dropout=0.):
        super(CosineSimilarityClassifierCell, self).__init__()
        self.similarity = nn.CosineSimilarity(dim=1, eps=1e-08)
        self.sigmoid = nn.Sigmoid()
    
    
    def forward(self, inputs):
        vec1, vec2 = inputs
        # print("\tclassifier input: ", vec1.shape)

        # inner product instead of concatenation
        sim = self.similarity(vec1, vec2)

        # print("\tsimilarity: ", sim.shape)
        return self.sigmoid(sim)


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
            chunks = chunks[:50]
    
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


    def fit(self, inputs, true_outputs, epochs=10, num_checkpoints=1):
        loss_f = torch.nn.BCELoss()
        optim = torch.optim.Adam(self.parameters(), lr=0.0001)
#         scheduler = ReduceLROnPlateau(optim, verbose=True)

        checkpoint_epochs, path_prefix = self.init_checkpoints(epochs, num_checkpoints)

        losses, preds = [], []

        # print(true_outputs)

        for i in tqdm(range(1, epochs+1)):
            for (e1, e2), y in tqdm(list(zip(inputs, true_outputs)), desc="epoch " + str(i)):
                embedded_e1, embedded_e2 = self.bert_embed(e1).unsqueeze(1), self.bert_embed(e2).unsqueeze(1)
                pred = self.forward((embedded_e1, embedded_e2))
                preds.append(pred.cpu())

                loss = loss_f(pred, y.to(device))
                # print(loss)

                losses.append(loss.cpu())

                optim.zero_grad()
                loss.backward()
                optim.step()
                # scheduler.step(loss)
                # print("--"*30, "\n\n")

            # print(loss)
            if i in checkpoint_epochs:
                self.checkpoint(i, optim, loss, path_prefix)
        return preds, losses


    def init_checkpoints(self, epochs, num_checkpoints):
        checkpoint_epochs = {epochs-i*(epochs//num_checkpoints) for i in reversed(range(num_checkpoints))}
        foldername = "checkpoints_" + strftime("%Y%m%d-%H%M") + "/"

        self.checkpoint_folder = foldername

        os.mkdir(foldername)

        return checkpoint_epochs, foldername

    def checkpoint(self, epoch, optimizer, loss, path=None):
        filename = path + f"Classisifier_epoch_{epoch:02d}.pth"
        
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss}, 
            filename)