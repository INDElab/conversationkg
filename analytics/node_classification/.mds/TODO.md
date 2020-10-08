# TODO	

## 

## Programming	

### KGs	

 - perform not only NER for entities tagged PERSON but also other tags, such as orgsanisation or location <br>
   => could potentially introduce more structure in TextKG for the RGCN to learn from
   
 

 - change `__eq__` method of special class OnlyNamePerson to perform approximate, rahter than exact, string matching (Levenshtein or something comparable) <br> 
   -> make threshold a parameter to the class <br>
   => purpose of this change is to create greater overlap between EmailKG and TextKG
   
 

### RoleHeuristics	

 - change RoleHeuristic definition into total function (i.e. move this aspect from the labelling function to attributes of the class)	

 - SendersorReceivers: in the current version of EmailKG, senders and receivers are the only Person entities in the graph; so if sender=1 and receiver=1, no Person entity will be labelled 0
   => leads to errors in training

 - SendersorReceivers: re-implement, some of the current logic seems faulty, same for Senders


### Data	

 - 


### Training

 - exhaustively search labelling heuristics, data parameters & model parameters for the best possible classification result <br>
   => purpose is to determine whether there is any hope at all for learning the classification transfer from the EmailKG to the TextKG


### Models

 - adapt the implementation of the RGCN to accept different sets of triples <br>
   => apply RGCN to different set of triples than it was trained on 

 - try other, simpler models than RGCN:
   - LabelPropagation
   - Non-Negative Matrix Factorization
   - RDF2Vec



