# Corpus TODO


- make individual classes such as `Person` and `Email` re-instantiable from JSON by adding a `class: Person` to the JSON and a helper function which handles importing and instantiating classes from strings

- fix StopIteration in getting start_time, occurs when full list of Conversations is used, happens even though years > 1 exist

# Corpus -> EmailKG

- temporal ordering of `Conversation` and `Email` type nodes
- topics of `Conversation` and `Email` type nodes
- sender and receiver of 
- of `Person` type nodes: `Organisation`


# Corpus -> TextKG

 - entities `Conversation` and `Email` have relations `before`, `is_about` (topic), 
 
 - use `spacy` for 'real' NER (not just recognition of WikiData entities), importantly also multiword NER

# Triples -> Graph -> Ground Truth Node Labels


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
