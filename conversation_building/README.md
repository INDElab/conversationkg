# Building Conversation Objects and Graphs from the Scraped W3C Emails


## Moving Parts

### 1. Extracting Quoted Text:
   - [ ] Emails are already sorted into conversations, so quoted text in a reply can be identify via per-line string distance from previous emails
   - [x] use a library: for now [email-reply-parser](https://github.com/zapier/email-reply-parser) (which specifically uses regular expressions), other libraries include [quotequail](https://github.com/closeio/quotequail) and [talon](https://github.com/mailgun/talon) (the latter is a general email utility toolbox)
   
### 2. Topic Model

HDP are not implemented in sklearn and sklearn and gensim require different representations 

   - [x] [sklearn.decomposition.LatentDirichletAllocation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html): classic LDA, uniform topic prior
   - [ ] [gensim.models.HdpModel](https://radimrehurek.com/gensim/models/hdpmodel.html): Hierarchical Dirichlet Process which generalises LDA in that the number of topics is also inferred
