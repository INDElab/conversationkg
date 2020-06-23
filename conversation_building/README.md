# Building Conversation Objects and Graphs from the Scraped W3C Emails


## Moving Parts

### Corpus Definitions

 - the order of conversations in the corpus is according to their starting time (time sent of the first email) 
 <br> 
 
 - on the conversation level, there are only interlocutors, no distinction between senders and receivers in being made (purely by choice, could be easily amended)
 - the organisations in a converstation are exactly those to which the interlocutors belong (thus excluding organisations of people in CC, etc.)
 - the documents of a conversation is defined as the set of URLs, addresses and extracted code snippets in the bodies of the conversation's emails; these different types of documents can still be distinguished by having different Python classes
 <br>
 
 - conversations have an inherent subject while emails also report subjects of their own; optimally and in most cases, these are the same (except for a "Re:"-prefix in emails that are replies) <br>
 => currently, conversations and emails have as subjects those which they individually report, with no resolving or merging performed
 
 - emails report multiple values for some of their meta properties:
    - sender name & address: each defined at most three times (fields `author`, `from`, `name`, `email`) <br>
    => currently use fields `name` and `email` (tend to be the most reliable)
    - time sent: defined at most three times (fields `date`, `date_from_body`, `isosent`) <br>
    => currently use field `date_from_body` (has the most convenient format for parsing as `datetime` object)
    - email ID: some emails report an ID additionally in their body <br> => currently use only the ID given in the email's header <br><br> 
    => should eventually use some merging heuristic for duplicate property values, such as majority voting
 
### 1. Extracting Quoted Text:
   - [ ] Emails are already sorted into conversations, so quoted text in a reply can be identify via per-line string distance from previous emails
   - [x] use a library: for now [email-reply-parser](https://github.com/zapier/email-reply-parser) (which specifically uses regular expressions), other libraries include [quotequail](https://github.com/closeio/quotequail) and [talon](https://github.com/mailgun/talon) (the latter is a general email utility toolbox)
   
### 2. Topic Model

HDP are not implemented in sklearn and sklearn and gensim require different representations 

   - [x] [sklearn.decomposition.LatentDirichletAllocation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html): classic LDA, uniform topic prior
   - [ ] [gensim.models.HdpModel](https://radimrehurek.com/gensim/models/hdpmodel.html): Hierarchical Dirichlet Process which generalises LDA in that the number of topics is also inferred
