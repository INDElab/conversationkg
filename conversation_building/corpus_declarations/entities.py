from urllib.parse import urlparse


class Entity:
    def __init__(self):
        self.qid
        self.tags
        self.aliases
        self.entity_links
    
    
class EntityInContext(Entity):
    def __init__(self, label):
        self.instance_label = label
        self.score = None
        
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return repr(self) == repr(other)
    
    def __str__(self):
        return repr(self)
        
    
    def __hash__(self):
        return hash(repr(self))
        
    
class Person(EntityInContext):
    def __init__(self, name, address):        
        if not address: address = ""        
        self.address = address
        
        self.organisation = Organisation.from_address(address)
        
        if not name: name = ""        
        if name == self.address.lower():
            name = ""
        name = name.strip("'").strip('"')
        
        
        super().__init__(name)
        
    def __repr__(self):
        return f"Person({self.instance_label if self.instance_label else 'NO_NAME'}, {self.address})"
    

class Organisation(EntityInContext):
    @classmethod
    def from_address(cls, addr):
        if not addr: return None
        extracted_domain = addr[addr.rfind("@")+1:]
        if not extracted_domain: return None
        
        name = extracted_domain[:extracted_domain.find(".")]
        
        return cls(name, extracted_domain)
    
    def __init__(self, name, domain):
        self.domain = domain
        super().__init__(name)
        
    def __repr__(self):
        return f"Org({self.instance_label if self.instance_label else 'NO_NAME'}, {self.domain})"
    
class Link(EntityInContext):
    def __init__(self, url):
        try:
            parsed = urlparse(url)
            self.domain = parsed.netloc
            self.path = parsed.path
        except ValueError:
            self.domain = None
            self.path = None
            
        super().__init__(url)
        
        
    def __repr__(self):
        return f"Link({self.instance_label})"