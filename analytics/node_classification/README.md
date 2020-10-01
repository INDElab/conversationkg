# Node Classification - A Testbed for the EmailKG/TextKG Approach

## Reminder: EmailKG and TextKG



## Node Classification 



### Roles in the Conversations

In brief: We use simple, deterministic heuristics 



### Modelling Task

Formally, node classification can be described as learning a function $f$ from a graph $G=(V,E)$ into a probability distribution over node classes given nodes, i.e. for each class $c \in C$ and node $e \in E$ $P(c | e)$. 





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

- the above note not only applies to intersecting the sets of nodes of KGs but also to translating them in a unified way
  => since this is such a pervasive issue, could temporarily change `Person.__hash__` and `Person.__eq__` to reflect this (would affect testing for set membership, testing for equality, dict indexing)
  
  
  
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
    

  
# Appendix A: Implementation Choices

## EmailKG

  - ~~next to the metadata information, EmailKG is also enriched with information form the emails' bodies, such as topic modelling, NER and link extraction; in this sense EmailKG is the more complete source of information (compared to TextKG) on the email corpus since it combines the metadata and the information extracted from bodies~~

## TextKG
  - even though the TextKG is supposed to only contain information form the emails' bodies themselves (no metadata information), we retain information about which emails belong to the same conversation and which conversation took place before which; we keep this information since it may provide important scaffolding for the subgraphs we care about (e.g. Conversations are only connected among each other by the before relation) CHECK

  - we use Stanford's NER algorithm to extract mentions of persons from an email's body (tag PERSON)

## Intersecting EmailKG and TextKG

  - intersecting the triples of EmailKG with those of TextKG is done as follows:

    - the intersection KG's triples are a proper subset of the TextKGs triples 
    - a triple is retained if it contains no entities of type Person (e.g. (Email, part_of, Conversation)) => provides scaffolding for communcative relationships between persons; could be changed
    - a triple which contains at least one Person entity is retained if at least one of the persons is also a node in EmailKG
    - conversely put, a triple is omitted if it contains at least one Person entity but none of the persons are in EmailKG

  - the Person entities in TextKG are discovered by NER, so cannot be literally matched with the Person entities in EmailKG
    => matching is done by person.instance_label.lower(), i.e. the lower-case version of a person's name
    => better matching for the future


## Labelling

  - the intersection scheme above entails that the intersection KG will contain Person entities for which we have no class label (these are obtained only for entities in EmailKG), so we create an additional label for such entities (cf. OOV tokens in NLP) => we want to keep such Persons, since they may provide valuable information about the persons who talked to them

  - the note on Person matching when intersecting EmailKG and TextKG also applies to labelling (i.e. the labels computed for the Person entities on the EmailKG), i.e. we look up the label for persons by their lower-cased name

  - labelling heuristics are computed on the EmailKG and subsequently applied to the intersection KG:

    1. Major Organisations: we define major organisations based on the number of people that belong to them (this is a parameter to the heuristic); for anyone, who isn't part of a major org, we introduce an additional label
    2. Classes based on clustering coefficients: we compute the clustering coefficient of each node and subsequently use k-Means to divide the distribution over coefficients into n classes (n is a parameter);

    3. Random classes: for testing purposes, we assign random labels (out of n classes, a parameter) to entities



# Node Classification - A Test-Case for Inferences from the TextKG onto the EmailKG

## Background

Having introduced two types KGs on the basis of the W3C Mailing List Acrchives, namely the EmailKG and the TextKG, we want to test the extent and quality to which the latter allows inferences onto the former. For a detailed description of the EmailKG and the TextKG, see [REF]; for the purposese of the current experiment, it is important to be aware 


  - testing how well node classes in the EmailKG can be recovered from the TextKG also indicates 



## Approach Outline

  - for now, we use node classification as a testbed but the rationale we argue can be extend to other (arbitrary?) inferential tasks on the EmailKG

  - treating the EmailKG as the ground truth of communicative interactions (who interacted with whom, interlocutors' addresses, which interactions are part of the same conversation), we assume that its characteristics as a graph and knowledge graph will indeed reflect on the characteristics of the held conversations and their interlocutors; for instance, we assume that clustering coefficients computed for the interlocutors are indeed reflective of how central a person is/was in connecting others in conversations

  - at the same time, we do not presume that the information contained in the EmailKG is always available 


## Experiment

### Generation of Data

  1. Extract the EmailKG and the TextKG from the email corpus.
  2. Compute the selected heuristic on the relevant subset of nodes in the EmailKG, leading to a mapping from that subset of nodes to a set of classes.
  3. At least for training purposes, subset the TextKG by taking a subset of its nodes s.t. it ensured that all nodes of the relevant type are mapped to a class in 2. (i.e. that all such nodes are also contained in the EmailKG). This essentially amounts to a form of intersection between the EmailKG and the TextKG, hence we call teh resulting KG IntersectionKG. Since there are many design choices involved in this step, see Appendix A for the details.
  
This process results in a graph, the IntersectionKG in the form of subject-predicate-object triples, and an assignment of nodes of the relevant type to classes.




















