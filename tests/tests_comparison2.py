print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_EmailCorpus

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, SpaCyNER,\
             RakeKeyWordExtractor, StanzaNER, AddressFactory, LinkFactory
from conversationkg.kgs.writers import CSVWriter

# from conversationkg import load_example_data_as_EmailKG, load_example_data_as_TextKG
from conversationkg.kgs import EmailKG, TextKG

print("SUCCESS: Imports passed")


parallel=False

vectoriser_params = dict(min_df=5)
lda_params = dict(n_topics=5, max_iter=100, verbose=0)


for mailing_list in example_mailinglists:
    print(f"\nCurrent mailing list: {mailing_list}...")
    
    corpus = load_example_data_as_EmailCorpus(mailing_list, n_conversations=10, parallel=parallel)
    print(f"\nSUCCESS [{mailing_list}]: Corpus instantiated")


    vectoriser = TfidfVectorizer(corpus, **vectoriser_params)
    vectoriser(corpus, attach_matrices_to_corpus=True) # CHANGED: ADDED PARAMETER
    
    lda = SKLearnLDA(corpus, **lda_params)
    rake = RakeKeyWordExtractor()
    
    addr_f = AddressFactory()
    link_f = LinkFactory()
    
    
    factory_dict = {
            'stanza' : [lda, rake, addr_f, link_f, StanzaNER()],
            'spacy' : [lda, rake, addr_f, link_f, SpaCyNER()]
            }
    
    
    print(f"SUCCESS [{mailing_list}]: Factories instantiated")

    
    
    for name, factories in factory_dict.items():
        for f in factories:
            f(corpus, parallel=parallel)
    
            
    
        emailkg = EmailKG(corpus)
        textkg = TextKG(corpus)
        CSVWriter(textkg).to_csv(mailing_list + '_tkg_' + name)
        CSVWriter(emailkg).to_csv(mailing_list+'_ekg_'+ name)
    
        print(f"SUCCESS [{mailing_list}]: EmailKG and TextKG extracted")


#print(f"SUCCESS: EmailCorpusCollection collected \n\t"
#      f"(total of {len(collection)} corpora, {collection.n_conversations} conversations," 
#      f" {collection.n_emails} emails)")


print(f"SUCCESS")