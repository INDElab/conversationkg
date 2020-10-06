# conversationkg
Building knowledge graphs from dialogue and analyzing them

Guide to directories (See READMEs in each for more information)

* [w3c_emails](https://github.com/pgroth/conversationkg/blob/master/w3c_emails) - building a knowledge graph from an old, incomplete crawl of W3C mailing lists. This folder is obsolete: [scrape_W3C](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C) implements crawling the _entire_ W3C mailinglist archive from scratch. Further, corpus building and graph construction have been separated and reside, respectively, in [conversation_building](https://github.com/pgroth/conversationkg/blob/master/conversation_building) and [analytics](https://github.com/pgroth/conversationkg/blob/master/analytics).
* [embeddings_for_the_people](https://github.com/pgroth/conversationkg/blob/master/embeddings_for_the_people) - entity resolution as authorship attributioon.
* [scrape_W3C](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C) - scraping the W3C email lists ourselves to make a bigger and cleaner corpus.
* [conversation_building](https://github.com/pgroth/conversationkg/blob/master/conversation_building) - using the scraped W3C email lists to build conversation-based knowledge graphs as a test bed for analytics.
* [analytics](https://github.com/pgroth/conversationkg/blob/master/analytics) - first ideas and plans for, then implementations of analyses of how conversation-based KGs, and ML algorithms trained on them, perform in terms of usability, efficacy and helpfulness to human analysts


## Guide to Extracting a Conversational KG from a Corpus

