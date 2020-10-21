from email.utils import parseaddr
import datetime
from dateutil.parser import parse as du_parse
import re
import json

from email_reply_parser import EmailReplyParser

from declarations.entities import EntityInstance, Person, Link, Address
from declarations.topics import TopicInstance

from declarations.ledger import Universe

url_re = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
address_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')

import spacy
nlp = spacy.load("en_core_web_md")



# MERGING
def merge_reported_authors(author, from_, name, email):
    return name, email

def merge_reported_times(date, date_from_body, isosent):
    return date_from_body

def merge_reported_ids(id_, id_from_body):
    return id_


#PARSING
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
    def from_email_dict(cls, mail_dict, **kwargs):
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
                    mail_dict["subject"],
                    []) # observers, i.e. persons in CC               
                    
        
    def __init__(self, body, sender, receiver, time, email_id, subject, observers, **kwargs):
        self.body = body
        self.sender = sender
        self.receiver = receiver
        
        self.time = time
        self.email_id = email_id
        self.subject = subject
        self.observers = observers
        
        self.organisations = (self.sender.organisation,
                              self.receiver.organisation)
        
        self.topic = None
        
        Universe.observe(body, self, "evidenced_by")
        Universe.observe(sender, self, "evidenced_by")
        Universe.observe(receiver, self, "evidenced_by")
        
        
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
        return f"Email from <{str(self.sender)}> to <{str(self.receiver)}>"
        
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
        email_id = json_dict["email_id"]
        subject = json_dict["subject"]
        observers = [Person.from_json(p_dict) for p_dict in json_dict["observers"]]
        
        email = cls(body, sender, receiver, time, email_id, subject, observers)
        
        if "topic" in json_dict:
            email.topic = TopicInstance.from_json(json_dict["topic"])
        
        return email
        

        
class EmailBody(str, metaclass=Universe):
    def __new__(cls, body_str, 
                 links=None, addresses=None, entities=None, **kwargs):
        body, signature, quoted = EmailBody.discern_quoted(body_str)
        self = super().__new__(cls, body)
        self.signature = signature
        self.quoted = quoted
        
        self.whole = body_str
        return self
        
    
    def __init__(self, body_str, 
                 links=None, addresses=None, entities=[], **kwargs):
        self.normalised = self.normalise()
                
        self.links = links if links else tuple(self.extract_links())
        self.addresses = addresses if addresses else tuple(self.extract_addresses())
        self.code_snippets = []
        
        
        if entities:
            self.entities = entities
        else:
            self.entities = self.discover_entities()
        
        for entity in self.entities:
            Universe.observe(entity, self, "mentioned_in")
            
    
    def normalise(self):
        normalised_self = self.strip('"').strip("'").lower()
        return normalised_self
    
    def extract_links(self):
        for l in url_re.findall(self.normalised):
            link = Link(l)
            Universe.observe(link, self, "mentioned_in")
            yield link
    
    def extract_addresses(self):
        for addr in address_pattern.findall(self.normalised):
            address = Address(addr)
            Universe.observe(address, self, "mentioned_in")
            yield address
            
    def discover_entities(self):
        ents = nlp(str(self)).ents
        ents = [(str(e).strip(), e.label_) for e in ents]
        return ents
    
    
    def to_json(self, dumps=False):
        d = {"class": self.__class__.__name__,
             "self": self.whole, 
             "links": [l.to_json(dumps=False) for l in self.links],
             "addresses":[a for a in self.addresses],
             "entities":[(e, l) for e, l in self.entities]}  # e.to_json(dumps=False)
        
        if dumps: return json.dumps(d)
        return d
        
    
    @classmethod
    def from_json(cls, json_dict):
        body = json_dict["self"]
        links = [Link.from_json(l) for l in json_dict["links"]]
        addresses = json_dict["addresses"]
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
    
#    def discern_quoted:
#        from Levenshtein import distance as levenshtein
#        
#        i = 3
#        latest = convos[i][-1]
#
#        for l in latest.body.split("\n"):
#            if not l.strip():
#                continue
#            print(":", l)
#            
#            for e_ in convos[1][:-1]:
#                quoted = [l_ for l_ in e_.body.split("\n") if levenshtein(l, l_) < (min(len(l), len(l_))/2)]
#                
#                print(quoted)
#                
#            print("\n---")

    