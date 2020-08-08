# Triples -> Graph -> Ground Truth Node Labels


- `networkx` can take any object as nodes, so do not need to be translated before adding to graph -> makes it easier to discern relevant node types, i.e. `Person`

- make individual classes such as `Person` and `Email` re-instantiable from JSON by adding a `class: Person` to the JSON and a helper function which handles importing and instantiating classes from strings

- e.g. `networkx.algorithms.cluster.clustering` + `sklearn.cluster.KMeans(n_cluster=3` yields relatively equally populated classes of nodes (could be interpreted as low clustering, intermediate clustering, high clustering); the clustering value given by `networkx` is proportional to the number of triangles through a node divided by the node's degree
