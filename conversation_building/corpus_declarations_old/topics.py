import numpy as np
import json

from sklearn.decomposition import LatentDirichletAllocation

#from gensim.corpora.dictionary import Dictionary
#from gensim.sklearn_api import HdpTransformer
#from gensim.models import HdpModel
#from gensim.matutils import Sparse2Corpus



class TopicModel:
    def __init__(self, email_corpus, **kwargs):
        self.model_args = dict(n_components=20, max_iter=200, learning_method='batch',
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
    
    
    def determine_n_components(self, ns_to_search, email_corpus):
        models = {}
        for n in ns_to_search:
            cur_args = {**dict(n_components=n), **self.model_args}
            cur_model = LatentDirichletAllocation(**cur_args).fit(email_corpus.vectorised)
            models[n] = cur_model
            
        print("Perplexities:", [(n, models[n].bound_) for n in ns_to_search])
        return max(models.items(), key=lambda item: item[1].bound_)
            
            
    
    
class Topic:
    def __init__(self, index, word_dist, words=None):
        self.index = index
        self.word_dist = np.asarray(word_dist)
        self.words = words if words else range(self.word_dist.size)
        self.sorted_words = tuple(self.words[i] for i in self.word_dist.argsort())
        
    
    def top_words(self, n):
        return self.sorted_words[:n]
    
    def __repr__(self):
        return f"Topic({self.index}; " + f"{self.top_words(5)}"[1:]
    
    def __hash__(self):
        return hash((self.index, self.word_dist))
    
    def __eq__(self, other):
        if not isinstance(other, Topic):
            return False
        return self.index == other.index and np.array_equal(self.word_dist, other.word_dist)
    
    
    def to_json(self, dumps=False):
        d = {"index": self.index,
             "words": self.words,
             "word_dist": self.word_dist.tolist()}
        
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        params = [json_dict[k] for k in ["index", "word_dist", "words"]]
        return cls(*params)


class TopicInstance:    
    def __init__(self, topic, confidence):
        self.index = topic.index
        self.topic = topic
        self.score = confidence
        
    def __repr__(self):
        return f"Prob[{self.topic}] = {self.score:0.3f}"
    
    def __eq__(self, other):
        if isinstance(other, Topic):
            return self.topic == other
        elif isinstance(other, TopicInstance):
            return self.topic == other.topic
        else:
            return False
        
    def __hash__(self):
        return hash(self.topic)
    
    
    def to_json(self, dumps=False):
        d = dict(score=self.score)
        d["topic"] = self.topic.to_json(dumps=False)
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        topic = Topic.from_json(json_dict["topic"])
        score = json_dict["score"]
        return cls(topic, score)
        