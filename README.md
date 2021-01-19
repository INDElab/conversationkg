# conversationkg

Building knowledge graphs from dialogue and analyzing them.

## Goals and Functions

 - parsing email conversations in (standard) JSON format into hierarchies of Python objects in order to make tasks such as inspection, iteration and extraction convenient
 
 - exposing interfaces for common information extraction tasks, such as NER, topic modelling and keyword extraction on email data
 
 - implementing basic versions of two types of knowledge graphs of email conversations:
   - EmailKG, a ground-truth graph based on the emails' meta-data
   - TextKG, a graph obtained purely by information extraction on emails' textual bodies
 
 - facilitating and testing the feasibility of machine-learning experiments based on conversational data
 
## Contents of the Repository

conversationkg is both a package and a repository, the below list is a guide to the directories in this repository (see the READMEs in each for more information):

 - [analytics](./analytics) - ML experiments based on the the W3C email data and knowledge graphs defined in the `conversationkg` package  
 - [conversationkg](./conversationkg) - the code of the `conversationkg` Python package described in the next section, see the [API documentation](https://indelab.github.io/conversationkg)
 - [docs](./docs) - API documentation for the `conversationkg` package, auto-generated by [pdoc3](https://pdoc3.github.io/pdoc/), served at [this address](https://indelab.github.io/conversationkg/)
 - [email_data_compressed](./email_data_compressed) - (compressed) data from two W3C mailing lists ([public_credentials](https://lists.w3.org/Archives/Public/public-credentials) and [http-ietf-wg](https://lists.w3.org/Archives/Public/ietf-http-wg/)
 - [scrape_W3C](./scrape_W3C) - scripts to scrape the entire [W3C mailing list archive](https://lists.w3.org/Archives/Public/), via HTML requests and parsing
 - [test](./tests) - should be self-explanatory, includes tests both for the `conversationkg` package and directed at the uses in the analytics directory
 


## Working with the `conversationkg` package

### Installation

Requires Python>=3.6 and Python pip; no virtual environment needed (and not tested), this creates a local site-packages installation by default. For Python-internal dependencies, see [requirements.txt](requirements.txt).
Installation steps:

 1. clone this repository (e.g. by running `git clone https://github.com/pgroth/conversationkg.git` in your command-line interface)
 2. navigate to the cloned repository and run `python -m pip install .`
 
_Note: The installation copies and extracts the contents of email_data_compressed into the package, which will occopy up to a GB of memory. The mailinglist data in email_data_compressed can subsequently be loaded as part of the package and should make development with this data easier._

#### Contribute

Once you have cloned a local copy and made changes you wish to upload to the `main` branch of this repository, follow these (standard) steps:
  0. use `git pull` to update your local copy with remote changes (git will alert and abort if local changes would be overwritten)
  1. to add all changes at once, run `git add .` in the root directory (`git add [some folder]` only adds the changes made in `[some folder]`)
  2. commit the added changes with `git commit -m "[your message]"` where `[your message]` is hopefully a meaningful description of the changes
  3. finally, upload the changes to the repository by running `git push`
  
You can check what your changes are, if any, by running `git status`.
You can, of course, also make a new branch that will co-exist with the `main` branch and upload your changes to that. Or make a pull request if you want your changes approved by the repository's owners before they are integrated. Please refer to GitHub's documentation.

The package's documentation (located in the `docs` folder) is autogenerated by [pdoc3](https://pdoc3.github.io/pdoc/). If you have made changes to the package (and re-installed it), please re-generate the documentation by running `pdoc --html conversationkg` and copy the contents of the produced folder `html` into `docs` (and upload the updated documentation as described above).


### Usage

For the full API documentation, go to https://indelab.github.io/conversationkg.


#### Basics

Once installed, the package can be imported by:

```python
import conversationkg
```

There are two subpackages (for the two subtasks, corpus parsing and knowledge graph extraction):

```python

import conversationkg.corpus 
import conversationkg.kgs

```

Load the example mailinglist `ietf-http-wg` included in the package installation:

```python
from conversationkg import load_example_data_as_raw_JSON

json_data = load_example_data_as_raw_JSON("ietf-http-wg")
```
The names of all included mailing lists can be found in `conversationkg.example_mailinglists`.


Import and instantiate a corpus object:

```python
from conversationkg.conversations import EmailCorpus

corpus = EmailCorpus.from_email_dicts(json_data)

```

The corpus object can alternatively be instantiated via a list of conversation objects:

```python

from conversationkg.conversations import EmailCorpus, Conversation

conversations = [Conversation.from_email_dicts(subject, email_dicts) for subject, email_dicts in json_data

corpus = EmailCorpus(conversations)
```


#### Applying Factories

The most common and basic information extraction tasks are implemented in the `conversationkg` package as so-called *factories* (named so because they produce objects, mainly entities, given emails or conversations). `conversationkg` implements factories for text vectorisation, topic modelling, NER and keyword extraction and has base classes for these so that new factories can easily be added. Factories are applied to a corpus like so:

```python
from conversationkg.conversations import EmailCorpus
from conversationkg.conversations.factories import SKLearnLDA, SpaCyNER, StanzaNER, RakeKeyWordExtraction

corpus = EmailCorpus.from_email_dicts(json_data)

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
corpus.vectorise(TfidfVectorizer)


factories = [SKLearnLDA(corpus, 13, max_iter=10), 
             SpaCyNER(),  # alternatively StanzaNER
             RakeKeyWordExtraction()]

for factory in factories: factory(corpus)

```


Beware that some of the downstream functionality, most importantly the parts of KG extraction, require or relie on factories having already been run on the corpus and may produce useless results otherwise.



#### Instantiating KGs

Instantiating either a TextKG or EmailKG object from a corpus object is as simple as:

```python

from conversationkg.kgs import EmailKG, TextKG

emailkg = EmailKG(corpus)

textkg = TextKG(corpus)

```



### Supplying your own Data: Required Format

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
