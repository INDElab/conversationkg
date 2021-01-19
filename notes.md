# Notes

A place for shared notes and pointers

- Work of [Svitlana Vakulenko](https://svakulenk0.github.io/) is interesting. 
    - Her phd on knowledge based conversational search is good. 
    - Start with the [slides](https://svakulenk0.github.io/pdfs/slides/defence_final.pdf)
- [An introduction to dialog research](https://docs.google.com/presentation/d/1arMKZks0_IEqdsvJrPrhqa_9yEdq57CCY_Dm9wlETrM/mobilepresent?slide=id.g2a1dee6562_0_221)


## New Tasks

- More data:
    - larger, higher quality, more extensive coverage of domains
    - e.g. (1) scrape more of the W3C mailing lists, (2) [Spotify Podcast Dataset](https://engineering.atspotify.com/2020/04/16/introducing-the-spotify-podcast-dataset-and-trec-challenge-2020/), (3) revisit other data sets?
    - also obtain attached or mentioned documents in the process of scraping 
    
- Situating the conversations in larger context:
    - Connecting to KB such as Wikidata, linking and resolving entities
    - Using ML methods on the data, e.g. topic modelling or open IE <br>
       => perhaps embedding-based with BERT
    - Gathering mentioned or attached documents <br>
      => techniques from knowledge fusion [(Google Paper)](http://www.vldb.org/pvldb/vol7/p881-dong.pdf)
    
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
    - Linguistic/Stylistic analyses? e.g. detecting and classifying meta-dialogue expressions 
  
  
  
  
## Papers and tools for KGE and OpenIE


 ### Processed Datasets:
 
   - OPIEC: OpenIE done on entire English Wikipedia with additional annotations <br>
     (_Gashteovski et al.: OPIEC: An Open Information Extraction Corpus_)

   - X-WikiRE: OpenIE done cross-linguistically on Wikipedia of 5 European languages <br>
     (_Abdou et al.: X-WikiRE: A Large, Multilingual Resource for Relation Extraction as Machine Comprehension_) <br>
     -> in addition to providing annotated multilingual data, paper shows that cross-lingual transfer leads to more robust extraction models


 ### KGE, i.e. entity set and relation set given and task is essentially classification:
   
   - SpERT: joint entity and relation extraction based on BERT embeddings <br>
     (_Eberts & Ulges: Span-based Joint Entity and Relation Extraction with Transformer Pre-training_) <br>
     -> similar: _Dixit & Al-Onaizan Span-Level Model for Relation Extraction_
     
   - Comet: Transformer-LM-based approach to KB completion in natural language phrases<br>
     (_Bosselut at al.: COMET: Commonsense Transformers for Automatic Knowledge Graph Construction_)
   
 ### OpenIE, i.e. discovery rather than extraction of entities and relations:
 
   - Summary: Map existing OpenIE studies according to formally defined criteria to identify trends and issues
     (_Glauber & Claro: A systematic mapping study on open information extraction_)
     
   - Summary: Broad overview over exisiting OpenIE approaches, models and tools, including review of performance and open problems <br>
     (_Niklaus et al.: A Survey on Open Information Extraction_)
    
   - MinIE: model and tool for OpenIE, reportedly more robust to polarity and modality of facts <br>
     (_Gashteovski et al.: MinIE: Minimizing Facts in Open Information Extraction_)
   
   - CORE: OpenIE model which integrates contextual information to increase accuracy <br>
     (_Petroni et al.: CORE: Context-Aware Open Relation Extraction with Factorization Machines_) <br>
     -> related: _Sorokin & Gurevych: Context-Aware Representations for Knowledge Base Relation Extraction_
     
 ### Python Libraries for Graph Datastructures and Algorithms
   
