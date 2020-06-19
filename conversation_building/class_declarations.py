# -*- coding: utf-8 -*-

from email.utils import parseaddr
from dateutil.parser import parse as du_parse
from urllib.parse import urlparse
import datetime


import re


#import stanza
#stanza.download('en')
#nlp = stanza.Pipeline('en', processors="tokenize,ner")


import spacy
nlp = spacy.load("en")


def process_time_sent(s):
    dt = du_parse(s)
    
    if not dt.tzinfo:
            raise ValueError("No timezone information in parse!", s)
            dt = dt.replace(tzinfo=datetime.timezone.utc)
    if dt.tzinfo.utcoffset(dt) > datetime.timedelta(hours=24) or\
            dt.tzinfo.utcoffset(dt) < -datetime.timedelta(hours=24):
        print("Timezone outside of 24 hours: ", dt.tzinfo.utcoffset(dt))
        raise ValueError("Timezone outside of 24 hours: ", dt.tzinfo.utcoffset(dt))
        
    if dt is None:
        raise ValueError(s)
        
    return dt

sender_re = re.compile(r"[^@]+@[^@]+\.[^@]+")
author_re = re.compile(r"(.+)(\([^@]+@[^@]+\.[^@]+\))")

url_re = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
address_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')


#def parseaddr(addr_str):
#    *name, mail = addr_str.split("|||")
#    print(mail)
#    if name:
#        return name[-1], mail
#    else:
#        return "", mail



def merge_reported_subjects(subject, subject_from_meta):
    same = subject == subject_from_meta
    
    if same:
        return subject
    
    return subject

def merge_reported_authors(author, from_, name, email):
#    if sender_re.match(from_):
#        from_name, from_email = parseaddr(from_)
#        if not from_name: pass
#        else: pass
#    else: pass
    return name + "<" + email + ">"
    
def merge_reported_ids(id_, id_from_body):
    if not id_from_body:
        pass
    
    return id_
    
def merge_reported_time(date, date_from_body, isosent):
    try:
        return process_time_sent(date_from_body)
    except ValueError as e:
        return datetime.datetime(1,1,1).replace(tzinfo=datetime.timezone.utc)

class Org:
    @classmethod
    def from_address(cls, email_addr):
        if not email_addr: return None
        extracted_org = email_addr[email_addr.rfind("@")+1:]
        return extracted_org if extracted_org else None
    
    def __init__(self, domain_name):
        self.domain_name = domain_name
        
    def __hash__(self):
        return hash(self.domain_name)
    
    def __eq__(self, other):
        if not isinstance(other, Org):
            return False
        return hash(self) == hash(other)


class Link:
    def __init__(self, url):
        self.url = url
        try:
            parsed = urlparse(url)
            self.domain = parsed.netloc
            self.path = parsed.path
        except ValueError:
            self.domain = None
            self.path = None
        
    def __str__(self):
        return str(self.url)
    
    def __repr__(self):
        return str(self)
        
    def __hash__(self):
        return hash(str(self))


class Person:
    def __init__(self, person_string):
        self.name, self.address = parseaddr(person_string)
        self.org = Org.from_address(self.address)

        if self.name == self.address.lower():
            self.name = ""
    
        self.name = self.name.strip("'")
    
    def __repr__(self):
        return f"<{self.name if self.name else 'NO_NAME'} ({self.address})>"
    
    def __str__(self):
        return repr(self)
        
    def __hash__(self):
        return hash(repr(self))
    
    def __eq__(self, other):    
        if not isinstance(other, Person):
            return False
        return repr(self) == repr(other)


class Email_Body(str):
    def __new__(cls, email_body):
        self = str.__new__(cls, email_body)
        self.normalised = self.normalise()
        self.links = self.extract_links()
        self.addresses = self.extract_addresses()
        self.entities = self.extract_named_entities()
        
        
        return self
  
#    def __init__(self, email_body):
#        super().__init__(email_body)
#        self.normalised = self.normalise()
    
    def normalise(self):
        normalised_self = self.strip('"').strip("'").lower()
        return normalised_self
        
    def extract_links(self):
        return [Link(l) for l in url_re.findall(self.normalised)]
    
    def extract_addresses(self):
        return [addr for addr in address_pattern.findall(self.normalised)]
    
    def extract_named_entities(self):
        return nlp(self.normalised).ents
    
    
class Email:
    def __init__(self, mail_dict):
#        super().__init__(self)
        
        self.body = Email_Body(mail_dict["body"])
        self.sender = Person(merge_reported_authors(mail_dict["author"],
                                             mail_dict["from"],
                                             mail_dict["name"],
                                             mail_dict["email"]))
        
        self.receiver = Person(mail_dict["to"])
        
        self.time = merge_reported_time(mail_dict["date"],
                                        mail_dict["date_from_body"],
                                        mail_dict["isosent"])
        
        self.id = merge_reported_ids(mail_dict["id"],
                                     mail_dict["id_from_body"])
    
    def repr(self):
        return f"Email from {self.sender.address} to {self.receiver.address}"
    
    def __eq__(self):
        pass
        
    def __hash__(self):
        return hash((self.body, self.sender, self.receiver, self.id))
    
               
class Conversation:
    def __init__(self, subject, email_dicts):
        self.subject = subject
        self.emails = tuple(sorted((Email(m) for m in email_dicts), key=lambda e: e.time))

        self.start_time = self.emails[0].time
        self.end_time = self.emails[-1].time

        
        self.interlocutors = set(p for m in self.emails for p in (m.sender, m.receiver))
        self.involved_orgs = set(p.org for p in self.interlocutors)
        self.observers = None
        
        self.mentioned_links = set(l for m in self.emails for l in m.body.links)
        self.mentioned_addresses = set(a for m in self.emails for a in m.body.addresses)
        
    def __len__(self):
        return len(self.emails)
    
    
    def __iter__(self):
        return iter(self.emails)

    def __getitem__(self, i):
        return self.emails[i]
    
    # for sorting
    def __lt_(self, other):
        if not isinstance(other, Conversation):
            raise TypeError(f"Comparison impossible with {type(other)}!")
        
        if self.start_time < other.start_time:
            return True
        return False
    
    def __repr__(self):
        return f"{self.subject} ({len(self.emails)} emails; {self.start_time.date()} -- {self.end_time.date()})"
    
    
    # WARNING: not a persistent identifier across processes
    def __hash__(self):
        return hash((self.subject, self.emails))
    
#%%