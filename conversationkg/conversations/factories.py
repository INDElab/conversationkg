import numpy as np
import json
from tqdm import tqdm

from functools import reduce

# topic modelling
from sklearn.decomposition import LatentDirichletAllocation

# named entity recognition
import spacy
import stanza

# keyword extraction
from rake_nltk import Rake


#from .ledger import Universe
from .entities import Entity, StringEntity
from .entities import Topic, TopicInstance
from .entities import Person, Organisation
from .entities import KeyWord

from sklearn.feature_extraction.text import TfidfVectorizer as tfidf
from sklearn.feature_extraction.text import CountVectorizer as count


class FactoryChain:
    """
    Not Implemented (yet). Idea is to wrap a sequence of factory classes into this FactoryChain
    which runs the factories on a corpus. 
    Most important use: Some factories depend on the output of others (e.g. TopicFactory depends on VectorFactory), 
    so the FactoryChain could help ensure that factories are executed in the correct order and produce meaningful
    error messages if this is not the case (rather than pure AttributeErrors).
    Other uses: FactoryChain could keep track of the factories that have been applied, gather statistics,
    help parallelisation, preform preparation and postprocessing tasks, etc.
    """
    def __init__(*classes, **keyword_args):
        """
        FactoryChain is initialised with a list of factory classes and keyword arguments, where
        each key is expected to be the name of a factory class and the value is a dict of parameters
        for that factory, e.g. CountVectoriser=dict(max_df=0.7, min_df=5). 
        """
#        no_dependencies = {c for c in classes if getattr(c, "depends_on", None) is None}
        for c in classes:
            if c.depends_on not in classes:
                raise ValueError(f"Factory {c} depends on {c.depends_on} but the latter"
                                 f"is not in the given chain of classes!")
                



from joblib import Parallel, delayed

class Factory:
    """
    The base class for any specialised factory family, such as VectorFactory, TopicFactory, etc.
    Use this class as base class to create a new factory family; perhaps for instance a StatsFactory 
    for a family of factories which observe statistics about emails and conversations and attach those to both.
    
    TODO:
        - default __init__? -> perhaps for checks if subclassing factory family is well-defined?
        - default __call__ function with basic functionality (that factories override if necessary)
        - parallelisation (including parameters)
    """
    
    def __init__(self):
        raise NotImplementedError
    
    
    def process_conversation(self, conversation):
        raise NotImplementedError
    
    def process_email(self, email):
        raise NotImplementedError
        
        
    def parallelise_call(self, conversation_iter, n_jobs=-1, processing_function=None):
        if processing_function is None:
            processing_function = self.process_conversation
        delayed_func = delayed(processing_function)
        # Parallel(n_jobs=n_jobs, require='sharedmem')
        return Parallel(n_jobs=n_jobs)(delayed_func(conv) for conv in conversation_iter)
    
    
    def __call__(self, corpus, parallel=True, n_jobs=-1):
        progressbar = tqdm(corpus, 
                           desc=f"{self.__class__.__name__} iterating conversations"
                                f" {'in parallel' if parallel else ''}")
        
        if parallel:
            return self.parallelise_call(progressbar, n_jobs)
        else:
            processed_conversations = list(map(self.process_conversation, progressbar))
            
        return processed_conversations
        
    
    
    @staticmethod
    def combine_processors(*processors):
        """
        Convenience function which combines a list of processors (i.e. functions) into a single one, equivalent to
        mathematical function composition. In terms of call order, the function at the first index of the list 
        is called last, while the function at the last index is called first (**unlike** the convention in 
        function composition).
        May be unsafe to use if the given functions take and return different numbers and types of arguments.
        
        Usage example:
            to_lower = str.lower
            remove_outer_whitespace = str.strip
            remove_comma = lambda s: s.replace(",", "")
            str_normaliser = Factory.combine_processors([remove_comma, remove_outer_whitespace, to_lower])
        """
        return reduce(lambda f, g: lambda x: f(g(x)), processors, lambda x: x)
#        return reduce(lambda f, g: lambda *x, **y: f(g(*x, **y)), processors, lambda *x, **y: (x, y))


class VectorFactory(Factory):
    def __init__(self, corpus, vectoriser_algorithm, add_matrix_to_corpus=True, **vectoriser_kwargs):
        default_args = dict(max_df=0.7, min_df=5)
        default_args.update(vectoriser_kwargs)

        self.fitted_corpus = corpus
        self.add_matrix = add_matrix_to_corpus
        
        self.vectoriser = vectoriser_algorithm(**default_args)
        self.matrix = self.vectoriser.fit_transform([
                            email.body.normalised for email in corpus.iter_emails()
                        ])
        self.conversation_matrix = self.vectoriser.transform(
                                    [conv.get_email_bodies(attr="normalised", join_str=" ") for conv in corpus]
                                    )        
        
        self.vocabulary = self.vectoriser.get_feature_names()
        

    def process_conversation(self, conversation):
        conversation.vectorised = next(self.conv_iter)
        for email in conversation:
            email_vector = self.process_email(email)
        return conversation.vectorised
    
    def process_email(self, email):
        email.body.vectorised = next(self.email_iter)
        return email.body.vectorised


    def __call__(self, corpus=None, **kwargs):
        if not corpus:
            corpus = self.fitted_corpus
        
        if self.add_matrix:
            corpus.vectorised_vocabulary = self.vocabulary
            corpus.vectorised = self.matrix
            corpus.conversations_vectorised = self.conversation_matrix        
        
        self.conv_iter = iter(self.conversation_matrix)
        self.email_iter = iter(self.matrix)
        
        return super().__call__(corpus, **kwargs)
        

#        if not corpus:
#            corpus = self.fitted_corpus
#        conv_matrix = self.conversation_matrix
#        email_ind = 0
#        for i, conv in enumerate(corpus):
#            conv.vector = conv_matrix[i]
#            for email in conv:
#                email.body.vectorised = self.matrix[email_ind]
#                email_ind += 1
#                
#        if self.add_matrix:
#            corpus.vectorised_vocabulary = self.vocabulary
#            corpus.vectorised = self.matrix
#            corpus.conversations_vectorised = self.conversation_matrix
                

class CountVectorizer(VectorFactory):
    """
    Wrapper for scikit-learn's equally-named [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html).
    
    """
    def __init__(self, corpus, **vectoriser_kwargs):
        super().__init__(corpus, count, **vectoriser_kwargs)

               
class TfidfVectorizer(VectorFactory):
    """
    Wrapper for scikit-learn's equally-named [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).
    
    """    
    def __init__(self, corpus, **vectoriser_kwargs):
        super().__init__(corpus, tfidf, **vectoriser_kwargs)


        
class TopicFactory(Factory):
    depends_on = VectorFactory
    def __init__(self, corpus, n_topics):
        if not hasattr(self, "word_distribution"):
            raise AttributeError("TopicFactory needs a word distribution to be well-defined!")    
        if not hasattr(self, "predict") or not callable(self.predict):
            raise AttributeError("TopicFactory needs a prediction function to be well-defined!")            

        self.fitted_corpus = corpus
        self.word_distribution = self.word_distribution/self.word_distribution.sum(axis=1)[:, np.newaxis]
        self.topics = [Topic(i, dist, corpus.vectorised_vocabulary)
                            for i, dist in enumerate(self.word_distribution)]
    
    
    def get_topic(self, topic_dist):
        max_prob_ind = topic_dist.argmax()
        return TopicInstance(self.topics[max_prob_ind], topic_dist[max_prob_ind])
    
    
    def process_conversation(self, conversation):
        conversation.topic = self.get_topic(next(self.conv_iter))    
        for email in conversation:
            email_topic = self.process_email(email)
        return conversation.topic

    def process_email(self, email):
        email.topic = self.get_topic(next(self.email_iter))
        return email.topic
            
    
    
    
    def __call__(self, corpus=None, **kwargs):
        if not corpus:
            corpus = self.fitted_corpus
        
        self.conv_iter = iter(self.predict(corpus.conversations_vectorised))
        self.email_iter = iter(self.predict(corpus.vectorised))
        
        return super().__call__(corpus, **kwargs)
        
        
#        email_ind = 0 
#        for i, conv in tqdm(enumerate(corpus), 
#                         desc=f"{self.__class__.__name__} iterating conversations",
#                         total=len(corpus)):
#            convo_topic_ind = convo_topic_dists[i].argmax()
#            conv.topic = TopicInstance(self.topics[convo_topic_ind], 
#                                       convo_topic_dists[i][convo_topic_ind])
#            
#            for email in conv:
#                email_topic_ind = email_topic_dists[email_ind].argmax()
#                email.topic = TopicInstance(self.topics[email_topic_ind], 
#                                            email_topic_dists[email_ind][email_topic_ind])
#                email_ind += 1


class SKLearnLDA(TopicFactory):
    def __init__(self, corpus, n_topics, **kwargs):
        self.model_args = dict(n_components=n_topics, max_iter=20, learning_method='batch',
                               random_state=0, verbose=1, n_jobs=-1)
        self.model_args.update(learning_offset=self.model_args["max_iter"]//100*10)
        self.model_args.update(dict(evaluate_every=self.model_args["max_iter"]//10))
        self.model_args.update(kwargs)
        model = LatentDirichletAllocation(**self.model_args)
        model.fit(corpus.vectorised)

        self.word_distribution = model.components_
        self.predict = model.transform
        
        super().__init__(corpus, n_topics)
        
        
    def determine_n_components(self, ns_to_search, corpus=None):
        if not corpus:
            corpus = self.corpus_fitted
        models = {}
        for n in ns_to_search:
            cur_args = {**self.model_args, **dict(n_components=n)}
            cur_model = LatentDirichletAllocation(**cur_args).fit(corpus.vectorised)
            models[n] = cur_model
            
        print("Perplexities:", [(n, models[n].bound_) for n in ns_to_search])
        return models
    
    
class GensimLDA(TopicFactory):
    def __init__(self, email_corpus, n_topics, **kwargs):
        raise NotImplementedError("LDA with Gensim not implemented yet, please feel free to add!\n"
                                  "Make sure to add attrs word_distribution and predict(), "
                                  "as required by the parent TopicFactory.")


        

class NamedEntityFactory(Factory):
    def __init__(self, corpus, preprocessors=[], postprocessors=[]):
        self.product_type = Entity
        self.product_name = "entities"
        
        self.pre = self.combine_processors(*preprocessors)
        self.post = self.combine_processors(self.string_to_class, *postprocessors)
        
#        super().__init__(self, corpus, preprocessors, postprocessors)
    
    
    @staticmethod
    def string_to_class(entity_list):
        label_class_map = {"PERSON": lambda name: Person(name, ""),
                           "ORG": lambda name: Organisation(name, "")}
        
        return [(label_class_map[l](e)) if l in label_class_map else NamedEntityFactory.entity_from_NER_label(e, l)
                for e, l in entity_list]
        
    @staticmethod 
    def entity_from_NER_label(entity_string, label):
        cls = type(label.title(), (StringEntity, ), dict(class_dynamically_created=True))
        return cls(entity_string)


    def process_conversation(self, conversation):
        conversation.entities = []
        for email in conversation:
            email_entities = self.process_email(email)
            conversation.entities.append(email_entities)
        return conversation.entities
    
    def process_email(self, email):
        email.entities = list(filter(None, self.post(self.get_entities_with_labels(self.pre(email.body.normalised)))))
        return email.entities
    
#    def __call__(self, corpus):
#        for conv in tqdm(corpus, 
#                         desc=f"{self.__class__.__name__} iterating conversations"):
#            all_entities = []
#            for email in conv:
#                email.entities = list(filter(None, 
#                                             self.post(self.get_entities_with_labels(self.pre(email.body.normalised)))
#                                             ))
#                all_entities.extend(email.entities)
#            conv.entities = all_entities
    
    
class SpaCyNER(NamedEntityFactory):
    def __init__(self, preprocessors=[], postprocessors=[]):
        self.nlp = spacy.load("en_core_web_md")
        super().__init__(preprocessors, postprocessors)
        
    def get_entities(self, text):
        return [str(e) for e in self.nlp(text).ents]
    
    def get_entities_with_labels(self, text):
        return [(str(e), e.label_) for e in self.nlp(text).ents] 
        
    
class StanzaNER(NamedEntityFactory):
    def __init__(self, preprocessors=[], postprocessors=[]):
        self.nlp = stanza.Pipeline('en', processors="tokenize, mwt, ner")
        super().__init__(preprocessors, postprocessors)
        
    def get_entities(self, text):
        return [d.text for d in self.nlp(text).ents]
    
    def get_entities_with_labels(self, text):
        return [(d.text, d.type) for d in self.nlp(text).ents]            



class KeyWordFactory(Factory):
    def __init__(self, preprocessors=[], postprocessors=[]):
        self.product_type = KeyWord
        self.product_name = "keywords"
        
        self.pre = self.combine_processors(*preprocessors)
        self.post = self.combine_processors(self.output_to_class, *postprocessors)
        
#        # set to False if process_conversation calls process_email, to True otherwise
#        self.process_emails_separately = False
        
#        super().__init__(self, corpus=None, preprocessors, postprocessors)


    def process_conversation(self, conversation):
        conversation.keywords = []
        for email in conversation:
            email_keywords = self.process_email(email)
            conversation.keywords.append(email_keywords)
        return conversation.keywords

    def process_email(self, email):
        email.keywords = list(filter(None, self.post(self.get_keywords(self.pre(email.body.normalised)))))
        return email.keywords


#    def __call__(self, corpus):
#        for conv in tqdm(corpus, 
#                         desc=f"{self.__class__.__name__} iterating conversations"):
#            all_keywords = []
#            for email in conv:
#                email.keywords = list(filter(None,
#                                             self.post(self.get_keywords(self.pre(email.body.normalised)))
#                                    ))
#                all_keywords.extend(email.keywords)
#            conv.keywords = all_keywords
    
    
    @staticmethod
    def output_to_class(keyword_list):
        return [KeyWord(s) for s in keyword_list]
    
    
    
class RakeKeyWordExtractor(KeyWordFactory):
    def __init__(self, preprocessors=[], postprocessors=[]):
        self.rake = Rake()
        postprocessors = [self.remove_low_scores, *postprocessors]  # self.combine_processors(self.remove_low_scores, *postprocessors)
        super().__init__(preprocessors, postprocessors)
    
    @staticmethod    
    def remove_low_scores(keyword_list, score=1.0):
        return [phrase for score, phrase in keyword_list if score > 1.0]
    
    
    
    def get_keywords(self, text):
        self.rake.extract_keywords_from_text(text)
        return self.rake.get_ranked_phrases_with_scores()
