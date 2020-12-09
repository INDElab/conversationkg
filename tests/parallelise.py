print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON

from conversationkg.conversations import EmailCorpusCollection, EmailCorpus, Conversation
from conversationkg.kgs import EmailKG, TextKG

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, StanzaNER, SpaCyNER, RakeKeyWordExtractor

from tqdm import tqdm
from joblib import Parallel, delayed


#def split_list(ls, n_chunks):
#    q, r = divmod(len(ls), n_chunks)
#    stop = 0
#    for i in range(1, n_chunks + 1):
#        start = stop
#        stop += q + 1 if i <= r else q
#        yield ls[start:stop]
        
        
        
print("SUCCESS: Imports passed")

example_mailinglist = "ietf-http-wg"


raw_data = load_example_data_as_raw_JSON(example_mailinglist)[:100]


print("SUCCESS: Data loaded")


#%%

#processor = Parallel(n_jobs=4)
#
#delayed_f = delayed(Conversation.from_email_dicts)
#
#conversations = processor(delayed_f(subj, d) for subj, d in tqdm(raw_data))
#
#corpus = EmailCorpus(conversations)


corpus = EmailCorpus.from_email_dicts(raw_data, parallel=True)


# above the parallelised version vs. the single-process one:
# corpus = EmailCorpus([Conversation.from_email_dicts(subj, d) for subj, d in tqdm(raw_data)])

# comparison:
# 100%|██████████| 100/100 [00:18<00:00,  5.36it/s] <- parallel
# 100%|██████████| 100/100 [00:24<00:00,  4.06it/s] <- serial

print("SUCCESS: Corpus parsed and object instantiated")
print(f"\t({len(corpus)} conversations, {corpus.n_emails} emails)")



#%%


v = TfidfVectorizer(corpus)

v(corpus, parallel=True, attach_matrices_to_corpus=True)

#%%

lda = SKLearnLDA(corpus, 5)

_ = lda(corpus, parallel=True)

#%%

spacy = SpaCyNER(preprocessors=lambda s: s.replace("a", "b"))
spacy_outputs = spacy(corpus, parallel=True) # , n_jobs=4)

stanza = StanzaNER(preprocessors=lambda s: s.replace("a", "b"))
stanza_outputs = stanza(corpus[:3], parallel=False) # , n_jobs=4)




# SpaCyNER iterating conversations in parallel: 100%|██████████| 300/300 [01:18<00:00,  3.81it/s]
# SpaCyNER iterating conversations : 100%|██████████| 300/300 [01:18<00:00,  3.84it/s]
#%%


class StanzaNER:
    def __init__(self, preprocessors=[], postprocessors=[]):
        self.nlp = stanza.Pipeline('en', processors="tokenize, ner")
        
    def get_entities(self, text):
        return [d.text for d in self.nlp(text).ents]
    
    def get_entities_with_labels(self, text):
        return [(d.text, d.type) for d in self.nlp(text).ents]            



#%%

print(f"SUCCESS")