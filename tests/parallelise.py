print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON

from conversationkg.conversations import EmailCorpusCollection, EmailCorpus, Conversation
from conversationkg.kgs import EmailKG, TextKG

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, SpaCyNER, RakeKeyWordExtractor

from tqdm import tqdm
from joblib import Parallel, delayed


def split_list(ls, n_chunks):
    q, r = divmod(len(ls), n_chunks)
    stop = 0
    for i in range(1, n_chunks + 1):
        start = stop
        stop += q + 1 if i <= r else q
        yield ls[start:stop]
        
        
        
print("SUCCESS: Imports passed")

example_mailinglist = "ietf-http-wg"


raw_data = load_example_data_as_raw_JSON(example_mailinglist)[:300]

#chunks = list(split_list(raw_data, 4))


processor = Parallel(n_jobs=4)

delayed_f = delayed(Conversation.from_email_dicts)

conversations = processor(delayed_f(subj, d) for subj, d in tqdm(raw_data))

corpus = EmailCorpus(conversations)

print(len(corpus), corpus.n_emails)


split_corpus = list(split_list(corpus, 4))

coll = EmailCorpusCollection(split_corpus)


ner = SpaCyNER()

ner(corpus)


single_corpus = corpus


#df = delayed(ner)
#
#processor(df(corp) for corp in tqdm(coll))
#
#
#single_corpus = coll.merge_corpora()


print()
print(single_corpus[0].entities)
print()
print(single_corpus[0][0].entities)


print(f"SUCCESS")