from .corpus import EmailCorpus, Conversation, group_by_subject_line, group_by_id
from .emails import Email
from .entities import EntityUniverse, Entity, Person, Organisation, Address, Link, KeyWord, Topic
#from .topics import TopicModel
from .ledger import Universe



hierarchy = [
        Universe,
        EmailCorpus, Conversation, 
        Email, 
        EntityUniverse, Entity, Person, Organisation, Address, Link, KeyWord, Topic
#        TopicModel, Topic
        ]
