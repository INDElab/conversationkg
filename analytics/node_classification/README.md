# Node Classification - recovering the social dynamics of the EmailKG in the TextKG


## Node Classes

- we are primarily interested in persons' roles in the social network of email exchanges in our corpus; such roles include whether someone is a part of a certain organisation (e.g. the W3C) or displays certain patterns of social behaviour

- during pilot experiments, these roles are kept rather general, such as a person's connectivity in a social network, but ultimately we are interested in more detailed roles, such as whether a person belongs to specific small-scale networks of people or whether a person acts rather as an information-giver than an information-taker in interactions

- we define the identification of such roles of people as node classification, i.e. we represent people as nodes in a KG of email interactions (and parts of their contents) and attempt to assign discrete labels to people nodes that are intended to reflect the roles we seek to indentify

- in order to obtain (a proxy of) ground truth for node classification, we generate KGs in two ways: one in which we rely (almost) purely on emails' metadata and another in which we perform actual information extraction from emails' textual bodies and omit (most of the) metadata; roles extracted by (deterministic and simple) heuristics from the former is what we treat as ground truth and we use the latter as a testbed for the ability to recover the extracted roles


## Task Setup

- the goal is to classify persons in our email corpus into social, organisational (and other) groups based on their email exchanges; what makes this task interesting is that we try to recover these groups purely based on the information contained in emails' bodies; in this approach, we treat the emails' protocol information (fact that email was successfully delivered, addresses of sender and receiver, time sent, etc) as the ground truth for social interactions

- formally: given a graph $G = (V, E)$ and a set of classes $C$, a CGN learns a function $f: V -> P(C)$, i.e. for each vertex $v \in V$ and for each class $c \in C$, $f$ assigns a probability of $v$ belonging to class $c$


## Implementation Details


### Roles (i.e. Classes)

We define classes for people in two ways:
  1. according to a heuristic; a simple example is whether or not someone's email address has the domain `w3c.org` (indicating with high certainty that they belong to the W3C)
  2. according to clustering around graph measures; e.g. we calculate betweenness centrality for each vertex in the EmailKG and subsequently cluster nodes according to their centrality score

__Exploration__

- graph measures such as betwenness-centrality follow strongly exponential distributions across vertices, making clustering somewhat meaningless since the vast majority of vertices will belong to the same class

- 

- the clustering coefficient for nodes (taken from `networkx.algorithms.cluster.clustering`) leads to interesting distributions over vertices and has a useful interpretation, namely as a measure which captures how well connected a person is in their local, direct network of interactions; formally, the clustering coefficient is defined as $2T(v)/(deg(v)*(deg(v)-1)))$, where $T(v)$ is the number of triangles through vertex $v$ and $deg(v)$ is its degree; the resulting distribution is more interesting in the sense that density is spread more uniformly over values which in turn leads to more uniformly populated classes after clustering:







### KGs

- we are only interested in classifying members of $P \subset V$, the set of persons in the EmailKG <br>
 => how do we subset $E$? especially in order to retain relations which can potentially help the classification task
 
- we have two KGs: $EmailKG = (V_1, E_1)$ and $TextKG = (V_2, E_2)$ with (generally) $V_1 \not\subset V_2$ and vice versa <br>
 => how do we intersect $EmailKG$ and $TextKG$? <br>
 => for each triple in TextKG, omit the triple from the intersection iff none of the Person entities in it are contained in EmailKG; this implies that Person entities in the intersection graph may not have a label given by the heuristic on EmailKG 
 
### Training Data 

- we are only interested in classifying nodes of type Person but want to retain triples with nodes of other types for a richer set of information to pass to the RGCN <br>
  => problem: RGCN's implementation expects labels for all nodes contained in the triples that are given to it <br>
  => solution: create an addition label which applies to any node not of type Person; this entails that the RGCN additionall learns to classify nodes into Person nodes and non-Person nodes (a hierarchical setting where one model learns this task and a susequent one learns to classify Person nodes should be equivalent)
 

 


## Recipe for Running the Code

- `KGs` contains the definitions of EmailKG, TextKG, their intersection (in terms of Persons) and their translations into indices <br>
  => these KGs are extracted from the email corpus in the script `extract_triples`
  
- `roles` has the heuristics to go from KGs to nodes' labels <br>
  => the KGs are fed into these heuristics in the script `extract_features`
  
- `train_classifier` finally loads the KGs, the labels extracted from them by heuristics and the definitions of the RCGN (by Thiviyan) and trains the latter

# TODOs

## Corpus TODO

- make individual classes such as `Person` and `Email` re-instantiable from JSON by adding a `class: Person` to the JSON and a helper function which handles importing and instantiating classes from strings

- fix StopIteration in getting start_time, occurs when full list of Conversations is used, happens even though years > 1 exist

## Corpus -> EmailKG

- temporal ordering of `Conversation` and `Email` type nodes
- topics of `Conversation` and `Email` type nodes
- sender and receiver of 
- of `Person` type nodes: `Organisation`


## Corpus -> TextKG

 - entities `Conversation` and `Email` have relations `before`, `is_about` (topic), 
 
 - use `spacy` for 'real' NER (not just recognition of WikiData entities), importantly also multiword NER

## Triples -> Graph -> Ground Truth Node Labels

- https://arxiv.org/pdf/physics/0612169.pdf is a potentially very interesting paper (not only) for motivation and intuition

- experiment: get variance of the graph measure distribution's prior by -> subsampling <- important for clustering, as this determines which nodes fall into which classes (-> potential source of noise to the network); also gives an indication for how "naturally" nodes can be assigned to stipulated classes

- IDEA: (based on above paper) graph measures such as betweenness centrality are trivially highly correlated with "popularity" values such as number of emails sent; so e.g. define new measure by dividing betweenness centrality by degree centrality (is this meaningful?) in order to eliminate the correlation
