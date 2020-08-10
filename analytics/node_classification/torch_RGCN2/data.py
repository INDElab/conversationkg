# -*- coding: utf-8 -*-

import os
import pickle
import pandas as pd
import gzip
from collections import Counter
import tqdm
import rdflib as rdf
from rdflib import URIRef


S = os.sep


def locate_file(filepath):
    directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return directory + '/' + filepath

def st(node):
    """
    Maps an rdflib node to a unique string. We use str(node) for URIs (so they can be matched to the classes) and
    we use .n3() for everything else, so that different nodes don't become unified.
    Source: https://github.com/pbloem/gated-rgcn/blob/1bde7f28af8028f468349b2d760c17d5c908b58b/kgmodels/data.py#L16
    """
    if type(node) == URIRef:
        return str(node)
    else:
        return node.n3()


def add_neighbors(set, graph, node, depth=2):
    """
    Adds neighboring nodes that are n nodes away from the target label
    Source: https://github.com/pbloem/gated-rgcn/blob/f5031a3cbb485aab964aea7b6856d0584155c820/kgmodels/data.py#L29
    """
    if depth == 0:
        return

    for s, p, o in graph.triples((node, None, None)):
        set.add((s, p, o))
        add_neighbors(set, graph, o, depth=depth-1)

    for s, p, o in graph.triples((None, None, node)):
        set.add((s, p, o))
        add_neighbors(set, graph, s, depth=depth-1)



def load_node_classification_data(name, use_test_set=False, limit=None, enable_cache=True, val_prop=0.4, prune=False):
    """
    Load knowledge graphs for node classification experiment.
    Source: https://github.com/pbloem/gated-rgcn/blob/1bde7f28af8028f468349b2d760c17d5c908b58b/kgmodels/data.py#L42
    :param name: Dataset name ('aifb', 'am', 'bgs' or 'mutag')
    :param use_test_set: If true, load the canonical test set, otherwise split a validation set off from the training data.
    :param limit: If set, the number of unique relations will be limited to this value, plus one for the self-connections,
                  plus one for the remaining connections combined into a single, new relation.
    :param prune: Whether to prune edges that are further than two steps from the target labels
    :param disable_cache: If true, does not load from cache.
    :param val_prop: Size of the validation split from the training data (Default: 0.4).
    :return: A list containing the graph data, and the node classification test and train sets:
              - edges: list of edges [subject, predicate object]
    """
    REST = '.rest'
    INV = 'inv.'

    # Check if the data has been cached for quick loading.
    cachefile = locate_file(f'data{S}{name.lower()}{S}cache'
                            f'{"_test" if use_test_set else "_validation"}'
                            f'{"_prune" if prune else ""}.pkl')
    if enable_cache and os.path.isfile(cachefile) and limit is None:
        print('Using cached data...')
        with open(cachefile, 'rb') as file:
            data = pickle.load(file)
            print('Loaded.')
            return data
    print('Loading data from scratch...')

    if name.lower() == 'aifb':
        file = locate_file('data/aifb/aifb_stripped.nt.gz')
        train_file = locate_file('data/aifb/trainingSet.tsv')
        test_file = locate_file('data/aifb/testSet.tsv')
        label_header = 'label_affiliation'
        nodes_header = 'person'
    elif name.lower() == 'am':
        file = locate_file('data/am/am_stripped.nt.gz')
        train_file = locate_file('data/am/trainingSet.tsv')
        test_file = locate_file('data/am/testSet.tsv')
        label_header = 'label_cateogory'
        nodes_header = 'proxy'
    elif name.lower() == 'bgs':
        file = locate_file('data/bgs/bgs_stripped.nt.gz')
        train_file = locate_file('data/bgs/trainingSet(lith).tsv')
        test_file = locate_file('data/bgs/testSet(lith).tsv')
        label_header = 'label_lithogenesis'
        nodes_header = 'rock'
    elif name.lower() == 'mutag':
        file = locate_file('/data/mutag/mutag_stripped.nt.gz')
        train_file = locate_file('/data/mutag/trainingSet.tsv')
        test_file = locate_file('/data/mutag/testSet.tsv')
        label_header = 'label_mutagenic'
        nodes_header = 'bond'
    else:
        raise ValueError(f'Could not find \'{name}\' dataset')

    labels_train = pd.read_csv(train_file, sep='\t', encoding='utf8')
    if use_test_set:
        labels_test = pd.read_csv(test_file, sep='\t', encoding='utf8')
    else:
        # Split the training data into train and validation
        ltr = labels_train
        pivot = int(len(ltr) * val_prop)

        labels_test = ltr[:pivot]
        labels_train = ltr[pivot:]

    labels = labels_train[label_header].astype('category').cat.codes
    train = {}
    for nod, lab in zip(labels_train[nodes_header].values, labels):
        train[nod] = lab

    labels = labels_test[label_header].astype('category').cat.codes
    test = {}
    for nod, lab in zip(labels_test[nodes_header].values, labels):
        test[nod] = lab

    print('Labels loaded.')

    # Parse the data with RDFLib
    graph = rdf.Graph()

    if file.endswith('nt.gz'):
        with gzip.open(file, 'rb') as f:
            graph.parse(file=f, format='nt')
    else:
        graph.parse(file, format=rdf.util.guess_format(file))

    print('RDF loaded.')

    # Collect all node and relation labels
    if prune:
        triples = set()
        for node in list(train.keys()) + list(test.keys()):
            add_neighbors(triples, graph, URIRef(node), depth=2)

    else:
        triples = graph

    nodes = set()
    relations = Counter()

    for s, p, o in triples:
        nodes.add(st(s))
        nodes.add(st(o))

        relations[st(p)] += 1

    i2n = list(nodes) # maps indices to labels
    n2i = {n:i for i, n in enumerate(i2n)} # maps labels to indices

    # Truncate the list of relations if necessary
    if limit is not None:
        i2r = [r[0] for r in  relations.most_common(limit)] + [REST, INV+REST]
        # the 'limit' most frequent labels are maintained, the rest are combined into label REST to save memory
    else:
        i2r =list(relations.keys())

    r2i = {r: i for i, r in enumerate(i2r)}

    # Collect all edges into a list: [from, relation, to] (only storing integer indices)
    edges = list()
    for s, p, o in tqdm.tqdm(triples):
        s, p, o = n2i[st(s)], st(p), n2i[st(o)]
        pf = r2i[p] if (p in r2i) else r2i[REST]
        edges.append([s, pf, o])

    print('Graph loaded.')

    # Cache the results for fast loading next time
    if limit is None and enable_cache:
        with open(cachefile, 'wb') as file:
            pickle.dump([edges, (n2i, i2n), (r2i, i2r), train, test], file)

    return edges, (n2i, i2n), (r2i, i2r), train, test