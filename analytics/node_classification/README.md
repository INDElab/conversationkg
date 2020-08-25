# Node Classification - recovering the social dynamics of the EmailKG in the TextKG


## Node Classes

- we are primarily interested in persons' roles in the social network of email exchanges in our corpus; such roles include whether someone is a part of a certain organisation (e.g. the W3C) or to what  



## Task Setup

- the goal is to classify persons in our email corpus into social, organisational (and other) groups based on their email exchanges; what makes this task interesting is that we try to recover these groups purely based on the information contained in emails' bodies; in this approach, we treat the emails' protocol information (fact that email was successfully delivered, addresses of sender and receiver, time sent, etc) as the ground truth for social interactions

- formally: given a graph $G = (V, E)$ and a set of classes $C$, a CGN learns a function $f: V -> P(C)$, i.e. for each vertex $v \in V$ and for each class $c \in C$, $f$ assigns a probability of $v$ belonging to class $c$

- during training of the CGN, we use labels 


## Implementation Details


### Roles (i.e. Classes)


- we define classes for people in two ways:
  1. according to a heuristic; a simple example is whether or not someone's email address has the domain `w3c.org` (indicating with high certainty that they belong to the W3C)
  2. according to clustering around graph measures; e.g. we calculate betweenness centrality for each vertex in the EmailKG and subsequently cluster nodes according to their centrality score



- graph measures such as betwenness-centrality follow strongly exponential distributions across vertices, making clustering somewhat meaningless since the vast majority of vertices will belong to the same class

- the clustering coefficient for nodes (taken from `networkx.algorithms.cluster.clustering`) leads to interesting distributions over vertices and has a useful interpretation (?)





### KGs

- we are only interested in classifying members of $P \subset V$, the set of persons in the EmailKG <br>
 => how do we subset $E$? especially in order to retain relations which can potentially help the classification task
 
- we have two KGs: $EmailKG = (V_1, E_1)$ and $TextKG = (V_2, E_2)$ with (generally) $V_1 \not\subset V_2$ and vice versa <br>
 => how do we intersect $EmailKG$ and $TextKG$?
 

 


## Recipe for Running the Code

- `KGs` contains the definitions 
- `extract_triples` 

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


- `networkx` can take any _hashable_ object as nodes, so do not need to be translated before adding to graph -> makes it easier to discern relevant node types, i.e. `Person`


- e.g. `networkx.algorithms.cluster.clustering` + `sklearn.cluster.KMeans(n_cluster=3` yields relatively equally populated classes of nodes (could be interpreted as low clustering, intermediate clustering, high clustering); the clustering value given by `networkx` is proportional to the number of triangles through a node divided by the node's degree

- https://arxiv.org/pdf/physics/0612169.pdf is a potentially very interesting paper (not only) for motivation and intuition

- experiment: get variance of the graph measure distribution's prior by -> subsampling <- important for clustering, as this determines which nodes fall into which classes (-> potential source of noise to the network); also gives an indication for how "naturally" nodes can be assigned to stipulated classes

- TODO: find better method/justification for clustering of node values

- IDEA: (based on above paper) graph measures such as betweenness centrality are trivially highly correlated with "popularity" values such as number of emails sent; so e.g. define new measure by dividing betweenness centrality by degree centrality (is this meaningful?) in order to eliminate the correlation


##

Algorithm: 

Given a set of triples $T = \{(e_{i1}, p_{k1}, e_{j1}), ...\}$, construct the graph $G = (V, E)$ with $V$ the set of 

note: edge types are omitted, the resulting graph has only a single edge type
note: the set of vertices in the graph is the union of the set of subjects and objects in triples in $T$
