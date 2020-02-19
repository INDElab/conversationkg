# Corpus and Parsing

W3C mailing list crawled and parsed in 2005: https://tides.umiacs.umd.edu/webtrec/trecent/parsed_w3c_corpus.html <br>
 - Original dataset has around 170k e-mails
 - After processing around 140k remain; rest is dropped due to missing/inconsistent information
 
 ## Processing Pipeline

 1. parse e-mail headers (lines at the top of each e-mail in field=value format) (see `parse_headers.ipynb`):
   - extract sender address, receiver, subject, etc
   - extract time sent and parse into Python object
   - extract e-mail id, a unique identifier -> used to link e-mails by field inreplyto
   
   
 2. parse e-mail bodies, for now (see `parse_bodies.ipynb`):
   - convert to UTF-8 encoding (original latin-1) and unescape HTML entities
   - identify and remove quoted text (usually starts with > or | and introduced by a line with info about the previous e-mail)
   - extract URIs (i.e. HTTP links and e-mail addresses) mentioned in the body
   
   
 3. sort e-mails by time sent and group into conversations according to fields id and inreplyto (see `group_conversations.ipynb`)
 
=> conversations are the central entities in the graph we are building



## Extraction of Entities and Graph Structure

 - an Email has entities such Persons, Organisations and Links/Addresses and relations such as Sender(Email, Person), BelongsTo(Person, Organisation), Mentions(Email, Link)
 
 - a Conversation is simply a list of Email, leading to the relation EvidencedBy(Conversation, [Email_1, ..., EMail_n]), and inherits the relations of the Emails it consists of, that is e.g. Mentions(Conversation, Link)

see `extract_everything.ipynb`

## Provenance

 - to be able to recall where a fact or entity is from, store the id of the e-mail(s) it was extracted from
 - introduce two relations: EvidencedBy and MentionedBy, e.g. EvidencedBy(Person, Email) or MentionedBy(Org, Email), that are stored in an additinal ledger
