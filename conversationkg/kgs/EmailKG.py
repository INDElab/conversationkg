from tqdm import tqdm

from .KGs import KG, Person

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

        