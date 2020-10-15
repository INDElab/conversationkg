from tqdm import tqdm
import json

import numpy as np
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


from declarations.emails import Email
from declarations.topics import TopicInstance

from declarations.ledger import Universe



class EmailCorpus(tuple, metaclass=Universe):
    # TODO: switch factory from_conversations and __new__ around in terms of function
    @classmethod
    def from_conversations(cls, conversations, vectorise_default=False):
        self = super().__new__(cls, sorted(conversations))
        self.__init__(None, vectorise_default=vectorise_default)
        return self
    
    def __new__(cls, raw_conversations, vectorise_default=False):
        self = super().__new__(cls, sorted(Conversation(subj, mail_dicts) 
                                       for subj, mail_dicts in tqdm(raw_conversations)))
        return self
        
        
    def __init__(self, raw_conversations, vectorise_default=False):
        for conv in self:
            Universe.observe(conv, self, "evidenced_by")
            
        self.n_emails = sum(len(c) for c in self)
        
        self.interlocutors = set(p for c in self for p in c.interlocutors)
        self.organisations = set(o for c in self for o in c.organisations)
        
        self.start_time = next(c.start_time for c in self if c.start_time.year > 1)
        self.end_time = max(c.end_time for c in self)
        
        if vectorise_default:
            self.vectorise()
        else:
            self.vectorised, self.vectoriser = None, None    
    
    def __getitem__(self, key):
        conv_slice = super().__getitem__(key)
        if isinstance(key, int):
            return conv_slice
        
        subcorpus = EmailCorpus.from_conversations(
                    conv_slice, vectorise_default=False
                )
        
        if subcorpus.vectorised:
            subcorpus.vectorised = self.vectorised[key, ]
            subcorpus.vectoriser = self.vectoriser
        return subcorpus
    
    
    def iter_emails(self):
        for conversation in self:
            for email in conversation:
                yield email
                
                
    def vectorise(self, vectoriser_algorithm=CountVectorizer, **kwargs):
#        default_args = dict(max_df=0.5, min_df=0.1, max_features=self.n_emails)
        default_args = dict(max_df=0.7, min_df=5)
        
        default_args.update(kwargs)
        
        self.vectoriser = vectoriser_algorithm(**default_args)
        
        self.vectorised = self.vectoriser.fit_transform([
                email.body.normalised for email in self.iter_emails()
                ])
    
        for email, vec in zip(self.iter_emails(), self.vectorised):
            email.body.vectorised = vec
    
        
    def save(self, filename):
        if self.vectorised.size*self.vectorised.dtype.itemsize > 100e6:
            print("WARNING: The matrix holding the vectroised emails "
                  "may be larger than 100mb!"
                  "Saving separately in scipy-native .npz format!")
            scipy.sparse.save_npz("corpus_vectorised.npz", self.vectorised)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(self.to_json(), handle)
    
    @classmethod
    def load(cls, filename):
        with open(filename, encoding="utf-8") as handle:
            return cls.from_json(json.load(handle))

    def to_json(self, dumps=False):
        if self.vectorised is None:
            vectorised_to_save = None
            vectoriser_params = None
        else:
            if self.vectorised.size*self.vectorised.dtype.itemsize > 100e6:
                print("WARNING: The matrix holding the vectroised emails "
                      "may be larger than 100mb! Omitting from JSON representation!")
                vectorised_to_save = "corpus_vectorised.npz"
            else:
                vectorised_to_save = self.vectorised.toarray().tolist()
            vectoriser_params = self.vectoriser.get_params()
            del vectoriser_params["dtype"]
        
        d = {"self": [conv.to_json(dumps=False) for conv in self],
            "vectorised": vectorised_to_save,
            "vectoriser_params": vectoriser_params}        
        
        if dumps: return json.dumps(d)
        return d
    
    @classmethod
    def from_json(cls, json_dict):
        conversations = [Conversation.from_json(conv_dict) for conv_dict in json_dict["self"]]
        
        
        vectorised_value = json_dict["vectorised"]
        if vectorised_value:
            if isinstance(vectorised_value, str):
                vectorised = scipy.sparse.load_npz(vectorised_value)
            else:
                vectorised = scipy.sparse.csr_matrix(vectorised_value)
        else:
            vectorised = None
            
        vectoriser_params = json_dict["vectoriser_params"]
        corpus = cls.from_conversations(conversations, vectorise_default=False)
        corpus.vectorised = vectorised
        corpus.vectoriser = \
            CountVectorizer(**vectoriser_params) if vectoriser_params else None
        return corpus        
        
    
    
class Conversation(tuple, metaclass=Universe):
    @classmethod
    def from_email_dicts(cls, subject, email_dicts, **kwargs):
        return cls(subject, (Email.from_email_dict(mail_dict) for mail_dict in email_dicts), **kwargs)
    
    def __new__(cls, subject, emails, **kwargs):
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
        
        self.observers = None # will hold people in CC

        self.documents= set(d for m in self 
                            for doc_ls in (m.body.links, m.body.addresses, m.body.code_snippets)
                            for d in doc_ls)

    
        self.topic = None
    
    def __eq__(self, other):
        if not (type(self) == type(other) == Conversation):
            return False
        return hash(self) == hash(other)
    
    # not persistent across Python instances
    def __hash__(self):
        return hash((self.start_time, self.end_time, self.subject))
    
    def __repr__(self):
        return f"{self.subject} ({len(self)} {'emails' if len(self) > 1 else 'email'}; {self.start_time.date()} -- {self.end_time.date()})"
    
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
