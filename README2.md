# ConversationKG

Extracting and building knowledge graphs from dialogue and analysing them.

### Goals and Features

- we are interested in:
  - the social networks of and hierarchies among the interlocutors of email conversations - who is connected to whom and by what relationships
  - identifying roles, affiliations and other inherent properties of the interlocutors of dialogues
  - intentions and decision-making processes between interlocutors
  - central 'documents' (links, files, etc) that are being mentioned and shared across dialogues
  
- our goals are to:
  - build efficient and intuitive representations of conversational exchanges, specifically in the reprensentational framework of knowledge graphs
  - gauge how closely these respresentations cover the ground truth
  - obtain and build a representative data set and processing tools, to facilitate not only our own research but also future research into similar directions
  - 

- to address these goals, this repository features:
  - scripts to scrape the entire W3C mailing list archives from scratch (just under 2 Mio emails)
  - hierarchies of classes to parse mailing list archives (in the format of the W3C) into a converation-centred data structure
  - functions to obtain two kinds of knowledge graphs from mailing list data:
    1. a knowledge graph built from emails' meta-data (which is meant to represent (parts of) the ground truth of email-based conversations)
    2. a knowledge graph extracted in a 'true' information extraction fashion from emails' text (as 
  - experiments with machine learning-based algorithms on:
    - node classification, i.e. learning to discover the inherent roles and affiliations of the conversations' interlocutors 
    - entity resolution based on textual embeddings obtained from emails' bodies


### Contents

 - [conversationkg](https://github.com/pgroth/conversationkg/blob/master/conversationkg) - an installable package to parse mailing list archives
   into a conversation-based data structure and to build knowledges graphs from that data structure; this package is the core of this repository.
   
 - [scrape_W3C](https://github.com/pgroth/conversationkg/blob/master/scrape_w3c) - scripts to scrape the 
   [W3C mailing list archives](https://lists.w3.org/Archives/Public/) into a JSON-based corpus
   
 - [analytics](https://github.com/pgroth/conversationkg/blob/master/analytics) - machine learning experiments to 
   
 - [email_data_compressed](https://github.com/pgroth/conversationkg/blob/master/email_data_compressed) - example mailinglists taken from the W3C archives, compressed and added to the repository for development and exemplification
 
 
 
## Instructions for Use

### Installation

Requires Python>=3.6 and Python pip. No virtual environment needed (and not tested), creates a local site-packages installation.

Steps:
 1. clone this repository (e.g. by running `git clone https://github.com/pgroth/conversationkg.git` in a command-line interface)
 2. navigate to the cloned repository and run `python -m pip install .` 

### Importing & 

`import conversationkg`

`from conversationkg.conversations import EmailCorpus, Conversation, Email` etc.; the members of the class-hierarchy are listed in `conversationkg.conversations.members`



### 0. Required Format

The scraped W3C mailing lists are stored as JSON dict objects and the current implementation of `conversation_building.declarations.corpus.EmailCorpus` expects such a format. Below is an example of the `public-credentials` mailing list, namely the first email of the first conversation (subject `Use-Case: Deaths`) of the first period (`2015Aug`, i.e. August 2015):

```
public_credentials = """
{'2015Aug': 
     {'Use-Case: Deaths': 
         [  
             {'body': '\nAppearing at the infamous annual Def Con <https://www.defcon.org/> IT\nsecurity conference in Las Vegas this week, Mr Rock demonstrated gaping\nflaws that have surfaced in the rush to go digital\n<https://4a5b508b5f92124e39ff-ccd8d0b92a93a9c1ab1bc91ad6c9bfdb.ssl.cf4.rackcdn.com/2015/01/150122-Births-Deaths-Marriages-Records-To-Go-Online.pdf>\nwith\nthe process of registering births and deaths in Australia.\n\nRead more:\nhttp://www.theage.com.au/digital-life/consumer-security/meet-chris-rock-the-man-with-the-power-to-kill-off-any-australian-20150809-giuuxd.html\n<http://www.theage.com.au/digital-life/consumer-security/meet-chris-rock-the-man-with-the-power-to-kill-off-any-australian-20150809-giuuxd.html?utm_campaign=echobox&utm_medium=Social&utm_source=Facebook#ixzz3iIqYrCHc>\n',
              'author': 'Timothy Holborn (timothy.holborn@gmail.com)',
              'subject_from_meta': 'Use-Case: Deaths',
              'date': '2015-08-09',
              'isoreceived': '20150809080538',
              'isosent': '20150809080430',
              'sent': 'Sun, 9 Aug 2015 18:04:30 +1000',
              'name': 'Timothy Holborn',
              'email': 'timothy.holborn@gmail.com',
              'subject': 'Use-Case: Deaths',
              'id': 'CAM1Sok0TpowLbun83N+_QRyd14amti3ME0uPTRtodtnNGx87-Q@mail.gmail.com',
              'charset': 'UTF-8',
              'inreplyto': None,
              'from': 'Timothy Holborn <timothy.holborn@gmail.com>',
              'date_from_body': 'Sun, 9 Aug 2015 18:04:30 +1000',
              'to': 'W3C Credentials Community Group <public-credentials@w3.org>',
              'id_from_body': None,
              'original_path': ['public-credentials', '2015Aug', 'Use-Case: Deaths', '0021.html']
            }
        ]
    }
}
"""            
```
Notice that some of the meta-data entries duplicate information, such as `author` and `from`; `conversation_building.declarations.emails` defines how such duplicated information is resolved. All keys in the meta-data need to be present for parsing but can may empty (`""`) values. However, some meta-data information is necessary for certain functionality when extracting the KG; for instance, the `"sent"` meta-data entry is used to obtain temporal ordering on both conversations and emails inside those in the email corpus.


 
