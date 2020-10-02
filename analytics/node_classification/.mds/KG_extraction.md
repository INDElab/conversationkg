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
  - entities: Person (with both name and address attributes), Address, Organisation
  - relations: part_of (person1 part_of conv1), evidences (person1 evidences address1/org1), talked_to (person1/org1 talked_to person2/org2)


## Procedural Notes
  - any interlocutor (whether sender or receiver or both) is in the part_of relation with the conversation entity
  - the interlocutors' organisations are also in the part_of relation with the conversation entity
  - Address entities are obtained from Person entities' address attributes
  - Organisation entities are obtained from Address entities' domains (part of address after @)


# TextKG

  - besides the "scaffolding" structure mentioned above (see [All KGs](#all-kgs)), the TextKG is obtained purely from IE methods; that is, all information contained in TextKG originates from emails' bodies
  

## (Vertices, Edges)

  - entities: Person (only name attribute), Topics
  - relations: about (conv1 about topic1), mentions (email1 mentions person1), talked_to (person1 talked_to person2)

## Procedural Notes

  - the Person entities in EmailKG are discovered from emails' text bodies by spacy's NER system (entities tagged PERSON) -- for this reason, the Person entities have only name attributes and even for those often only first names, alternate spellings, etc. => entity resolution would be in order
  
  - for each pair of Person entities, person1 and person2, discovered by the NER we add the relation (person1 talked_to person2), postulating that person1 is the email's sender and person2 its receiver => this overly simple heuristic could be improved upon to further simplify downstream tasks

  - topic modelling:
    - we use LDA with a uniformly initialised topic prior
    - using a grid search, we select a number of topics that minimises perplexity on the set of document
    - fitting the topic and word distributions of LDA is done on the entire email corpus
    - when constructing TextKG, both emails (via their bodies) and conversations (word counts of conversation's emails are simply added) are assigned to topics
