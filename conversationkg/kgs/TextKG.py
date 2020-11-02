from tqdm import tqdm

#from ..conversations.entities import Person as WholePerson
from .KGs import KG, Person, WholePerson




class TextKG(KG):
    def __new__(cls, email_corpus):
        triples = []
        
        provenances = []
        
        for conv in tqdm(email_corpus, desc="Iterating Conversations in TextKG"):
            triples.append((conv, "is_about", conv.topic.topic))
            provenances.append(conv[0].email_id)
            
            for email in conv:
                triples.append((email, "is_about", email.topic.topic))
                provenances.append(email.email_id)
                
                mentioned_people = [Person(WholePerson(str(e), "")) for e, l in email.body.entities if l == "PERSON"]

                for person in mentioned_people:
                    triples.append((email, "mentions", person))
                    provenances.append(email.email_id)
                    
                    for person2 in mentioned_people:
                        if not person == person2:
                            triples.append((person, "talked_to", person2))
                            provenances.append(email.email_id)

        
        return KG.from_email_corpus(email_corpus, triples, provenances)