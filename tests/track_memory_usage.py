print("Testing...")

from conversationkg import load_example_data_as_raw_JSON, load_example_data_as_EmailCorpus

from conversationkg.conversations import EmailCorpus

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, SpaCyNER,\
             RakeKeyWordExtractor, StanzaNER, AddressFactory, LinkFactory

from conversationkg.kgs import EmailKG, TextKG
from conversationkg.kgs.writers import CSVWriter


print("SUCCESS: Imports passed")

from memory_profiler import profile
@profile
def whole_pipeline():
    corpus = load_example_data_as_EmailCorpus("ietf-http-wg", n_conversations=100)
    print(f"\nCorpus instantiated")

    vectoriser = TfidfVectorizer(corpus, min_df=5)
    vectoriser(corpus, attach_matrices_to_corpus=True)
    
    lda = SKLearnLDA(corpus, n_topics=5, max_iter=100, verbose=0)
    rake = RakeKeyWordExtractor()
    
    spacy = SpaCyNER()
    
    
    addr_f = AddressFactory()
    link_f = LinkFactory()
    
    
    factories = [lda, rake, addr_f, link_f, spacy]
    
    for f in factories: f(corpus)
    
    emailkg = EmailKG(corpus)
    textkg = TextKG(corpus)

    print(f"SUCCESS: EmailKG and TextKG extracted")
    
    return corpus, emailkg, textkg
    


# put whatever function you want to in the __main__ part below
# run this script with python3 -m memory_profiler track_memory_usage.py
# -> will print line-by-line memory usage statistics
if __name__ == "__main__":
    whole_pipeline()