# -*- coding: utf-8 -*-

import pickle

from urllib.parse import urlparse

from process_emails import extract_meta, parse_header, url_pattern,\
                            email_address_pattern, group_into_convos

class Ledger(dict):
    def __init__(self):
        super().__init__(self)    
    
        self.duplicate_entries = set()
    
    def store(self, entity_or_fact, origin, mode=None):
        if mode:
            key = (entity_or_fact, mode)
        else:
            key = entity_or_fact
        
        if key in self:
            self.duplicate_entries.add(key)
            self[key].append(origin)
        else:
            self[key] = [origin]
    
    def recall(self, entity_or_fact, mode=None):
        if mode:
            key = (entity_or_fact, mode)
        else:
            key = entity_or_fact
        return self[key]
    
    def invert(self):
        inverted_d = {}
        for k, v in self.items():
            for item in v:
                if not item in inverted_d:
                    inverted_d[item] = []
                inverted_d[item].append(k)
        return inverted_d
    
    def pickle(self, filename="ledger.pkl"):
        with open(filename, "wb") as handle:
            pickle.dump(self, handle)
    
    @classmethod
    def from_pickle(cls, filename="ledger.pkl"):
        with open(filename, "rb") as handle:
            loaded = pickle.load(handle)
            return loaded
    

class Person:
    def __init__(self, name, address, ledger):
        self.name = name if name else ""
        self.address =  address if address else ""
        self.org = Org.from_person(self)
        
        ledger.store(self.org, self, mode="evidencedBy")
        
    def __str__(self):
        return self.name + " <" + self.address +  ">"
    
    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return hash(other) == hash(self)
        

class Org:
    @classmethod
    def from_address(cls, email_addr):
        extracted_org = email_addr[email_addr.rfind("@")+1:]
        return extracted_org if extracted_org else None
    
    @classmethod
    def from_person(cls, person):
        if not person.address:
            return None
        return cls.from_address(person.address)

    
    def __init__(self, domain_name, provenance=None):
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
    
    
class Address:
    def __init__(self, addr):
        self.address = addr
        self.org = self.extract_org()

    def extract_org(self):
        if self.address:
            return self.address[self.address.rfind("@")+1:]
        else:
            None

    def __str__(self):
        return str(self.address)
    
    def __repr__(self):
        return str(self.address)

    def __hash__(self):
        return hash(str(self))


class Email:
    def __init__(self, raw_text, ledger):
        header_d, mail_body_raw = extract_meta(raw_text)
        header_d = parse_header(header_d)
        if header_d:
            self.has_header = True
            for k, v in header_d.items():
                setattr(self, k, v)
                
            self.sender = Person(self.name, self.email, ledger)
            self.receiver = Person(*self.to, ledger)
            ledger.store(self.sender, self, mode="EvidencedBy")
            ledger.store(self.receiver, self, mode="EvidencedBy")
            
            if self.cc:
                self.cc = Person(*self.cc, ledger)
                ledger.store(self.cc, self, mode="EvidencedBy")
            
        else: 
            self.has_header = False
        
        self.body_raw = mail_body_raw
        
        self.links = self.extract_links()
        for l in self.links: ledger.store(l, self, mode="MentionedBy")
        
        self.addresses = self.extract_addresses()
        for e in self.addresses: ledger.store(e, self, mode="MentionedBy")
        
    def extract_from_to(self):
        return (Person(self.name, self.email), 
                Person(*self.to))
    
    def extract_links(self):
        return [Link(l) for l in url_pattern.findall(self.body_raw)]
    
    def extract_addresses(self):
        return [Address(e) for e in email_address_pattern.findall(self.body_raw)]
        
    
    def __hash__(self):
        if self.has_header:
            return hash(self.id)
        else:
            return hash(self.body_raw)
        
        
class Conversation:
    @classmethod
    def conversations_from_sorted_emails(cls, emails_in_temp_order, ledger):
        convos = group_into_convos(emails_in_temp_order)
                
        return [cls(mail_ls, ledger) for mail_ls in convos]

    
    def __init__(self, list_of_emails, ledger):
        if len(list_of_emails) > 1:
            first, *_, last = list_of_emails
        else: 
            first = last = list_of_emails[0]
        self.start_time = first.sent
        self.end_time = last.sent
        
        self.emails = tuple(mail.id for mail in list_of_emails)
        ledger.store(self, self.emails, mode="EvidencedBy")        
        

        self.senders = [m.sender for m in list_of_emails]
        self.receivers = [m.receiver for m in list_of_emails]
        
        self.interlocutors = set(self.senders + self.receivers)
        
        self.observers = tuple(mail.cc for mail in list_of_emails)
        
        self.orgs = tuple(person.org for person in self.interlocutors)
        
        self.mentioned_links = tuple(l for mail in list_of_emails for l in mail.links)
        
        self.mentioned_addresses = tuple(e for mail in list_of_emails for e in mail.addresses)
        
        self.topic = "\n".join((m.subject for m in list_of_emails))
        
        
    def __len__(self):
        return len(self.emails)
    

    def __hash__(self):
        prod = 1
        for mail_id in self.emails: 
            prod *= hash(mail_id)
        return prod