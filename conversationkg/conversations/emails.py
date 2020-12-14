import warnings
import json
import re

import datetime
from dateutil.parser import parse as du_parse

from email_reply_parser import EmailReplyParser
from email.utils import parseaddr

import spacy
nlp = spacy.load("en_core_web_md")

from rake_nltk import Rake
rake = Rake()

from .entities import Person, Link, Address, KeyWord, TopicInstance
#from .topics import TopicInstance
from .ledger import Universe

url_re = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
address_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')


# MERGING
def merge_reported_authors(author, from_, name, email):
    return name, email

def merge_reported_times(date, date_from_body, isosent):
    return date_from_body

def merge_reported_ids(id_, id_from_body):
    return id_


# PARSING
def parse_name_address(person_str):
    return parseaddr(person_str)

def parse_time_sent(s):
    try:
        dt = du_parse(s)
    except ValueError:
#        print("ValueError:", s)
        return datetime.datetime(1,1,1).replace(tzinfo=datetime.timezone.utc)
    
    if not dt.tzinfo:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
    if dt.tzinfo.utcoffset(dt) > datetime.timedelta(hours=24) or\
            dt.tzinfo.utcoffset(dt) < -datetime.timedelta(hours=24):
        raise ValueError("Timezone outside of 24 hours: ", dt.tzinfo.utcoffset(dt))
    
    if dt is None: raise ValueError(s)
    return dt


class Email(metaclass=Universe):
    @classmethod
    def from_email_dict(cls, mail_dict, **unused_kwargs):
        return cls(EmailBody(mail_dict["body"]),
                   Person(*merge_reported_authors(mail_dict["author"],
                                             mail_dict["from"],
                                             mail_dict["name"],
                                             mail_dict["email"])),
                    Person(*parse_name_address(mail_dict["to"])),
                    parse_time_sent(merge_reported_times(mail_dict["date"],
                                        mail_dict["date_from_body"],
                                        mail_dict["isosent"])),
                    merge_reported_ids(mail_dict["id"],
                                     mail_dict["id_from_body"]),
                    mail_dict["inreplyto"],
                    mail_dict["subject"],
                    [], # attachments
                    []) # observers, i.e. persons in CC               
                    
        
    def __init__(self, body, sender, receiver, time, 
                 message_id, inreplyto_id, 
                 subject, observers, attachments, **unused_kwargs):
        
        self.message_id = message_id
        self.inreplyto_id = inreplyto_id
        
        self.body = body
        self.sender = sender
        self.receiver = receiver
        
        self.time = time
        self.subject = subject
        self.observers = observers
        
        self.attachments = attachments
        
        self.organisations = (self.sender.organisation,
                              self.receiver.organisation)
        
        self.first_observed_at = self.time
        
#        self.topic = None
        
#        Universe.observe(body, self, "evidenced_by")
#        Universe.observe(sender, self, "evidenced_by")
#        Universe.observe(receiver, self, "evidenced_by")
        
        
    # for sorting
    def __lt__(self, other):
        if not isinstance(other, Email):
            raise TypeError(f"<Email> cannot be compared to {type(other)}!")
        
        if self.time < other.time:
            return True
        return False
    
    def __eq__(self, other):
        if not (type(self) == type(other) == Email):
            return False
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash((self.time, self.subject))    
    
    def __repr__(self):
        return f"Email from <{str(self.sender.address)}> to <{str(self.receiver.address)}>"
        
#        return f"Email({str(self.sender)}, {str(self.receiver)}, {self.time.date()})"
    
    def __str__(self):
        return repr(self)
        
    
    def to_json(self, dumps=False):
        d = {k:v for k, v in self.__dict__.items()}
        d["class"] = self.__class__.__name__
        d["time"] = str(self.time)
        d["body"] = self.body.to_json(dumps=False)
        d["sender"] = self.sender.to_json(dumps=False)
        d["receiver"] = self.receiver.to_json(dumps=False)
        del d["organisations"]
        d["observers"] = [e.to_json(dumps=False) for e in self.observers]
        
        if self.topic:
            d["topic"] = self.topic.to_json(dumps=False)
        
        if dumps: return json.dumps(d)
        return d
    
    
    @classmethod
    def from_json(cls, json_dict):
        body = EmailBody.from_json(json_dict["body"])
        sender = Person.from_json(json_dict["sender"])
        receiver = Person.from_json(json_dict["receiver"])
        time = parse_time_sent(json_dict["time"])
        message_id = json_dict["message_id"]
        inreplyto_id = json_dict["inreplyto_id"]
        subject = json_dict["subject"]
        observers = [Person.from_json(p_dict) for p_dict in json_dict["observers"]]
        
        email = cls(body, sender, receiver, time, message_id, inreplyto_id, subject, observers)
        
        if "topic" in json_dict:
            email.topic = TopicInstance.from_json(json_dict["topic"])
        
        return email
        

        
class EmailBody(str, metaclass=Universe):
    def __new__(cls, body_str, 
                 links=None, addresses=None, entities=None, **kwargs):        
        self = super().__new__(cls, body_str)
        return self
        
    
    def __init__(self, body_str, **kwargs):
        self.body, self.signature, self.quoted = EmailBody.discern_quoted(body_str)
        self.normalised = self.normalise()
                
#        self.links = links if links else tuple(self.extract_links())
#        self.addresses = addresses if addresses else tuple(self.extract_addresses())
        self.code_snippets = []
        
        
#        self.entities = None
#        self.keywords = None
#        self.topic = None
        
        
#        if entities:
#            self.entities = entities
#        else:
#            self.entities = self.discover_entities()
        
#        for entity in self.entities:
#            Universe.observe(entity, self, "mentioned_in")
            
    
    def normalise(self):
        normalised_self = self.strip('"').strip("'").lower()
        return normalised_self
    
    def to_json(self, dumps=False):
        d = {"class": self.__class__.__name__,
             "self": str(self)} 
#             "links": [l.to_json(dumps=False) for l in self.links],
#             "addresses":[a for a in self.addresses],
#             "entities":[(e, l) for e, l in self.entities]}  # e.to_json(dumps=False)
        
        if dumps: return json.dumps(d)
        return d
        
    
    @classmethod
    def from_json(cls, json_dict):
        body = json_dict["self"]
        links = [Link.from_json(l) for l in json_dict["links"]]
        addresses = [Address(a) for a in json_dict["addresses"]]
        entities = [(e_str, l) for e_str, l in json_dict["entities"]] 
        
        return cls(body, links, addresses, entities)
    
    
    @staticmethod
    def discern_quoted(body_text):
        parsed_email = EmailReplyParser.read(body_text)
        
        reply = ""
        quoted = ""
        signature = ""
        
        for fragment in parsed_email.fragments:
            if fragment.quoted:
                quoted += fragment.content
            elif fragment.signature:
                signature += fragment.content
            else:
                reply += fragment.content
                
        return (reply, signature, quoted)
    
    
    
#    def extract_links(self):
#        for l in url_re.findall(self.normalised):
#            link = Link(l)
#            Universe.observe(link, self, "mentioned_in")
#            yield link
#    
#    def extract_addresses(self):
#        for addr in address_pattern.findall(self.normalised):
#            address = Address(addr)
#            Universe.observe(address, self, "mentioned_in")
#            yield address
            
#    def discover_entities(self):
#        s = str(self.normalised)
#        if len(s) > nlp.max_length:
#            warnings.warn(f"Email body of {len(self)} characters exceeds spacy's maximum"
#                            "of {nlp.max_length}! Clipping the body to the maximum length and proceeding.")
#            
#            s = s[:nlp.max_length]
#        ents = nlp(s).ents
#        ents = [(str(e).strip(), e.label_) for e in ents]
#        return ents
#    
#    def discover_keywords(self):
#        rake.extract_keywords_from_text(self.normalised)
#        kws = rake.get_ranked_phrases_with_scores()
#        return [KeyWord(phrase) for score, phrase in kws if score > 1.0]
        
        
