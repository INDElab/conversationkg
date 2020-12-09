print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON
from conversationkg import load_example_data_as_EmailCorpus

from conversationkg.conversations import EmailCorpusCollection
from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, SpaCyNER,\
             RakeKeyWordExtractor, StanzaNER, AddressFactory, LinkFactory
from conversationkg.kgs.writers import CSVWriter

# from conversationkg import load_example_data_as_EmailKG, load_example_data_as_TextKG
from conversationkg.kgs import EmailKG, TextKG

print("SUCCESS: Imports passed")


vectoriser_params = dict(min_df=5)
lda_params = dict(n_topics=5, max_iter=100)


collection = EmailCorpusCollection([])



textkgs = []


for mailing_list in ["ietf-http-wg"]:  # example_mailinglists:
    print(f"\nCurrent mailing list: {mailing_list}...")
    
    corpus = load_example_data_as_EmailCorpus(mailing_list, n_conversations=10)
    print(f"\nSUCCESS [{mailing_list}]: Corpus instantiated")


    vectoriser = TfidfVectorizer(corpus, **vectoriser_params)
    vectoriser(corpus, attach_matrices_to_corpus=True) # CHANGED: ADDED PARAMETER
    factory_list = [('stanza',[
        SKLearnLDA(corpus, **lda_params),
        StanzaNER(),
        RakeKeyWordExtractor()
        ]), ('spacy',[
        SKLearnLDA(corpus, **lda_params),
        SpaCyNER(),
        RakeKeyWordExtractor()
        ])]

    
    print(f"\nSUCCESS [{mailing_list}]: Corpus instantiated")
    
    for factory in factory_list: 
        

    # factories = [
    #     SKLearnLDA(corpus, **lda_params),
    #     StanzaNER(),
    #     RakeKeyWordExtractor()
    #     ]
        factories = factory[1]

        for f in factories:
            f(corpus)
            
        collection.append(corpus)

        
    #    topic_model = TopicModel(corpus, 10, **topic_model_args)
    #    topic_model.assign_topics_to_emails()
    #    topic_model.assign_topics_to_conversations()
    #    print(f"SUCCESS [{mailing_list}]: Topics assigned")

        emailkg = EmailKG(corpus)
        textkg = TextKG(corpus)
        textkgs.append(textkg)
        CSVWriter(textkg).to_csv(mailing_list + '_tkg_' + factory[0])
        CSVWriter(emailkg).to_csv(mailing_list+'_ekg_'+factory[0])
    
    print(f"SUCCESS [{mailing_list}]: EmailKG and TextKG extracted")


print(f"SUCCESS: EmailCorpusCollection collected \n\t"
      f"(total of {len(collection)} corpora, {collection.n_conversations} conversations," 
      f" {collection.n_emails} emails)")


print(f"SUCCESS")


#%%