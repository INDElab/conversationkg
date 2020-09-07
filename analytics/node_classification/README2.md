

# Implementation Choices

## EmailKG

- next to the metadata information, EMailKG  is also enriched with information form the emails' bodies, such as topic modelling, NER and link extraction; in this sense
  EmailKG is the more complete source of information (compared to TextKG) on the email corpus since it combines the metadata and the information extracted from bodies

## TextKG

- even though the TextKG is supposed to only contain information form the emails' bodies themselves (no metadata information), we retain information about which emails belong to the same conversation and which conversation took place before which; we keep this information since it may provide important scaffolding for the subgraphs we care about (e.g. Conversations are only connected among each other by the `before` relation)
  
- we use Stanford's NER algorithm to extract mentions of persons from an email's body (tag `PERSON`)


## Intersecting EmailKG and TextKG

- intersecting the triples of EmailKG with those of TextKG is done as follows:
  - the intersection KG's triples are a proper subset of the TextKGs triples
  - a triple is retained if it contains no entities of type Person (e.g. (Email, part_of, Conversation)) => provides scaffolding for communcative relationships between persons; could be changed
  - a triples which contains at least one Person entity is retained if at least one of the persons is also a node in EmailKG
  - conversely put, a triple is omitted if it contains at least one Person entity but none of the persons are in EmailKG <br> 


- the Person entities in TextKG are discovered by NER, so cannot be literally matched with the Person entities in EmailKG <br>
  => matching is done by person.instance_label.lower(), i.e. the lower-case version of a person's name <br>
  => better matching for the future
  
  
  
## Labelling

- the intersection scheme above entails that the intersection KG will contain Person entities for which we have no class label 
(these are obtained only for entities in EmailKG), so we create an additional label for such entities (cf. OOV tokens in NLP)
 => we want to keep such Persons, since they may provide valuable information about the persons who talked to them 

- the note on Person matching when intersecting EmailKG and TextKG also applies to labelling (i.e. the labels computed for the Person entities on the EmailKG), 
  i.e. we look up the label for persons by their lower-cased name


- labelling heuristics are computed on the EmailKG and subsequently applied to the intersection KG:
  1. Major Organisations: 
     we define major organisations based on the number of people that belong to them (this is a parameter to the heuristic); 
     for anyone, who isn't part of a major org, we introduce an additional label
     
  2.Classes based on clustering coefficients:
    we compute the clustering coefficient of each node and subsequently use k-Means to divide the distribution over coefficients into n classes (n is a parameter);
    
  3. Random classes:
    for testing purposes, we assign random labels (out of n classes, a parameter) to entities
    

  
