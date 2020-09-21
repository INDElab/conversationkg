# All KGs

- both EmailKG and TextKG contain the "scaffolding" structure of an email corpus: there are temporally ordered conversations which consist of exchanges of temporally ordered emails <br>
 => for practical application, this may still be an assumption (e.g. temporal order may not be given) => **potentially interesting question: can we learn a function which restores the temporal order? (answer will be related to conversational coherence)**


- both KGs contain links, addresses, etc extracted from emails' bodies by **regular expressions** (no ML) <br>
  => this information is included in both since (1: _EmailKG_) mentions of formal language such as http links can be treated as ground truth (accuracy near 100%) and (2: _TextKG_) extracting such mentions is always available  
  
- ~~for now, we include the topic modelling aspect in both KGs, although it strictly speaking does not belong in EmailKG, since the topic to which an email belongs is not part of the ground truth (there is inherent uncertainty about such assignments)~~ topics removed from EmailKG since they are not even used in the heuristic  (which could be interesting) => potentially interesting question: does the presence of topics in TextKG influence performance of the classifier?


## (Vertices, Edges)

 - entities: Conversation, Email, Link, Address
 - relations: before (conv1 before conv2), part_of (email1 part_of conv1), mentions (email1 mentions link1/address1)

# EmailKG

- the intent of the EmailKG is to provide emails' meta-conversational information, such as the interlocutors, their roles in the conversations, organisations they represent, etc

- any gathered information is (heuristically) obtained from the corpus itself and is therefore treated as the ground truth of the conversational social networks present in the corpus

- moreover, we treat the graph properties of the EmailKG as ground truth; so for instance, we treat nodes' degrees or clustering coefficients as reflecting their true value to the degree that the EmailKG is a representative sample of the underlying social network


- in brief: the entities and their relations and properties is what we try to recover using IE algorithms and machine learning on their outputs


## (Vertices, Edges)
  - entities: Person (with both name and address attributes), Address, Organisation (obtained from Address domain)
  - relations: part_of (person1 part_of conv1), evidences (person1 evidences address1/org1), talked_to (person1/org1 talked_to person2/org2)


## Procedural Notes
  - Address entities are obtained from Person entities' address attributes
  - Organisation entities are obtained from Address entities' domains (part of address after @)


# TextKG

