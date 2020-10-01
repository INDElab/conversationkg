# TODO	

## Programming	

### KGs	

 - unified_translation: should that also use the getter\_function? so that Person entitiies with the same name but different hashes (uses address) receive the same index	

### RoleHeuristics	

 - change RoleHeuristic definition into total function (i.e. move this aspect from the labelling function to attributes of the class)	

 - SendersorReceivers: in the current version of EmailKG, senders and receivers are the only Person entities in the graph; so if sender=1 and receiver=1, no Person entity will be labelled 0	
   => leads to errors in training	


 - SendersorReceivers: re-implement, some of the current logic seems faulty, same for Senders	


### Data	


### Training	

