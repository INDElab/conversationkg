# Notes

A place for shared notes and pointers

- Work of [Svitlana Vakulenko](https://svakulenk0.github.io/) is interesting. 
    - Her phd on knowledge based conversational search is good. 
    - Start with the [slides](https://svakulenk0.github.io/pdfs/slides/defence_final.pdf)
- [An introduction to dialog research](https://docs.google.com/presentation/d/1arMKZks0_IEqdsvJrPrhqa_9yEdq57CCY_Dm9wlETrM/mobilepresent?slide=id.g2a1dee6562_0_221)


## New Tasks

- More data:
    - larger, higher quality, more extensive coverage of domains
    - e.g. (1) scrape more of the W3C mailing lists, (2) Spotify Podcast Dataset, (3) revisit other data sets?
    
- Situating the conversations in larger context:
    - Connecting to KB such as Wikidata, linking and resolving entities
    - Using ML methods on the data, e.g. topic modelling or open IE <br>
       => perhaps embedding-based with BERT
    - Gathering mentioned or attached documents <br>
      => techniques from data and knowledge fusion [Google Paper](http://www.vldb.org/pvldb/vol7/p881-dong.pdf)
    
- Conversation-based KG: 
    - (More detailed) indexing of mentions of entities and concepts in dialogues (-> cf. tracking)
    - Comparing/Contrasting/Merging (novel) conversation-based KG to/with other/existing KGs <br>
       -> e.g. dialogue-typical distributions and their implications
    - Work more towards conversation-based data structure
    - Tracking and analysing entities' involvement in and across conversations
    

- Linguistic Analyses:
    - Anticipating the 'completedness' of a conversation? E.g. by modelling the probability of another reply
    - Gauging the degree of 'self-standingness' of a conversation? <br>
      => e.g. by the required number of links to a large KB
    - Questions & Answers: Decide which questions are answered and find their answers
    - Linguistic/Stylistic analyses? 
  
