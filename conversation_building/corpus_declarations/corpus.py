from tqdm import tqdm
import json

from corpus_declarations.emails import Email

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer



class EmailCorpus(tuple, json.JSONEncoder):
    @classmethod
    def from_conversations(cls, conversations):
        self = super().__new__(cls, sorted(conversations))
        self.__init__(None)
        return self
    
    def __new__(cls, raw_conversations):
        return super().__new__(cls, sorted(Conversation(subj, mail_dicts) 
                                       for subj, mail_dicts in tqdm(raw_conversations)))
        
    def __init__(self, raw_conversations, vectorise_default=False):
        self.n_emails = sum(len(c) for c in self)
        
        self.interlocutors = set(p for c in self for p in c.interlocutors)
        self.organisations = set(o for c in self for o in c.organisations)
        
        self.start_time = next(c.start_time for c in self if c.start_time.year > 1)
        self.end_time = max(c.end_time for c in self)
        
        if vectorise_default:
            self.vectorise_emails()
            self.vectorise_conversations()
        
        
    def vectorise_emails(self, **kwargs):
        default_args = dict(max_df=0.5, min_df=0.1, max_features=self.n_emails)
        
        default_args.update(kwargs)
        
        self.vectoriser_emails = CountVectorizer(**default_args)
        
        self.vectorised_emails = self.vectorizer.fit_transform([
                email.body.normalised for conv in self for email in conv
                ])
#        self.vectorized_labels = tf_vectorizer.get_feature_names()

    
    def vectorise_conversations(self, **kwargs):
        default_args = dict(max_df=0.5, min_df=0.1, max_features=self.n_emails)
        
        default_args.update(kwargs)
        
        self.vectoriser_conversations = CountVectorizer(**default_args)
        
        conversations_merged = ["".join(email.body.normalised for email in conv) 
                                            for conv in self]
        
        self.vectorised_conversations = self.vectorizer.fit_transform([
                            conversations_merged
                ])
    
    
    
    def save(self, filename):
        with open(filename, "w") as handle:
            json.dump(self.to_json(), handle)
    
    # for use in a call like json.dumps(email_corpus, cls=EmailCorpus)
    def default(self, obj):
        pass
    
    def to_json(self):
        return json.dumps(self)
    
    @classmethod
    def load(cls, filename):
        with open(filename) as handle:
            conversations_json = json.load(handle)
        
        conversations = [Conversation.load(c_json) for c_json in conversations_json]
        return cls.from_conversations(conversations)
            
        
        

class Conversation(tuple):
    def __new__(cls, subject, email_dicts):
        return super().__new__(cls, sorted((Email(m) for m in email_dicts)))
    
    # necessary to implement when overriding __new__ and using pickle (such as multiprocessing)
    # this is why the raw email_dicts need to be stored in self, even if not needed otherwise
    def __getnewargs__(self):
        return self.subject, self.email_dicts

            
    def __init__(self, subject, email_dicts):
        self.subject, self.email_dicts = subject, email_dicts
        self.start_time = self[0].time
        self.end_time = self[-1].time
        
        self.interlocutors = set(p for m in self for p in (m.sender, m.receiver))
        self.organisations = set(o for m in self for o in m.organisations) 
        
        self.observers = None # will hold people in CC

        self.documents= set(d for m in self 
                            for doc_ls in (m.body.links, m.body.addresses, m.body.code_snippets)
                            for d in doc_ls)

    
    # not persistent across Python instances
    def __hash__(self):
        return hash((self.start_time, self.end_time, self.subject))
    
    def __repr__(self):
        return f"{self.subject} ({len(self)} emails; {self.start_time.date()} -- {self.end_time.date()})"
    
    # for sorting
    def __lt__(self, other):
        if not isinstance(other, Conversation):
            raise TypeError(f"<Conversation> cannot be compared to {type(other)}!")
        
        if self.start_time < other.start_time:
            return True
        return False