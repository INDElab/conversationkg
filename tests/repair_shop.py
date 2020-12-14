from conversationkg import example_mailinglists, load_example_data_as_raw_JSON

from conversationkg.conversations import EmailCorpus

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, SpaCyNER,\
             RakeKeyWordExtractor, StanzaNER, AddressFactory, LinkFactory
from conversationkg.kgs.writers import CSVWriter

# from conversationkg import load_example_data_as_EmailKG, load_example_data_as_TextKG
from conversationkg.kgs import EmailKG, TextKG

print("SUCCESS: Imports passed")


parallel = False


mailing_list = "ietf-http-wg"
    
raw_data = load_example_data_as_raw_JSON(mailing_list)
corpus = EmailCorpus.from_email_dicts(raw_data[:10], parallel=parallel)

print(f"\nSUCCESS [{mailing_list}]: Corpus instantiated")


vectoriser = TfidfVectorizer(corpus, min_df=5)
vectoriser(corpus, attach_matrices_to_corpus=True, parallel=parallel) # CHANGED: ADDED PARAMETER
    
lda = SKLearnLDA(corpus, n_topics=5, max_iter=100, verbose=0)
rake = RakeKeyWordExtractor()
    
addr_f = AddressFactory()
link_f = LinkFactory()


#%%


link_f(corpus, parallel=True)




#%%


from joblib import Parallel, delayed

def s(e):
    setattr(e, "vale", 13)
    return e.vale


d = delayed(s)


with Parallel(n_jobs=2) as parallel:
    result = parallel(d(e) for e in corpus.iter_emails())

