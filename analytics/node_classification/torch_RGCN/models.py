from torch_RGCN.layers import RelationalGraphConvolution
from torch_RGCN.utils import add_inverse_and_self
import torch.nn.functional as F
from torch import nn
import torch



class NodeClassifier(nn.Module):
    """ Node classification with R-GCN message passing """
    def __init__(self,
                 triples=None,
                 nnodes=None,
                 nrel=None,
                 nfeat=None,
                 nhid=16,
                 nlayers=2,
                 nclass=None,
                 edge_dropout=None,
                 decomposition=None,
                 nemb=None):
        super(NodeClassifier, self).__init__()

        self.nlayers = nlayers

        assert (triples is not None or nnodes is not None or nrel is not None or nclass is not None), \
            "The following must be specified: triples, number of nodes, number of relations and number of classes!"
        assert 0 < nlayers < 3, "Only supports the following number of RGCN layers: 1 and 2."

        if nlayers == 1:
            nhid = nclass

        if nlayers == 2:
            assert nhid is not None, "Number of hidden layers not specified!"

        triples = torch.tensor(triples, dtype=torch.long)
        with torch.no_grad():
            self.register_buffer('triples', triples)
            # Add inverse relations and self-loops to triples
            self.register_buffer('triples_plus', add_inverse_and_self(triples, nnodes, nrel))

        self.rgc1 = RelationalGraphConvolution(
            triples=self.triples_plus,
            num_nodes=nnodes,
            num_relations=nrel * 2 + 1,
            in_features=nfeat,
            out_features=nhid,
            edge_dropout=edge_dropout,
            decomposition=decomposition,
            vertical_stacking=False
        )
        if nlayers == 2:
            self.rgc2 = RelationalGraphConvolution(
                triples=self.triples_plus,
                num_nodes=nnodes,
                num_relations=nrel * 2 + 1,
                in_features=nhid,
                out_features=nclass,
                edge_dropout=edge_dropout,
                decomposition=decomposition,
                vertical_stacking=True
            )

    def forward(self):
        """ Embed relational graph and then compute class probabilities """
        x = self.rgc1()

        if self.nlayers == 2:
            x = F.relu(x)
            x = self.rgc2(features=x)

        return x
    
    
class EmbeddingNodeClassifier(NodeClassifier):
    """ Node classification model with node embeddings as the feature matrix """
    def __init__(self,
                 triples=None,
                 nnodes=None,
                 nrel=None,
                 nfeat=None,
                 nhid=16,
                 nlayers=2,
                 nclass=None,
                 edge_dropout=None,
                 decomposition=None,
                 nemb=None):

        assert nemb is not None, "Size of node embedding not specified!"
        nfeat = nemb  # Configure RGCN to accept node embeddings as feature matrix

        super(EmbeddingNodeClassifier, self)\
            .__init__(triples, nnodes, nrel, nfeat, nhid, nlayers, nclass, edge_dropout, decomposition)

        # Node embeddings
        self.node_embeddings = nn.Parameter(torch.FloatTensor(nnodes, nemb))

        # Initialise Parameters
        nn.init.xavier_uniform_(self.node_embeddings)

    def forward(self):
        """ Embed relational graph and then compute class probabilities """
        x = self.rgc1(self.node_embeddings)

        if self.nlayers == 2:
            x = F.relu(x)
            x = self.rgc2(features=x)

        return x