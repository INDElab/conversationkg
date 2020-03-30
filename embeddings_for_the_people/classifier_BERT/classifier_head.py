import torch
import torch.nn as nn




class Cl(nn.module):
    def __init__(self, ):
        super(Cl, self).__init__()
        
        
        self.lstm = nn.LSTM( 