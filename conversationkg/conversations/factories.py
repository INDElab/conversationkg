import numpy as np
import json

from sklearn.decomposition import LatentDirichletAllocation

from .ledger import Universe
from .entities import KeyWord

# put Topic and TopicInstance in .entities
from .entities import Topic, TopicInstance

# Q: should this be a metaclass?
class Factory:
    def __init__(self):
        pass



class TopicFactory(Factory):
    def __init__(self, email_corpus, n_topics, **kwargs):
        self.model_args = dict(n_components=n_topics, max_iter=200, learning_method='batch',
                            learning_offset=5000.,random_state=0, verbose=2, n_jobs=-1)
        self.model_args.update(kwargs)
        
        self.model = LatentDirichletAllocation(**self.model_args)
        
        self.corpus_fitted = email_corpus
        self.model.fit(email_corpus.vectorised)
            
        normalised = self.model.components_ /self.model.components_.sum(axis=1)[:, np.newaxis]
        
        self.topics = [Topic(i, dist, 
                             email_corpus.vectoriser.get_feature_names()) 
                        for i, dist in enumerate(normalised)]
        
        
        
    def assign_topics_to_emails(self, email_corpus=None):
        if not email_corpus:
            email_corpus = self.corpus_fitted
        topic_dists = self.model.transform(email_corpus.vectorised)
        for dist, email in zip(topic_dists, email_corpus.iter_emails()):
            i = dist.argmax()
            email.topic = TopicInstance(self.topics[i], dist[i])
            Universe.observe(email.topic, email, "evidenced_by")
        

    def assign_topics_to_conversations(self, email_corpus=None):
        if not email_corpus:
            email_corpus = self.corpus_fitted
            
        
        conv_mat = np.ones((len(email_corpus),
                            len(email_corpus.vectoriser.vocabulary_)))
        conv_inds = [i for i, conv in enumerate(email_corpus) for _ in range(len(conv))]
        
        for i, v in zip(conv_inds, email_corpus.vectorised):
            conv_mat[i] += v
        
        topic_dists = self.model.transform(conv_mat)
        
        for dist, conv in zip(topic_dists, email_corpus):
            i = dist.argmax()
            conv.topic = TopicInstance(self.topics[i], dist[i])
            Universe.observe(conv.topic, conv, "evidenced_by")
    
    
    def determine_n_components(self, ns_to_search, email_corpus=None):
        if not email_corpus:
            email_corpus = self.corpus_fitted
        
        models = {}
        for n in ns_to_search:
            cur_args = {**self.model_args, **dict(n_components=n)}
            cur_model = LatentDirichletAllocation(**cur_args).fit(email_corpus.vectorised)
            models[n] = cur_model
            
        print("Perplexities:", [(n, models[n].bound_) for n in ns_to_search])
        return models
    
    
    

class EntityFactory(Factory):
    pass    


class KeyWordFactory(Factory):
    pass
    
    
    