import warnings
from tqdm import tqdm
import json
from joblib import Parallel, delayed

from itertools import groupby
from collections import defaultdict

import numpy as np
import scipy

from .emails import Email
from .entities import TopicInstance
from .ledger import Universe


def group_by_subject_line(emails, strip={"Re: "}, **kwargs):
    def edit_subject(subj):
        s = subj
        for prefix in strip:
            s= s.lstrip(prefix)
        return s
    key = lambda e: edit_subject(e.subject)
    for subj, email_iter in groupby(sorted(emails, key=key), key):
        yield subj, list(email_iter)

def group_by_id(emails, **kwargs):
    # collect all emails' successor emails
    # NOTE: (1) an email which is not a successor is the successor of None
    # (2) implicitly, some emails will not exist as keys in the mapping, these are
    #  those emails which have not successors
    emails_by_id = {e.message_id:e for e in emails}
    successors = defaultdict(list)
    for e in emails:
        if e.inreplyto_id:
            if e.inreplyto_id in emails_by_id:
                predecessor_e = emails_by_id[e.inreplyto_id]
                successors[predecessor_e].append(e)
            else:
                successors[None].append(e)
        else:
            successors[None].append(e)
    
    
    def get_subject_line(ls_of_emails):
    #    subjs = [e.subject for e in ls_of_emails]
        initial_subj = ls_of_emails[0].subject  # majority_vote = max(set(subjs), key=subjs.count)
        return initial_subj
        
    def collect_recursive(e, conv_so_far):
        # email has no reply, so conversation over, yield finished conversation
        if not e in successors:
            complete_conv = conv_so_far + [e]
            subj = get_subject_line(complete_conv)
            yield (subj, complete_conv)
        
        successor_mails = successors[e]
        
        # go through the next emails in the conversation and repeat recursively
        for next_e in successor_mails:
            copy = list(conv_so_far + [e])   
            yield from list(collect_recursive(next_e, copy))
            
    
    for starter in successors[None]:
        convo_tuples = list(collect_recursive(starter, []))
        yield from convo_tuples
        
        
        
class EmailCorpusCollection(list, metaclass=Universe):
    @classmethod
    def from_list_of_ungrouped_email_dicts(cls, list_of_email_dict_list, 
                                           grouping_function=group_by_id,
                                           **grouping_function_args):
        
        corpus_list = [EmailCorpus.from_ungrouped_email_dicts(email_dicts, 
                                                              grouping_function,
                                                              **grouping_function_args)
                        for email_dicts in list_of_email_dict_list]
        return cls(corpus_list)
        
    
    @classmethod
    def from_email_dict_list(cls, list_of_email_dict_list):
        corpus_list = [EmailCorpus.from_email_dicts(email_dicts)
                        for email_dicts in list_of_email_dict_list]
        return cls(corpus_list)
        
    def __new__(cls, list_of_email_corpora=[]):
        self = super().__new__(cls, [])
        return self
    
    def __init__(self, list_of_email_corpora):
        if len(self) < 1:
            self.names = []
            self.n_conversations = self.n_emails = 0
        else:
            self.names = [getattr(c, "name", None) for c in self]
            self.n_conversations = sum(map(len, self))
            self.n_emails = sum(c.n_emails for c in self)

        
    def apply(self, *factories):
        progressbar = tqdm(self, desc="Applying factories to corpus")
        for corpus in progressbar:
            progressbar.set_description(f"Applying factories to corpus {corpus.name}")
            yield list(corpus.apply(*factories))
        
    def iter_conversations(self):
        for corpus in self:
            for conv in corpus:
                yield conv
    
    def iter_emails(self):
        for conv in self.iter_conversations():
            for email in conv:
                yield email              
                
    def merge_corpora(self):
        return EmailCorpus(self.iter_conversations())
                
    def __getitem__(self, key):
        corpus_slice = super().__getitem__(key)
        # user is asking for a single corpus
        if isinstance(key, int):
            return corpus_slice
        return EmailCorpusCollection(corpus_slice)
    
    def append(self, corpus):
        super().append(corpus)
        self.names.append(getattr(corpus, "name", None))
        self.n_conversations += len(corpus)
        self.n_emails += corpus.n_emails
                



class EmailCorpus(tuple, metaclass=Universe):
    @staticmethod
    def parallelise(it, func, n_jobs=-1):
        delayed_f = delayed(func)
        return Parallel(n_jobs)(delayed_f(x) for x in it)
    
    
    @classmethod
    def from_ungrouped_email_dicts(cls, 
                                   email_dicts, 
                                   corpus_name=None,
                                   grouping_function=group_by_id, 
                                   **grouping_function_args):
        
#        emails = tqdm(map(Email.from_email_dict, email_dicts), total=len(email_dicts),
#                      desc="Iterating emails in EmailCorpus.from_ungrouped_email_dicts")
        progressbar = tqdm(email_dicts, 
                           desc="Iterating emails in EmailCorpus.from_ungrouped_email_dicts")
        emails = cls.parallelise(progressbar, Email.from_email_dict)
        
        grouped_emails = grouping_function(emails, **grouping_function_args)
        
        conversations = (Conversation(subj, email_ls) for subj, email_ls in grouped_emails)
        return cls(conversations, corpus_name)
    
    
    @classmethod
    def from_email_dicts(cls, email_dicts, corpus_name=None):
        progressbar = tqdm(email_dicts, 
                           desc="Iterating conversations in EmailCorpus.from_email_dicts")
        f = lambda tup: Conversation.from_email_dicts(*tup)
        conversations = cls.parallelise(progressbar, f)
        return cls(conversations, corpus_name)

    def __new__(cls, conversations, corpus_name=None):
        self = super().__new__(cls, sorted(conversations))
        if len(self) < 1:
            raise ValueError("Empty list of conversations given!")
        return self
        
    def __init__(self, conversations, corpus_name=None):        
        for conv in self:
            Universe.observe(conv, self, "evidenced_by")
        
        if corpus_name:
            self.name = corpus_name
        
        self.n_emails = sum(len(c) for c in self)
        
        self.interlocutors = set(p for c in self for p in c.interlocutors)
        self.organisations = set(o for c in self for o in c.organisations)
        
        if len(self) > 1:
            self.start_time = next(c.start_time for c in self if c.start_time.year > 1)
            self.end_time = max(c.end_time for c in self)
        else:
            self.start_time, self.end_time = self[0].start_time, self[0].end_time
        
    
    def __getitem__(self, key):
        conv_slice = super().__getitem__(key)
        # user is asking for a single conversation
        if isinstance(key, int):
            return conv_slice
        # else: key is a slice(), i.e. user is asking for a subcorpus
        
        subcorpus = EmailCorpus(conv_slice)
        
        
        email_inds = list(range(sum(len(c) for c in conv_slice)))
        
        
        if hasattr(self, "vectorised"):
            subcorpus.vectorised = self.vectorised[email_inds, ]
            subcorpus.conversations_vectorised = self.conversations_vectorised[key, ]
            subcorpus.vectorised_vocabulary = self.vectorised_vocabulary
        return subcorpus
    
    
    def iter_emails(self):
        for conversation in self:
            for email in conversation:
                yield email    
    
    
    def apply(self, *factories):
        for f in factories: yield f(self)
    
    
    def save(self, filename):
#        if self.vectorised.size*self.vectorised.dtype.itemsize > 100e6:
#            print("WARNING: The matrix holding the vectorised emails "
#                  "may be larger than 100mb!"
#                  "Saving separately in scipy-native .npz format!")
#            scipy.sparse.save_npz("corpus_vectorised.npz", self.vectorised)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(self.to_json(), handle)
    
    @classmethod
    def load(cls, filename):
        with open(filename, encoding="utf-8") as handle:
            return cls.from_json(json.load(handle))

    def to_json(self, dumps=False):
#        if self.vectorised is None:
#            vectorised_to_save = None
#            vectoriser_params = None
#        else:
#            if self.vectorised.size*self.vectorised.dtype.itemsize > 100e6:
#                warnings.warn("WARNING: The matrix holding the vectorised emails "
#                      "may be larger than 100mb! Omitting from JSON representation!")
#                vectorised_to_save = "corpus_vectorised.npz"
#            else:
#                vectorised_to_save = self.vectorised.toarray().tolist()
#            vectoriser_params = self.vectoriser.get_params()
#            del vectoriser_params["dtype"]
        
        d = {"class": self.__class__.__name__,
            "self": [conv.to_json(dumps=False) for conv in self]}#,
#            "vectorised": vectorised_to_save,
#            "vectoriser_params": vectoriser_params}        
        
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        conversations = [Conversation.from_json(conv_dict) for conv_dict in json_dict["self"]]
        
        
#        vectorised_value = json_dict["vectorised"]
#        if vectorised_value:
#            if isinstance(vectorised_value, str):
#                vectorised = scipy.sparse.load_npz(vectorised_value)
#            else:
#                vectorised = scipy.sparse.csr_matrix(vectorised_value)
#        else:
#            vectorised = None
#            
#        vectoriser_params = json_dict["vectoriser_params"]
        corpus = cls.from_conversations(conversations, vectorise_default=False)
#        corpus.vectorised = vectorised
#        corpus.vectoriser = \
#            CountVectorizer(**vectoriser_params) if vectoriser_params else None
        return corpus        
        
    
    
class Conversation(tuple, metaclass=Universe):
    @classmethod
    def from_email_dicts(cls, subject, email_dicts):
        return cls(subject, (Email.from_email_dict(mail_dict) for mail_dict in email_dicts))
    
    def __new__(cls, subject, emails):
        self = super().__new__(cls, sorted(emails))
        for email in self:
            Universe.observe(email, self, "evidenced_by")
        return self
        
    # necessary to implement when overriding __new__ and using pickle (such as for multiprocessing)
    def __getnewargs__(self):
        return self.subject, [e for e in self]

            
    def __init__(self, subject, emails):
        self.subject = subject
        self.start_time = self[0].time
        self.end_time = self[-1].time
        
        self.interlocutors = set(p for m in self for p in (m.sender, m.receiver))
        self.organisations = set(o for m in self for o in m.organisations) 
        self.observers = set(p for m in self for p in m.observers) # people in CC
        
        self.attachments = set(a for m in self for a in m.attachments)
        self.documents = set(d for m in self 
                            for doc_ls in (m.body.links, m.body.addresses, m.body.code_snippets)
                            for d in doc_ls)

        self.first_observed_at = self.start_time
    
    def __eq__(self, other):
        if not (type(self) == type(other) == Conversation):
            return False
        return hash(self) == hash(other)
    
    # not persistent across Python instances
    def __hash__(self):
        return hash((self.start_time, self.end_time, self.subject))
    
    def __repr__(self):
        return f"Conversation of {len(self)} {'emails' if len(self) > 1 else 'email'} ({self.start_time.date()} - {self.end_time.date()})"
#        return f"{self.subject} ({len(self)} {'emails' if len(self) > 1 else 'email'}; {self.start_time.date()} -- {self.end_time.date()})"
    
    # for sorting
    def __lt__(self, other):
        if not isinstance(other, Conversation):
            raise TypeError(f"<Conversation> cannot be compared to {type(other)}!")
        
        if self.start_time < other.start_time:
            return True
        return False
    
    
    def to_json(self, dumps=False):
        d = {"class": self.__class__.__name__,
            "subject": self.subject,
             "self": [e.to_json(dumps=False) for e in self]}
        if self.topic:
            d["topic"] = self.topic.to_json(dumps=False)
        
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        subject = json_dict["subject"]
        emails = json_dict["self"]
        
        emails = [Email.from_json(e_dict) for e_dict in json_dict["self"]]
        
        conv = cls(subject, emails)
        if "topic" in json_dict:
            conv.topic = TopicInstance.from_json(json_dict["topic"])
            
        return conv
    
    
    def get_email_bodies(self, attr=None, join_str=None):
        get = lambda e: str(e) if (attr is None) else getattr(e, attr)
        bodies = [get(e.body) for e in self]
        
        return bodies if (join_str is None) else join_str.join(bodies)