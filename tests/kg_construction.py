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

from conversationkg.conversations import Person
from conversationkg.kgs import KG
from conversationkg.kgs import PersonNode



class EmailKG(KG):
    def __new__(cls, email_corpus):
        triples = []
        
        provenances = []
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in EmailKG"):            
            for email in conv:
                sender, receiver = Person(email.sender),\
                                        Person(email.receiver)
                
                
                triples.append((sender, "part_of", conv))
                provenances.append(email.message_id)
                
                triples.append((receiver, "part_of", conv))
                provenances.append(email.message_id)
                
                
                triples.append((sender, "talked_to", receiver))
                provenances.append(email.message_id)
                
#                triples.append((sender, "evidences", sender.address))
#                provenances.append(email.message_id)                
#                triples.append((receiver, "evidences", receiver.address))
#                provenances.append(email.message_id)                
                

                triples.append((sender.organisation, "part_of", conv))
                provenances.append(email.message_id)                
                triples.append((receiver.organisation, "part_of", conv))
                provenances.append(email.message_id)

                triples.append((sender.organisation, 
                                     "talked_to", receiver.organisation))
                provenances.append(email.message_id)
                triples.append((sender, "evidences",
                                     sender.organisation))
                provenances.append(email.message_id)

                triples.append((receiver, "evidences",
                                     receiver.organisation))
                provenances.append(email.message_id)

        
        return KG.from_email_corpus(email_corpus, triples, provenances)


class TextKG(KG):
    def __new__(cls, email_corpus):
        triples = []
        
        provenances = []
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in TextKG"):
            triples.append((conv, "is_about", conv.topic.topic))
            provenances.append(conv[0].message_id)
            
            for email in conv:
                triples.append((email, "is_about", email.topic.topic))
                provenances.append(email.message_id)
                
                mentioned_people = [PersonNode(Person(str(e), "")) for e, l in email.body.entities 
                                    if l == "PERSON"]

                for person in mentioned_people:
                    triples.append((email, "mentions", person))
                    provenances.append(email.message_id)
                    
                    for person2 in mentioned_people:
                        if not person == person2:
                            triples.append((person, "talked_to", person2))
                            provenances.append(email.message_id)

        
        return KG.from_email_corpus(email_corpus, triples, provenances)
    
    
    
#%%