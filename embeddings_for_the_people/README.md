# Entity Resolution as Authorship Attribution

## Plan


## Libraries & Tools 

 - huggingface: pre-trained [DistillBERT] (incl. tokenizer, etc.)
 - t-SNE: [sklearn.manifold.TSNE]
 - Factor Analysis: [sklearn.decomposition.FactorAnalysis]
 - Independent Component Analysis: [sklearn.decomposition.FastICA]



## E-mail2Vec Pipeline

 1. 




## Skipped Issues & Notes

 - cased (`distilbert-base-cased`) version of DistilBert could not be found <br>
   -> using uncased (`distilbert-base-cased`)
 - no sentence segmentation by DistilBertTokenizer (not needed?) <br>
   -> no sentence segmentation for now (although punctuation marks are encoded)
 - what is the sequence vector in the outputs of the model? (cf what Peter mentioned) <br>
   -> for development using the sum of the token vectors
   -> use specific architecture for sentence embeddings? (such as [SBERT])
 - need to add special tokens at start and end of each text? (pertains to DistilBertTokenizer)
   -> added for now, results probably invariant anyway
 - need to overlap chunks of 512 tokens in e-mails
   -> currently cutting e-mails longer than 512 into independent chunks and averaging

[DistillBERT]: https://huggingface.co/transformers/model_doc/distilbert.html
[sklearn.manifold.TSNE]: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
[sklearn.decomposition.FactorAnalysis]: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FactorAnalysis.html
[sklearn.decomposition.FastICA]: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html
[SBERT]: https://arxiv.org/pdf/1908.10084.pdf

