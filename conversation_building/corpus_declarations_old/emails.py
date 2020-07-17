from email.utils import parseaddr
import datetime
from dateutil.parser import parse as du_parse
import re
import json

from email_reply_parser import EmailReplyParser

from corpus_declarations.entities import EntityInstance, Person, Link
from corpus_declarations.topics import TopicInstance

url_re = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
address_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')



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


class Email:
    @classmethod
    def from_mail_dict(cls, mail_dict):
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
                    []) # observers               
                    
        
    def __init__(self, body, sender, receiver, time, email_id, subject, observers):
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
        
        
    # for sorting
    def __lt__(self, other):
        if not isinstance(other, Email):
            raise TypeError(f"<Email> cannot be compared to {type(other)}!")
        
        if self.time < other.time:
            return True
        return False
    
    
    def __hash__(self):
        return hash((self.time, self.subject, self.body))    
    
    def __repr__(self):
        return f"Email({str(self.sender)}, {str(self.receiver)}, {self.time.date()})"
    
    def __str__(self):
        return repr(self)
        
    
    def to_json(self, dumps=False):
        d = {k:v for k, v in self.__dict__.items()}
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
        

        
class EmailBody(str):
    def __new__(cls, body_str, 
                 links=None, addresses=None, entities=None):
        body, signature, quoted = EmailBody.discern_quoted(body_str)
        self = super().__new__(cls, body)
        self.signature = signature
        self.quoted = quoted
        
        self.whole = body_str
        return self
        
    
    def __init__(self, body_str, 
                 links=None, addresses=None, entities=None):
        self.normalised = self.normalise()
                
        self.links = links if links else self.extract_links()
        self.addresses = addresses if addresses else self.extract_addresses()
        self.code_snippets = []
        
        self.entities = entities if entities else []
    
    
    def normalise(self):
        normalised_self = self.strip('"').strip("'").lower()
        return normalised_self
    
    def extract_links(self):
        return [Link(l) for l in url_re.findall(self.normalised)]
    
    def extract_addresses(self):
        return [addr for addr in address_pattern.findall(self.normalised)]
    
    def to_json(self, dumps=False):
        d = dict(self=self.whole, 
                 links=[l.to_json(dumps=False) for l in self.links],
                 addresses=[a for a in self.addresses],
                 entities=[e.to_json(dumps=False) for e in self.entities])
        
        if dumps: return json.dumps(d)
        return d
        
    @classmethod
    def from_json(cls, json_dict):
        body = json_dict["self"]
        links = [Link.from_json(l) for l in json_dict["links"]]
        addresses = json_dict["addresses"]
        entities = [EntityInstance.from_json(e_dict) for e_dict in json_dict["entities"]]
        
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