print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON
from conversationkg import load_example_data_as_EmailCorpus

from conversationkg.conversations import EmailCorpusCollection
from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, SpaCyNER, RakeKeyWordExtractor

# from conversationkg import load_example_data_as_EmailKG, load_example_data_as_TextKG
from conversationkg.kgs import EmailKG, TextKG

print("SUCCESS: Imports passed")


vectoriser_params = dict(min_df=5)
lda_params = dict(n_topics=5, max_iter=100)


collection = EmailCorpusCollection([])

for mailing_list in example_mailinglists:
    print(f"\nCurrent mailing list: {mailing_list}...")
    
    corpus = load_example_data_as_EmailCorpus(mailing_list, n_conversations=50)
    print(f"\nSUCCESS [{mailing_list}]: Corpus instantiated")

#    vectoriser = TfidfVectorizer(corpus, **vectoriser_params)
#    vectoriser(corpus)
#
#    factories = [
#            SKLearnLDA(corpus, **lda_params),
#            SpaCyNER(),
#            RakeKeyWordExtractor()
#            ]
#    
#    
#    
#    for f in factories:
#        f(corpus)
        
    collection.append(corpus)

    
#    topic_model = TopicModel(corpus, 10, **topic_model_args)
#    topic_model.assign_topics_to_emails()
#    topic_model.assign_topics_to_conversations()
#    print(f"SUCCESS [{mailing_list}]: Topics assigned")

    emailkg = EmailKG(corpus)
    textkg = TextKG(corpus)
    print(f"SUCCESS [{mailing_list}]: EmailKG and TextKG extracted")


print(f"SUCCESS: EmailCorpusCollection collected \n\t"
      f"(total of {len(collection)} corpora, {collection.n_conversations} conversations," 
      f" {collection.n_emails} emails)")


print(f"SUCCESS")


#%%