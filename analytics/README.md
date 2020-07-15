# Analytics

### Focus Points

* social networks - including frequencies of interactions, groups and organisations
* conversational roles & hierarchy
* conversational intentions
* conversational depth & contentfulness
* decision making processes

### General Questions

* how accurately does our KG cover the ground truth, human analysts are seeking to discover, i.e. how much human inference is required?
* do the structure (conversation-based) and quality of our KG effectively assist human analytics?
* is our KG an apt basis ML techniques in assisting human analytics?
* how does our KG compare to other assistance methods, e.g. to topic modelling?


### Setting of Hypothesis Testing

* our KG effectively assists human inference of underlying, ground-truth social networks
  - specifically, our KG covers a large extent of that ground-truth or at least parts which enable efficient inference (cf. low false-negative ratio)
  - specifically, our KG is sufficient quality compared to other potential ones to this end (e.g. low false-positive ratio)
  - specifically, the structure of our KG is sufficiently robust to distortions to this end (confusion matrix is robust to small changes in the extraction method or underlying data)
* our KG effectively enables machine learning techniques to be derived from it which assist human analystics
* our KG outperforms other computational methods to assist human analytics, ML-based or text-based 

### Operationalisations

* W3C is a _real_ organisation, governing _real_ standards, so we can source the ground truth (or at least proxies thereof) of organisational roles and standardisation decisions from the internet; links [[1](#1)] ... [[5](#5)] contain examples of documents and organisation charts from which ground truth on specific subgroups and standards of the W3C could be obtained/scraped; <br>
the listed documents contain some but not all information on:
  - which groups of people belong to specific standardisation bodies
  - which persons belong to the core staff of the W3C, to managing groups of standardisation bodies and parts of the hierarchies between them
  - when creatin standardisation decisions have been made and by whom
  
* large-scale knowledge bases, such as WikiData, contain entries on the standards and technologies decided and maintained by the W3C; <br>
  so e.g. the HTTP standard names its ivnentor and the W3C and IETF as its standardising bodies both of which entities could expanded recusively; <br>
  unfortunately, for this approach of sourcing the ground truth, coverage of the invovled persons and concepts is likely not high enough, leading to
  small and non-complex organisational networks and in turn to little ground truth


* in a different approach, we can treat the KG we extract from the W3C mailing list archives as representative of the ground truth and create less representative KGs; <br>
strategies for creating such KGs either could actively introduce non-existing facts (or omit existing ones), based on various heuristics, or could use other sources for trying to create the same KG
   - for a strategy which uses other sources, see Section [Email KG vs Text KG](#email-kg-vs-text-kg); the idea there is that those other sources both do not contain the same amount of information as the original W3C archive and are associated with less certainty of the extracted facts
   - 

* use ML algorithms on different versions on our graph to assist human analytics, and measure how much performance improves compared to no assistance
 
* choice in operationalisation: provide analysts with either
  1. only the version of the KG from which they are tasked to reconstruct the ground truth
  2. both 1. and the corresponding email texts
  3. only the corresponding email texts

### Email KG vs Text KG

The core idea of this approach is that we may treat the KG extracted from the mailing list archives as the ground truth because these archives consist of email transactions between servers. That is, on the one hand, the corresponding email servers have resolved addresses and identities of senders and receivers and their aossciated email domains. On the other hand, we're not extracting performing knowledge extraction in the same sense as e.g. NER but rather are taking facts directly from the headers in email protocols. Hence if the mailing list archives contain an email from X to Y, then we are almost guaranteed that both X and Y factually exist as entities and X factually talked to Y. 

With this KG as ground truth, we construct/extract a second KG which we give to the human analysts:
We remove all email protocol information from the mailing archives, so that only the email bodies remain and we are left with a purely textual corpus without any metadata. Then, we perform "proper" knowledge extraction, i.e. identify greetings and signatures, perform NER, etc., in order try and construct the same KG as the ground truth graph.




### Hypotheses to Test

* 

### Settings of hypothesis testing:
i.e. hopyetheses to be tested and how

* testing the efficacy of our extracted KG itself in assisting human analytics <br>
  problem: need ground truth, to gauge to what extent the inaccuracies of our KG hinder successful and efficient analytics (and vice-versa) <br>
  remedy: W3C is a _real_ organisation, governing _real_ standards; so we can source the ground truth of organisational structure and roles in conversation from the internet (or at least a proxy of the ground truth, may not be the full truth); see the links for some documents where organisational structures could be scraped; in addition, KBs contain entries to the governing bodies of W3C standards, from which the relevant subgraphs can be recursively extracted <br>
  links: [W3C Group Dependency Graph](https://www.w3.org/2003/02/W3COrg.svgz), [W3C Core Staff](https://www.w3.org/People), [W3C Process Document](https://www.w3.org/2019/Process-20190301/) , [W3C Accessibility Document](https://www.w3.org/TR/2020/WD-accessibility-conformance-challenges-20200619)
  => operationalisation: obtain a (proxy) "ground truth" KG of (a part of) the W3C which contains "real" types, roles, ..., and measures how well analysts can infer these given only the conversations and our KG
  
  
* testing the aptness of our extracted KG as a basis for ML-assisted analytics <br>
  e.g. by treating our own extracted KG as ground truth and testing the efficacy of link prediction algorithms on that KG in helping human analysts <br>
 => operationalisation: train link prediction on KG, distort the KG with omitted true links/added false links, measure how well human analysts reconstruct original KG aided by link prediction system <br>
 
 
 <a id="1">[[1]: W3C Group Dependency Graph](https://www.w3.org/2003/02/W3COrg.svgz)</a>
 
 [[2]: W3C Core Staff](https://www.w3.org/People), 
 
 [[3]: W3C Process Document](https://www.w3.org/2019/Process-20190301/) , 
 
 <a id="4">[[4]: W3C Accessibility Document](https://www.w3.org/TR/2020/WD-accessibility-conformance-challenges-20200619)</a>
