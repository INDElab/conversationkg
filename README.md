# conversationkg
Building knowledge graphs from dialogue and analyzing them

Guide to directories (See READMEs in each for more information)

* [w3c_emails](https://github.com/pgroth/conversationkg/blob/master/w3c_emails) - building a knowledge graph from an old, incomplete crawl of W3C mailing lists. This folder is obsolete: [scrape_W3C](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C) implements crawling the _entire_ W3C mailinglist archive from scratch. Further, corpus building and graph construction have been separated and reside, respectively, in [conversation_building](https://github.com/pgroth/conversationkg/blob/master/conversation_building) and [analytics](https://github.com/pgroth/conversationkg/blob/master/analytics).
* [embeddings_for_the_people](https://github.com/pgroth/conversationkg/blob/master/embeddings_for_the_people) - entity resolution as authorship attributioon.
* [scrape_W3C](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C) - scraping the W3C email lists ourselves to make a bigger and cleaner corpus.
* [conversation_building](https://github.com/pgroth/conversationkg/blob/master/conversation_building) - using the scraped W3C email lists to build conversation-based knowledge graphs as a test bed for analytics.
* [analytics](https://github.com/pgroth/conversationkg/blob/master/analytics) - first ideas and plans for, then implementations of analyses of how conversation-based KGs, and ML algorithms trained on them, perform in terms of usability, efficacy and helpfulness to human analysts


## Guide to Extracting a Conversational KG from a Corpus

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



### 1. Instantiate an EmailCorpus Object

As an intermediate step between the raw email data and an actual KG, we read the above JSON format into a object-oriented hierarchy of classes. This step makes KG extraction easy and modular and additionally serves to perform required or desired pre-processing steps, such as determining data volumes, meta-data resolution or named-entity recognition. The class hierarchy is roughly as follows: An EmailCorpus object takes as input a list of Conversation objects which are in turn tuples of the conversation's subject and a list of Email objects. Email objects are instantiated from dicts in the form of the above example. Thus:

```
import json
from declarations.corpus import EmailCorpus, Conversation
from declarations.emails import Email

period_2015Aug = json.loads(public_credentials)["2015Aug"]

email = Email.from_email_dict(["Use-Case: Deaths"][0])

conversation = Conversation(("Use-Case: Deaths", [email]))
# OR VIA SHORTCUT
conversation = Conversation.from_email_dicts(("Use-Case: Deaths", period_2015Aug["Use-Case: Deaths"]))

corpus = EmailCorpus.from_conversations([conversation])

```

Notice that the period structure is omitted when instantiating the Conversation and EmailCorpus objects, that is email data from a different source need not be structured into periods.

### 1.1 Perform TopicModelling

```
 from topics import TopicModel
 
 lda = TopicModel(corpus)
 
 lda.assign_topics_to_emails()
 lda.assign_topics_to_conversations()
 

```


### 2. Extracting a KG

Currently (this will change), the code to extract a KG from an EmailCorpus object resides in `analytics.node_classification.KGs` and there are two types of KG, the EmailKG and TextKG; see [the analytics README](https://github.com/pgroth/conversationkg/blob/master/analytics) and the [KG extraction README](https://github.com/pgroth/conversationkg/blob/master/analytics/node_classification/.mds/KG_extraction.md) for motivation and details of the two types of KGs.

Given an EmailCorpus object, instantiating either type of KG is as simple as

```
from KGs import EmailKG, TextKG

emailkg = EmailKG(corpus)

textkg = TextKG(corpus)
```

### 3. Writing it out to a CSV File

```
emailkg.to_csv("emailkg")

textkg.to_csv("textkg")
```




