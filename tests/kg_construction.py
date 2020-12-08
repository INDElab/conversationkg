from tqdm import tqdm



print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON

from conversationkg.conversations import EmailCorpusCollection, EmailCorpus, Conversation

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, StanzaNER, SpaCyNER, RakeKeyWordExtractor

print("SUCCESS: Imports passed")

example_mailinglist = "ietf-http-wg"


raw_data = load_example_data_as_raw_JSON(example_mailinglist)[:50]


print("SUCCESS: Data loaded")


#%%

#corpus = EmailCorpus.from_email_dicts(raw_data)


corpus = EmailCorpus([Conversation.from_email_dicts(subj, d) for subj, d in tqdm(raw_data)])


#%%

vec = TfidfVectorizer(corpus)
vec(corpus, parallel=False)

factories = [SKLearnLDA(corpus, 10), 
             SpaCyNER(), RakeKeyWordExtractor()]

for f in factories:
    f(corpus, parallel=False)



#%%


from conversationkg.kgs import KG, EmailKG, TextKG


textkg = TextKG(corpus)

emailkg = EmailKG(corpus)