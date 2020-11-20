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
    
    corpus = load_example_data_as_EmailCorpus(mailing_list, n_conversations=50, **corpus_args)
    print(f"SUCCESS [{mailing_list}]: Corpus instantiated")

    topic_model = TopicModel(corpus, 10, **topic_model_args)
    topic_model.assign_topics_to_emails()
    topic_model.assign_topics_to_conversations()
    print(f"SUCCESS [{mailing_list}]: Topics assigned")

    emailkg = EmailKG(corpus)
    textkg = TextKG(corpus)
    print(f"SUCCESS [{mailing_list}]: EmailKG and TextKG extracted")


print(f"SUCCESS")



#
##%%
#
#
#from conversationkg import load_example_data_as_raw_JSON
#from conversationkg.conversations import EmailCorpus, Conversation, Email
#from conversationkg.kgs import TextKG
#
#
##%%
#
#d_raw = load_example_data_as_raw_JSON("ietf-http-wg")
#
#corpus = EmailCorpus.from_email_dicts(d_raw)
#
##%%
#
#def get(json, prop):
#    return [email_d[prop] for conv in json for email_d in conv[1]]
#
#
#ids = get(d_raw, "id")
#
#d_mod = d_raw
#
#
#for conv in d_mod:
#    for email_d in conv[1]:
#        email_d["id"] = "13"
#        email_d["inreplyto"] = "13"
#
#
##%%
#    
#
#    
#corp_mod = EmailCorpus.from_email_dicts(d_mod[:10])
#
#single_conv = [ed for conv in d_mod for ed in conv[1]]
#corp2 = EmailCorpus.from_ungrouped_email_dicts(single_conv[:100])
#
#
##%%
#
#from conversationkg.conversations.corpus import group_by_id
#
#
#single_conv_ = [Email.from_email_dict(e) for e in single_conv[:10]]
#
#grouped = list(group_by_id(single_conv_))
#
##%%
#
#from collections import defaultdict
#
#emails_by_id = {e.message_id:e for e in single_conv_}
#successors = defaultdict(list)
#for e in single_conv_:
#    if e.inreplyto_id:
#        if e.inreplyto_id in emails_by_id:
#            predecessor_e = emails_by_id[e.inreplyto_id]
#            successors[predecessor_e].append(e)
#        else:
#            successors[None].append(e)
#    else:
#        successors[None].append(e)
#
#
##%% 
#
#tkg_mod = TextKG(corp_mod)
#

