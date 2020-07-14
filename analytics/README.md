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
  - specifically, our KG is sufficient quality compared to other potential ones to this end
  - specifically, the structure of our KG is sufficiently robust to small distortions to this end
* our KG effectively enables machine learning techniques to be derived from it which assist human analystics
* our KG outperforms other computational methods to assist human analytics, ML-based or text-based

### Operationalisations

* problem: need ground truth, on one hand for measuring analysts' performance, on the other to measure how accurately our KG represents it <br>
  => remedy: W3C is a _real_ organisation, governing _real_ standards => we can source the ground truth of organisational roles and decided standards from the internet (or at least a close proxy thereof); some document [[1](#1) ... [5](5)].




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
 
 [[2]: W3C Core Staff](https://www.w3.org/People), [W3C Process Document](https://www.w3.org/2019/Process-20190301/) , [W3C Accessibility Document](https://www.w3.org/TR/2020/WD-accessibility-conformance-challenges-20200619)
  

 
 [1](google.com)
 
 [2](faceboo.com)
