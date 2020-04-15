import torch
import torch.nn as nn

# import pickle
# from tqdm import tqdm

class CosineSimilarityClassifierCell(nn.Module):
    def __init__(self, input_size, hidden_size=None, dropout=0.):
        super(CosineSimilarityClassifierCell, self).__init__()
        self.similiarity = nn.CosineSimilarity(dim=1, eps=1e-08)
        self.sigmoid = nn.Sigmoid()
    
    
    def forward(self, inputs):
        vec1, vec2 = inputs
        # inner product instead of concatenation
        sim = self.similarity(vec1, vec2)
        return self.sig(sim)


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
    

# class Classifier(nn.Module):
#     def __init__(self, word_emb_size, lstm_hidden_size, lstm_num_layers, clssfr_cell_type, clssfr_hidden_size):
#         super(Classifier, self).__init__()
        
#         self.is_bidirectional = True
#         self.lstm_hidden_size = lstm_hidden_size
#         self.lstm = nn.LSTM(input_size=word_emb_size, 
#                             hidden_size=lstm_hidden_size, 
#                             num_layers=lstm_num_layers,
#                             dropout=0.2, bidirectional=self.is_bidirectional)
        
#         self.clssfr = clssfr_cell_type(lstm_hidden_size, 
#                                      hidden_size=clssfr_hidden_size,
#                                      dropout=0.2)
        
#     def encode(self, seq, h_0=None, c_0=None):
#         outs, (h_n, c_n) = self.lstm(seq)
        
#         if self.is_bidirectional:
#             forward_out = outs[-1, :, :self.lstm_hidden_size]
#             backward_out = outs[0, :, self.lstm_hidden_size:]
#             return (forward_out+backward_out)/2
#         else:
#             return outs[-1]
        
#     def forward(self, inputs):
#         seq1, seq2 = inputs        
#         enc1, enc2 = self.encode(seq1), self.encode(seq2)
#         return self.clssfr((enc1, enc2))
    
    
#     def fit(self, inputs, true_outputs, epochs=10):
#         # convert inputs & outputs to tensors (batch?)
#         # setup training: optimiser, loss func, train params
#         # keep track of variables: loss and prediction
#         # train loop
        
#         loss_f = torch.nn.BCELoss()
#         optim = torch.optim.Adam(self.parameters(), lr=0.0001)

#         losses, preds = [], []

#         for i in tqdm(range(epochs)):
#             pred = self.forward((one_tens, two_tens))
#             preds.append(pred)
    
#             loss = loss_f(pred, y)
#             losses.append(loss)

#             optim.zero_grad()
#             loss.backward()
#             optim.step()
            
            
            
            
            
            
            
            
            
            
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
       
            
            
def cut_up(mail_tensor, n=512):
    split_tens = mail_tensor.split(n)

    if split_tens[-1].nelement() == split_tens[0].nelement():
        return torch.stack(split_tens), None
    else:
        return torch.stack(split_tens[:-1]), split_tens[-1].unsqueeze(0)       
            
            
            
            
        
        
        
class Classifier(nn.Module):
    def __init__(self, bert_instance, word_emb_size, lstm_hidden_size, lstm_num_layers, clssfr_cell_type, clssfr_hidden_size):
        super(Classifier, self).__init__()
        
        self.bert = bert_instance
        self.bert.eval()
        
        self.is_bidirectional = True
        self.lstm_hidden_size = lstm_hidden_size
        self.lstm = nn.LSTM(input_size=word_emb_size, 
                            hidden_size=lstm_hidden_size, 
                            num_layers=lstm_num_layers,
                            dropout=0.2, bidirectional=self.is_bidirectional)
        
        self.clssfr = clssfr_cell_type(lstm_hidden_size, 
                                       hidden_size=clssfr_hidden_size,
                                       dropout=0.2)
        
        self.chunk_size = 512
    
    def bert_embed(self, text_inds):
        with torch.no_grad():
            chunks, end_chunk = cut_up(text_inds, self.chunk_size) 
            chunks = chunks[:50]
    
            chunks_cuda = chunks.to(device)
            outputs, *_ = bert(chunks_cuda)
  
            outputs_flattened = outputs.view(-1, outputs.shape[-1])
    
            if end_chunk is not None:
                end_cuda = end_chunk.to(device)
                end_output, *_ = bert(end_cuda)
                outputs_flattened = torch.cat((outputs_flattened, end_output.squeeze(0)), 0)

        return outputs_flattened
            
                        
    
    
    def encode(self, seq, h_0=None, c_0=None):
        outs, (h_n, c_n) = self.lstm(seq)
        
        if self.is_bidirectional:
            forward_out = outs[-1, :, :self.lstm_hidden_size]
            backward_out = outs[0, :, self.lstm_hidden_size:]
            return (forward_out+backward_out)/2
        else:
            return outs[-1]
        
    def forward(self, embedded_inputs):
        seq1, seq2 = embedded_inputs        
        enc1, enc2 = self.encode(seq1), self.encode(seq2)
        return self.clssfr((enc1, enc2))
    
    
    def fit(self, inputs, true_outputs, epochs=10):
        # convert inputs & outputs to tensors (batch?)
        # setup training: optimiser, loss func, train params
        # keep track of variables: loss and prediction
        # train loop
        
        loss_f = torch.nn.BCELoss()
        optim = torch.optim.Adam(self.parameters(), lr=0.0001)

        losses, preds = [], []

        for i in tqdm(range(epochs)):
            for (e1, e2), y in zip(inputs, true_outputs):
                embedded_e1, embedded_e2 = self.bert_embed(e1), self.bert_embed(e2)
                pred = self.forward((embedded_e1, embedded_e2))
                preds.append(pred)
    
                loss = loss_f(pred, y)
                losses.append(loss)

                optim.zero_grad()
                loss.backward()
                optim.step()