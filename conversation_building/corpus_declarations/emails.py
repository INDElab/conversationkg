from email.utils import parseaddr
import datetime
from dateutil.parser import parse as du_parse
import re

url_re = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
address_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')


from corpus_declarations.entities import Person, Link

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
        print("ValueError:", s)
        return datetime.datetime(1,1,1).replace(tzinfo=datetime.timezone.utc)
    
    if not dt.tzinfo:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
    if dt.tzinfo.utcoffset(dt) > datetime.timedelta(hours=24) or\
            dt.tzinfo.utcoffset(dt) < -datetime.timedelta(hours=24):
        raise ValueError("Timezone outside of 24 hours: ", dt.tzinfo.utcoffset(dt))
    
    if dt is None: raise ValueError(s)
    return dt


class Email:
    def __init__(self, mail_dict):
        self.body = EmailBody(mail_dict["body"])
        
        self.sender = Person(*merge_reported_authors(mail_dict["author"],
                                             mail_dict["from"],
                                             mail_dict["name"],
                                             mail_dict["email"]))
        
        self.receiver = Person(*parse_name_address(mail_dict["to"]))
        
        self.time = parse_time_sent(merge_reported_times(mail_dict["date"],
                                        mail_dict["date_from_body"],
                                        mail_dict["isosent"]))
        
        self.id = merge_reported_ids(mail_dict["id"],
                                     mail_dict["id_from_body"])
        
        self.subject = mail_dict["subject"]
        
        self.organisations = (self.sender.organisation, 
                              self.receiver.organisation)
        
        self.observers = None
        
        
    # for sorting
    def __lt__(self, other):
        if not isinstance(other, Email):
            raise TypeError(f"<Email> cannot be compared to {type(other)}!")
        
        if self.time < other.time:
            return True
        return False
    
    
    def __hash__(self):
        return hash((self.time, self.subject))    
    
    def __repr__(self):
        return f"Email({str(self.sender)}, {str(self.receiver)}, {self.time.date()})"
    
    def __str__(self):
        return repr(self)
        
        
class EmailBody(str):
    def __new__(cls, body_str):
        return super().__new__(cls, body_str)
    
    def __init__(self, body_str):
        self.normalised = self.normalise()
        
        self.links = self.extract_links()
        self.addresses = self.extract_addresses()
        self.code_snippets = []
        
        
    def normalise(self):
        normalised_self = self.strip('"').strip("'").lower()
        return normalised_self
    
    def extract_links(self):
        return [Link(l) for l in url_re.findall(self.normalised)]
    
    def extract_addresses(self):
        return [addr for addr in address_pattern.findall(self.normalised)]
    