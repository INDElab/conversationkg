print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON
from conversationkg import load_example_data_as_EmailCorpus

from conversationkg.conversations import TopicModel 

# from conversationkg import load_example_data_as_EmailKG, load_example_data_as_TextKG
from conversationkg.kgs import EmailKG, TextKG

print("SUCCESS: Imports passed")

corpus_args = dict(vectorise_default=True)
topic_model_args = dict(max_iter=30)

for mailing_list in example_mailinglists:
    print(f"Current mailing list: {mailing_list}...")
    
    corpus = load_example_data_as_EmailCorpus(mailing_list, n_conversations=1000, **corpus_args)
    print(f"SUCCESS [{mailing_list}]: Corpus instantiated")

    topic_model = TopicModel(corpus, 10, **topic_model_args)
    topic_model.assign_topics_to_emails()
    topic_model.assign_topics_to_conversations()
    print(f"SUCCESS [{mailing_list}]: Topics assigned")

    emailkg = EmailKG(corpus)
    textkg = TextKG(corpus)
    print(f"SUCCESS [{mailing_list}]: EmailKG and TextKG extracted")


print(f"SUCCESS")