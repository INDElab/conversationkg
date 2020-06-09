# -*- coding: utf-8 -*-

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from sklearn.decomposition import NMF, LatentDirichletAllocation

from sklearn.metrics import mutual_info_score, adjusted_mutual_info_score, normalized_mutual_info_score


#%%

#text = "hello world, I and I go to the beach now"
#text = "I"

#corpus = [text]

no_features = 1000
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=0, 
                                max_features=no_features)#, stop_words='spanish')



tf_mat = tf_vectorizer.fit_transform(corpus)
tf_feature_names = tf_vectorizer.get_feature_names()


#%%




no_topics = 20

# Run NMF
#nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

# Run LDA
lda = LatentDirichletAllocation(n_components=no_topics, max_iter=5, learning_method='batch', learning_offset=50.,random_state=0, verbose=2, n_jobs=-1).fit(tf_mat)


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

authors = [m["author"].replace("\n", "") for m in mails]

with open("authors.tsv", "w") as handle:
    handle.write("\n".join(authors))
#    
#    for v in vecs:
#        line = "\t".join(list(map(str, v)))
#        handle.write(line)
#        handle.write("\n")
#

#%%
    
    






