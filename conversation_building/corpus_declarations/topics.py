import numpy as np

from sklearn.decomposition import LatentDirichletAllocation

from gensim.corpora.dictionary import Dictionary
from gensim.sklearn_api import HdpTransformer
from gensim.models import HdpModel
from gensim.matutils import Sparse2Corpus



class TopicModel:
    def __init__(self, email_corpus, level="email", **kwargs):
        self.model_args = dict(n_components=20, max_iter=200, learning_method='batch',
                            learning_offset=5000.,random_state=0, verbose=2, n_jobs=-1)
        
        self.model_args.update(kwargs)
                
        self.model = LatentDirichletAllocation(**self.model_args)
        
        if level == "email":
            self.level = level    
            self.model.fit(email_corpus.vectorised_emails)
        elif level == "conversation":
            self.model.fit(email_corpus.vectorised_conversations)
        else:
            raise ValueError(f"Given level '{level}' not recognised!")
            
        self.topics = [Topic(self.dist) for dist in self.model.components_ /self.model.components_.sum(axis=1)[:, np.newaxis]]
        
        
        
    def assign_topics_to(self, email_corpus, level="email"):
        if level == "email":
            topic_dists = self.model.transform(email_corpus.vectorised_emails)
        elif level == "conversations":
            topic_dists = self.model.transform(email_corpus.vectorised_conversations)
            
    
            
        
        
    
    def determine_n_components(self, ns_to_search, email_corpus):
        models = {}
        for n in ns_to_search:
            cur_args = {**dict(n_components=n), **self.model_args}
            cur_model = LatentDirichletAllocation(**cur_args).fit(email_corpus.vectorised)
            models[n] = cur_model
            
        print("Perplexities:", [(n, models[n].bound_) for n in ns_to_search])
        return max(models.items(), key=lambda item: item[1].bound_)
            
            
    
    
class Topic:
    def __init__(self, word_dist, words=None):
        self.words = words if words else range(word_dist.size)
        self.sorted_words = [self.sorted_words[i] for i in word_dist.argsort()]
        self.word_dist = word_dist
        
    def top_words(self, n):
        return self.sorted_words[:n]
    
    
    
    
#%%
        
def f(x=1, **kwargs):
    print(kwargs)
    return x**2

