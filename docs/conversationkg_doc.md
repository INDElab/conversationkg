---
description: |
    API documentation for modules: conversationkg.conversations, conversationkg.conversations.corpus, conversationkg.conversations.emails, conversationkg.conversations.entities, conversationkg.conversations.entities2, conversationkg.conversations.entity_factories, conversationkg.conversations.ledger, conversationkg.conversations.topics.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Module `conversationkg.conversations` {#conversationkg.conversations}




    
## Sub-modules

* [conversationkg.conversations.corpus](#conversationkg.conversations.corpus)
* [conversationkg.conversations.emails](#conversationkg.conversations.emails)
* [conversationkg.conversations.entities](#conversationkg.conversations.entities)
* [conversationkg.conversations.entities2](#conversationkg.conversations.entities2)
* [conversationkg.conversations.entity_factories](#conversationkg.conversations.entity_factories)
* [conversationkg.conversations.ledger](#conversationkg.conversations.ledger)
* [conversationkg.conversations.topics](#conversationkg.conversations.topics)






    
# Module `conversationkg.conversations.corpus` {#conversationkg.conversations.corpus}






    
## Functions


    
### Function `group_by_id` {#conversationkg.conversations.corpus.group_by_id}




>     def group_by_id(
>         emails,
>         **kwargs
>     )




    
### Function `group_by_subject_line` {#conversationkg.conversations.corpus.group_by_subject_line}




>     def group_by_subject_line(
>         emails,
>         strip={'Re: '},
>         **kwargs
>     )





    
## Classes


    
### Class `Conversation` {#conversationkg.conversations.corpus.Conversation}




>     class Conversation(
>         subject,
>         emails
>     )


tuple() -> empty tuple
tuple(iterable) -> tuple initialized from iterable's items

If the argument is a tuple, the return value is the same object.


    
#### Ancestors (in MRO)

* [builtins.tuple](#builtins.tuple)





    
#### Static methods


    
##### `Method from_email_dicts` {#conversationkg.conversations.corpus.Conversation.from_email_dicts}




>     def from_email_dicts(
>         subject,
>         email_dicts,
>         **kwargs
>     )




    
##### `Method from_json` {#conversationkg.conversations.corpus.Conversation.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.corpus.Conversation.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `EmailCorpus` {#conversationkg.conversations.corpus.EmailCorpus}




>     class EmailCorpus(
>         conversations,
>         vectorise_default=False
>     )


tuple() -> empty tuple
tuple(iterable) -> tuple initialized from iterable's items

If the argument is a tuple, the return value is the same object.


    
#### Ancestors (in MRO)

* [builtins.tuple](#builtins.tuple)





    
#### Static methods


    
##### `Method from_email_dicts` {#conversationkg.conversations.corpus.EmailCorpus.from_email_dicts}




>     def from_email_dicts(
>         email_dicts,
>         vectorise_default=False
>     )




    
##### `Method from_json` {#conversationkg.conversations.corpus.EmailCorpus.from_json}




>     def from_json(
>         json_dict
>     )




    
##### `Method from_ungrouped_email_dicts` {#conversationkg.conversations.corpus.EmailCorpus.from_ungrouped_email_dicts}




>     def from_ungrouped_email_dicts(
>         email_dicts,
>         grouping_function=<function group_by_id>,
>         vectorise_default=False,
>         **grouping_function_args
>     )




    
##### `Method load` {#conversationkg.conversations.corpus.EmailCorpus.load}




>     def load(
>         filename
>     )





    
#### Methods


    
##### Method `iter_emails` {#conversationkg.conversations.corpus.EmailCorpus.iter_emails}




>     def iter_emails(
>         self
>     )




    
##### Method `save` {#conversationkg.conversations.corpus.EmailCorpus.save}




>     def save(
>         self,
>         filename
>     )




    
##### Method `to_json` {#conversationkg.conversations.corpus.EmailCorpus.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
##### Method `vectorise` {#conversationkg.conversations.corpus.EmailCorpus.vectorise}




>     def vectorise(
>         self,
>         vectoriser_algorithm=sklearn.feature_extraction.text.CountVectorizer,
>         **kwargs
>     )






    
# Module `conversationkg.conversations.emails` {#conversationkg.conversations.emails}






    
## Functions


    
### Function `merge_reported_authors` {#conversationkg.conversations.emails.merge_reported_authors}




>     def merge_reported_authors(
>         author,
>         from_,
>         name,
>         email
>     )




    
### Function `merge_reported_ids` {#conversationkg.conversations.emails.merge_reported_ids}




>     def merge_reported_ids(
>         id_,
>         id_from_body
>     )




    
### Function `merge_reported_times` {#conversationkg.conversations.emails.merge_reported_times}




>     def merge_reported_times(
>         date,
>         date_from_body,
>         isosent
>     )




    
### Function `parse_name_address` {#conversationkg.conversations.emails.parse_name_address}




>     def parse_name_address(
>         person_str
>     )




    
### Function `parse_time_sent` {#conversationkg.conversations.emails.parse_time_sent}




>     def parse_time_sent(
>         s
>     )





    
## Classes


    
### Class `Email` {#conversationkg.conversations.emails.Email}




>     class Email(
>         body,
>         sender,
>         receiver,
>         time,
>         message_id,
>         inreplyto_id,
>         subject,
>         observers,
>         attachments,
>         **unused_kwargs
>     )









    
#### Static methods


    
##### `Method from_email_dict` {#conversationkg.conversations.emails.Email.from_email_dict}




>     def from_email_dict(
>         mail_dict,
>         **unused_kwargs
>     )




    
##### `Method from_json` {#conversationkg.conversations.emails.Email.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.emails.Email.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `EmailBody` {#conversationkg.conversations.emails.EmailBody}




>     class EmailBody(
>         body_str,
>         links=None,
>         addresses=None,
>         entities=[],
>         **kwargs
>     )


str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.


    
#### Ancestors (in MRO)

* [builtins.str](#builtins.str)





    
#### Static methods


    
##### `Method discern_quoted` {#conversationkg.conversations.emails.EmailBody.discern_quoted}




>     def discern_quoted(
>         body_text
>     )




    
##### `Method from_json` {#conversationkg.conversations.emails.EmailBody.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `discover_entities` {#conversationkg.conversations.emails.EmailBody.discover_entities}




>     def discover_entities(
>         self
>     )




    
##### Method `discover_keywords` {#conversationkg.conversations.emails.EmailBody.discover_keywords}




>     def discover_keywords(
>         self
>     )




    
##### Method `extract_addresses` {#conversationkg.conversations.emails.EmailBody.extract_addresses}




>     def extract_addresses(
>         self
>     )




    
##### Method `extract_links` {#conversationkg.conversations.emails.EmailBody.extract_links}




>     def extract_links(
>         self
>     )




    
##### Method `normalise` {#conversationkg.conversations.emails.EmailBody.normalise}




>     def normalise(
>         self
>     )




    
##### Method `to_json` {#conversationkg.conversations.emails.EmailBody.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )






    
# Module `conversationkg.conversations.entities` {#conversationkg.conversations.entities}







    
## Classes


    
### Class `Address` {#conversationkg.conversations.entities.Address}




>     class Address(
>         address,
>         **entity_params
>     )


str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.


    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities.EntityInstance](#conversationkg.conversations.entities.EntityInstance)
* [builtins.str](#builtins.str)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.Address.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.Address.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Base` {#conversationkg.conversations.entities.Base}




>     class Base(
>         x
>     )






    
#### Descendants

* [conversationkg.conversations.entities.Sub](#conversationkg.conversations.entities.Sub)





    
### Class `Entity` {#conversationkg.conversations.entities.Entity}




>     class Entity(
>         qid=None,
>         label=None,
>         description=None,
>         aliases=None,
>         edges=None,
>         types=None
>     )









    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.Entity.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.Entity.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `EntityInstance` {#conversationkg.conversations.entities.EntityInstance}




>     class EntityInstance(
>         entity_params={},
>         instance_label=None,
>         instance_score=None,
>         score=None,
>         page_rank=None,
>         alternative_entities=None,
>         **kwargs
>     )






    
#### Descendants

* [conversationkg.conversations.entities.Address](#conversationkg.conversations.entities.Address)
* [conversationkg.conversations.entities.KeyWord](#conversationkg.conversations.entities.KeyWord)
* [conversationkg.conversations.entities.Link](#conversationkg.conversations.entities.Link)
* [conversationkg.conversations.entities.Organisation](#conversationkg.conversations.entities.Organisation)
* [conversationkg.conversations.entities.Person](#conversationkg.conversations.entities.Person)




    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.EntityInstance.from_json}




>     def from_json(
>         json_dict
>     )




    
##### `Method from_tapioca_api` {#conversationkg.conversations.entities.EntityInstance.from_tapioca_api}




>     def from_tapioca_api(
>         text,
>         result_dict,
>         **kwargs
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.EntityInstance.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `EntityUniverse` {#conversationkg.conversations.entities.EntityUniverse}




>     class EntityUniverse(
>         *args,
>         **kwargs
>     )


type(object_or_name, bases, dict)
type(object) -> the object's type
type(name, bases, dict) -> a new type


    
#### Ancestors (in MRO)

* [builtins.type](#builtins.type)



    
#### Class variables


    
##### Variable `duplicates` {#conversationkg.conversations.entities.EntityUniverse.duplicates}






    
##### Variable `entities` {#conversationkg.conversations.entities.EntityUniverse.entities}






    
##### Variable `n_duplicates` {#conversationkg.conversations.entities.EntityUniverse.n_duplicates}








    
#### Static methods


    
##### `Method reset` {#conversationkg.conversations.entities.EntityUniverse.reset}




>     def reset()





    
### Class `KeyWord` {#conversationkg.conversations.entities.KeyWord}




>     class KeyWord(
>         phrase,
>         **entity_params
>     )


str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.


    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities.EntityInstance](#conversationkg.conversations.entities.EntityInstance)
* [builtins.str](#builtins.str)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.KeyWord.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.KeyWord.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Link` {#conversationkg.conversations.entities.Link}




>     class Link(
>         url,
>         **entity_params
>     )





    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities.EntityInstance](#conversationkg.conversations.entities.EntityInstance)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.Link.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.Link.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Organisation` {#conversationkg.conversations.entities.Organisation}




>     class Organisation(
>         name,
>         domain,
>         **entity_params
>     )





    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities.EntityInstance](#conversationkg.conversations.entities.EntityInstance)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.Organisation.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.Organisation.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Person` {#conversationkg.conversations.entities.Person}




>     class Person(
>         name,
>         address,
>         **entity_params
>     )





    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities.EntityInstance](#conversationkg.conversations.entities.EntityInstance)


    
#### Descendants

* [conversationkg.kgs.KGs.Person](#conversationkg.kgs.KGs.Person)




    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities.Person.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities.Person.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Sub` {#conversationkg.conversations.entities.Sub}




>     class Sub(
>         s
>     )


str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.


    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities.Base](#conversationkg.conversations.entities.Base)
* [builtins.str](#builtins.str)








    
# Module `conversationkg.conversations.entities2` {#conversationkg.conversations.entities2}







    
## Classes


    
### Class `Address` {#conversationkg.conversations.entities2.Address}




>     class Address(
>         address,
>         score=None
>     )


str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.


    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities2.EntityInstance](#conversationkg.conversations.entities2.EntityInstance)
* [builtins.str](#builtins.str)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities2.Address.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities2.Address.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Entity` {#conversationkg.conversations.entities2.Entity}




>     class Entity(
>         name
>     )









    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities2.Entity.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities2.Entity.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `EntityInstance` {#conversationkg.conversations.entities2.EntityInstance}




>     class EntityInstance(
>         label,
>         score,
>         entity=None
>     )






    
#### Descendants

* [conversationkg.conversations.entities2.Address](#conversationkg.conversations.entities2.Address)
* [conversationkg.conversations.entities2.KeyWord](#conversationkg.conversations.entities2.KeyWord)
* [conversationkg.conversations.entities2.Link](#conversationkg.conversations.entities2.Link)
* [conversationkg.conversations.entities2.Organisation](#conversationkg.conversations.entities2.Organisation)
* [conversationkg.conversations.entities2.Person](#conversationkg.conversations.entities2.Person)




    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities2.EntityInstance.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `repr` {#conversationkg.conversations.entities2.EntityInstance.repr}




>     def repr(
>         self
>     )




    
##### Method `to_json` {#conversationkg.conversations.entities2.EntityInstance.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `EntityUniverse` {#conversationkg.conversations.entities2.EntityUniverse}




>     class EntityUniverse(
>         *args,
>         **kwargs
>     )


type(object_or_name, bases, dict)
type(object) -> the object's type
type(name, bases, dict) -> a new type


    
#### Ancestors (in MRO)

* [builtins.type](#builtins.type)



    
#### Class variables


    
##### Variable `duplicates` {#conversationkg.conversations.entities2.EntityUniverse.duplicates}






    
##### Variable `entities` {#conversationkg.conversations.entities2.EntityUniverse.entities}






    
##### Variable `n_duplicates` {#conversationkg.conversations.entities2.EntityUniverse.n_duplicates}








    
#### Static methods


    
##### `Method reset` {#conversationkg.conversations.entities2.EntityUniverse.reset}




>     def reset()





    
### Class `KeyWord` {#conversationkg.conversations.entities2.KeyWord}




>     class KeyWord(
>         phrase
>     )


This entity encapsulates key words or phrases extracted from textual entities 
(subjects of conversations, email bodies, etc.)
common key word extraction algorithms.

Usage
^^^^^

Instantiate as follows:
    
    kw = KeyWord("some keyword")
    kw.to_json()
    

.. _<code>TensorFlow Distributions</code>:
<https://arxiv.org/abs/1711.10604>


    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities2.EntityInstance](#conversationkg.conversations.entities2.EntityInstance)
* [builtins.str](#builtins.str)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities2.KeyWord.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities2.KeyWord.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Link` {#conversationkg.conversations.entities2.Link}




>     class Link(
>         url
>     )


str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.


    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities2.EntityInstance](#conversationkg.conversations.entities2.EntityInstance)
* [builtins.str](#builtins.str)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities2.Link.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities2.Link.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Organisation` {#conversationkg.conversations.entities2.Organisation}




>     class Organisation(
>         name,
>         domain,
>         score=None
>     )





    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities2.EntityInstance](#conversationkg.conversations.entities2.EntityInstance)





    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.entities2.Organisation.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities2.Organisation.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `Person` {#conversationkg.conversations.entities2.Person}




>     class Person(
>         name,
>         address
>     )





    
#### Ancestors (in MRO)

* [conversationkg.conversations.entities2.EntityInstance](#conversationkg.conversations.entities2.EntityInstance)






    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.entities2.Person.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )






    
# Module `conversationkg.conversations.entity_factories` {#conversationkg.conversations.entity_factories}









    
# Module `conversationkg.conversations.ledger` {#conversationkg.conversations.ledger}







    
## Classes


    
### Class `Universe` {#conversationkg.conversations.ledger.Universe}




>     class Universe(
>         *args,
>         **kwargs
>     )


type(object_or_name, bases, dict)
type(object) -> the object's type
type(name, bases, dict) -> a new type


    
#### Ancestors (in MRO)

* [builtins.type](#builtins.type)



    
#### Class variables


    
##### Variable `evidenced_by` {#conversationkg.conversations.ledger.Universe.evidenced_by}






    
##### Variable `mentioned_in` {#conversationkg.conversations.ledger.Universe.mentioned_in}






    
##### Variable `nothing_to_register` {#conversationkg.conversations.ledger.Universe.nothing_to_register}








    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.ledger.Universe.from_json}




>     def from_json(
>         json_dict
>     )




    
##### `Method observe` {#conversationkg.conversations.ledger.Universe.observe}




>     def observe(
>         obj,
>         witness,
>         mode
>     )




    
##### `Method reset` {#conversationkg.conversations.ledger.Universe.reset}




>     def reset()




    
##### `Method to_json` {#conversationkg.conversations.ledger.Universe.to_json}




>     def to_json(
>         dumps=False
>     )





    
### Class `Universe2` {#conversationkg.conversations.ledger.Universe2}




>     class Universe2(
>         *args
>     )


type(object_or_name, bases, dict)
type(object) -> the object's type
type(name, bases, dict) -> a new type


    
#### Ancestors (in MRO)

* [builtins.type](#builtins.type)



    
#### Class variables


    
##### Variable `bases` {#conversationkg.conversations.ledger.Universe2.bases}






    
##### Variable `evidenced_by` {#conversationkg.conversations.ledger.Universe2.evidenced_by}






    
##### Variable `mentioned_in` {#conversationkg.conversations.ledger.Universe2.mentioned_in}






    
##### Variable `name` {#conversationkg.conversations.ledger.Universe2.name}






    
##### Variable `nothing_to_register` {#conversationkg.conversations.ledger.Universe2.nothing_to_register}








    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.ledger.Universe2.from_json}




>     def from_json(
>         json_dict
>     )




    
##### `Method observe` {#conversationkg.conversations.ledger.Universe2.observe}




>     def observe(
>         obj,
>         witness,
>         mode
>     )




    
##### `Method reset` {#conversationkg.conversations.ledger.Universe2.reset}




>     def reset()




    
##### `Method to_json` {#conversationkg.conversations.ledger.Universe2.to_json}




>     def to_json(
>         dumps=False
>     )





    
#### Methods


    
##### Method `call_self` {#conversationkg.conversations.ledger.Universe2.call_self}




>     def call_self(
>         self,
>         *args,
>         **kwargs
>     )




    
##### Method `get_call_self` {#conversationkg.conversations.ledger.Universe2.get_call_self}




>     def get_call_self(
>         self
>     )






    
# Module `conversationkg.conversations.topics` {#conversationkg.conversations.topics}







    
## Classes


    
### Class `Topic` {#conversationkg.conversations.topics.Topic}




>     class Topic(
>         index,
>         word_dist,
>         words=None
>     )









    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.topics.Topic.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.topics.Topic.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
##### Method `top_words` {#conversationkg.conversations.topics.Topic.top_words}




>     def top_words(
>         self,
>         n
>     )




    
### Class `TopicInstance` {#conversationkg.conversations.topics.TopicInstance}




>     class TopicInstance(
>         topic,
>         confidence
>     )









    
#### Static methods


    
##### `Method from_json` {#conversationkg.conversations.topics.TopicInstance.from_json}




>     def from_json(
>         json_dict
>     )





    
#### Methods


    
##### Method `to_json` {#conversationkg.conversations.topics.TopicInstance.to_json}




>     def to_json(
>         self,
>         dumps=False
>     )




    
### Class `TopicModel` {#conversationkg.conversations.topics.TopicModel}




>     class TopicModel(
>         email_corpus,
>         n_topics,
>         **kwargs
>     )










    
#### Methods


    
##### Method `assign_topics_to_conversations` {#conversationkg.conversations.topics.TopicModel.assign_topics_to_conversations}




>     def assign_topics_to_conversations(
>         self,
>         email_corpus=None
>     )




    
##### Method `assign_topics_to_emails` {#conversationkg.conversations.topics.TopicModel.assign_topics_to_emails}




>     def assign_topics_to_emails(
>         self,
>         email_corpus=None
>     )




    
##### Method `determine_n_components` {#conversationkg.conversations.topics.TopicModel.determine_n_components}




>     def determine_n_components(
>         self,
>         ns_to_search,
>         email_corpus=None
>     )





-----
Generated by *pdoc* 0.9.1 (<https://pdoc3.github.io>).
