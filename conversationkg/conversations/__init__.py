from .corpus import EmailCorpus, Conversation
from .emails import Email
from .entities import EntityUniverse, Person, Organisation, Address, Link
from .topics import TopicModel, Topic
from .ledger import Universe



members = [
        Universe,
        EmailCorpus, Conversation, 
        Email, 
        EntityUniverse, Person, Organisation, Address, Link,
        TopicModel, Topic
        ]







