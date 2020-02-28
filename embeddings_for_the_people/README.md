# Entity Resolution as Authorship Attribution

## Plan

### Idea 1:

Re-train BERT with a binary classifier for people on top:

 - in training mode, use BERT to obtain embeddings for e-mails
 - feed the e-mail's embedding together with label for person X into a binary classifier <br>
    -> output probability is interpreted as probability that $author(e-mail) = X$
 - Q: labels for person X? just an index? use BERT to embed (name, address)-tuple?
 
 - data:
    - positive samples: ((name, addr), body) for each e-mail in w3c corpus with (name, addr) unique ID of true author and body the main text
    - negative samples: same but author labels randomly swapped -> use string difference measure to ensure that assigned author really not the true author
    - two assumptions: 
      1. for each e-mail in the corpus, the given label (name, addr) is a true label for the true author
      2. with string distance high enough, an author label from a different e-mail truly is from a different author
    
    
### Idea 2:

Fine-tune BERT on each person, obtaining an LM for each person, then use Bayes Theorem

  - assume a generative process: e-mail m ~ Person X <br> 
  -> an LM trained on the all e-mails of X converges in the limit to this source <br>
  -> for each X, re-train BERT to become BERT_X
  
  - given an author-LM which can assign a probability to an e-mail under that author, $P(m | X)$ use Bayes Theorem: <br>
  $P(X|m) \propto P(X)\times P(m|X)$ <br><br>
  
  => problem: BERT does not actually define a probability distribution over texts (see [1] and [2]) <br>
  -> could add a post-processing step (in the form of additional layer) to transform the outputs into probabilities <br>
    use `BertForMaskedLM.model(input).prediction_scores` from `transformers` to for scores
  => GPT-2 supports probabilities!
  
  
 


## Libraries & Tools 

 - huggingface: pre-trained [DistillBERT] (incl. tokenizer, etc.)
 - t-SNE: [sklearn.manifold.TSNE]
 - Factor Analysis: [sklearn.decomposition.FactorAnalysis]
 - Independent Component Analysis: [sklearn.decomposition.FastICA]



## E-mail2Vec Pipeline

 1. 







## Skipped Issues & Implementation Notes

 - cased (`distilbert-base-cased`) version of DistilBert could not be found <br>
   -> using uncased (`distilbert-base-cased`)
 - no sentence segmentation by DistilBertTokenizer (not needed?) <br>
   -> no sentence segmentation for now (although punctuation marks are encoded)
 - what is the sequence vector in the outputs of the model? (cf what Peter mentioned) <br>
   -> using the average of the token vectors, like most others (cf [SBERT])
   -> use specific architecture for sentence embeddings? (such as [SBERT])
 - BERT takes at most 512 tokens, so need to split into smaller chunks
   -> was cutting e-mails longer than 512 into independent chunks and averaging
   -> now: cutting up into chunks of size at most 512 each with 20 tokens overlap with the previous
 - GPT-2 takes at most 1024 tokens
   -> splitting up into independent chunks (with overlap complicated from probability computation)
   -> to generate batches: omitting last chunk if has fewer tokens than the other chunks








[DistillBERT]: https://huggingface.co/transformers/model_doc/distilbert.html
[sklearn.manifold.TSNE]: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
[sklearn.decomposition.FactorAnalysis]: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FactorAnalysis.html
[sklearn.decomposition.FastICA]: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html
[SBERT]: https://arxiv.org/pdf/1908.10084.pdf
[1]: https://github.com/google-research/bert/issues/35
[2]: https://arxiv.org/pdf/1904.09408.pdf
