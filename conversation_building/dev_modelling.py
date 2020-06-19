# -*- coding: utf-8 -*-

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from sklearn.decomposition import NMF, LatentDirichletAllocation

from sklearn.mixture import BayesianGaussianMixture

from sklearn.metrics import mutual_info_score, adjusted_mutual_info_score, normalized_mutual_info_score




from tqdm import tqdm
import json
from class_declarations import Conversation

#%%

mailinglist = "ietf-http-wg"
with open(f"email_data/{mailinglist}/all.json") as handle:
    mail_dicts = json.load(handle)

    
short = 50
#convos = [Conversation(subj_str, mail_ls) for period, subj_d in tqdm(list(mail_dicts.items())[:short])
#                for subj_str, mail_ls in subj_d.items()]
#
#
#
#corpus = [e.body.normalised for c in convos[:short] for e in c]



conv_iter = zip(range(short), ((subj_str, mail_ls) for period, subj_d in mail_dicts.items() 
                                            for subj_str, mail_ls in subj_d.items()))

convos = [Conversation(subj_str, mail_ls) for _, (subj_str, mail_ls) in tqdm(conv_iter, total=short)]

corpus = [e.body.normalised for c in convos for e in c]
authors = [e.sender for c in convos for e in c]

#%%

#text = "hello world, I and I go to the beach now"
#text = "I"

#corpus = [text]

no_features = 1000
no_features = None
tf_vectorizer = CountVectorizer(max_df=0.5, min_df=0.1, 
                                max_features=no_features)#, stop_words='spanish')



tf_mat = tf_vectorizer.fit_transform(corpus)
tf_feature_names = tf_vectorizer.get_feature_names()


#%%




no_topics = 20

# Run NMF
#nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

# Run LDA
lda = LatentDirichletAllocation(n_components=no_topics, max_iter=200, learning_method='batch', learning_offset=5000.,random_state=0, verbose=2, n_jobs=-1).fit(tf_mat)


#%%

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()
    

print("\nTopics in LDA model:")
tf_feature_names = tf_vectorizer.get_feature_names()
print_top_words(lda, tf_feature_names, 20)




#%%




vecs = lda.transform(tf_mat)

with open("vecs.tsv", "w") as handle:
    for v in vecs:
        line = "\t".join(list(map(str, v)))
        handle.write(line)
        handle.write("\n")

#authors = [m["author"].replace("\n", "") for m in mails]

with open("authors.tsv", "w") as handle:
    handle.write("\n".join([
            (a.name if a.name else "_") for a in authors
            ]))
#    
#    for v in vecs:
#        line = "\t".join(list(map(str, v)))
#        handle.write(line)
#        handle.write("\n")
#



#%%

# cluster assigned topics
    
    
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=no_topics)
clusters = kmeans.fit_transform(vecs)


#%%

from gensim.corpora.dictionary import Dictionary
from gensim.sklearn_api import HdpTransformer
from gensim.models import HdpModel

tknsd = [t.split() for t in corpus]

dct = Dictionary(tknsd)
bows = [dct.doc2bow(t) for t in tknsd]

hdp = HdpModel(bows, dct)

#%%

hdp.print_topics(num_topics=20, num_words=10)


