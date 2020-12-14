print("Testing...")

from conversationkg import example_mailinglists, load_example_data_as_raw_JSON

from conversationkg.conversations import EmailCorpusCollection, EmailCorpus, Conversation
from conversationkg.kgs import EmailKG, TextKG

from conversationkg.conversations.factories import TfidfVectorizer, SKLearnLDA, StanzaNER, SpaCyNER, RakeKeyWordExtractor

from time import time, sleep
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


raw_data = load_example_data_as_raw_JSON(example_mailinglist)[:10]


print("SUCCESS: Data loaded")

#%%

corpus = EmailCorpus.from_email_dicts(raw_data, parallel=False)

stanza = StanzaNER()


#%%

print("\nStanza parallelised takes:")
t0 = time(); out = stanza(corpus, parallel=False, n_jobs=4); print("\t", time() - t0, "seconds")



sleep(60)

#%%

t = " ".join([conv.get_email_bodies(attr="normalised", join_str=" ")
            for conv in corpus])

print("\nStanza on concatenated texts takes:")
t0 = time(); out = stanza.nlp(t); print("\t", time() - t0, "seconds")



#parallelise NamedEntityFactory as follows:
#   1. implement `__call__` (overriding that of `Factory`)
#   2. concatenate the bodies of (multiple/all) emails together -> put special characters to be able to split text
#   3. run NER on concatenated text
#   4. get list of (entity, label , span) -> latter is important
#   5. split list of entities according to span in concatenated text
## code below 


#%%

#email_sep = "<END_EMAIL>"  # "\n-------------\n"
#conv_sep = "<END_CONVERSATION>"  # "\n\n-------\n\n"
#
#
#texts = [conv.get_email_bodies(attr="normalised", join_str=email_sep)
#            for conv in corpus]
#
#
#t = conv_sep.join(texts)


#%%

#ranges = []
#
#x = 0
#
#l, k = len(conv_sep), len(email_sep)
#
#for i, conv in enumerate(corpus):
#    cur = []
#    for j, email in enumerate(conv):
#        y = x + len(email.body.normalised) + (k if j < len(conv)-1 else 
#                                            (l if i < len(corpus)-1 else 0))
#        cur.append((x, y))
#        x = y
#    ranges.append(cur)
##    x -= k
##    x += l
#
#
##%%
#
#stanza = StanzaNER(verbose="DEBUG")  # , logging_level="DEBUG")
#
##%%
#
#out = stanza.nlp(t)
#
##%%
#
#
#
#
#
#def e_r_iter(corpus):
#    r_c, r_e = (0, 0), (0, 0)
#    for conv in corpus:
#        email in conv:
#            yield conv, email, r_c, r_e
#            
#            
#
#
#
#
#ri = iter(ranges)
#cur = next(ri)
#
#is_in = lambda x, r: x in range(r[0][0], r[-1][1])
#
#ls = []
#conv_es = []
#for e in out.entities:
#    sc, ec = e.start_char, e.end_char
#    
#    if is_in(sc, cur):
#        conv_es.append(e)
#    else:
#        ls.append(conv_es)
#        conv_es = [e]
#        cur = next(ri)
#        if not is_in(sc, cur): raise ValueError(str(sc, ec, cur))
#        
#
#
##%%
#        
#stanza = StanzaNER()
#
##%%
#t = " ".join([conv.get_email_bodies(attr="normalised", join_str=" ")
#            for conv in corpus])
#
#out = stanza.nlp(t)     
##%%
#
#t = " ".join([conv.get_email_bodies(attr="normalised", join_str=" ")
#            for conv in corpus])
#
#
#r = (0, 0)
#
##l, k = len(conv_sep), len(email_sep)
#
#ent_iter = iter(out.entities)
#
#
#for conv in corpus:
#    for email in conv:
#        r = (r[1], len(email) + 1)


#%%

#import re   
#
#
#
#def get(tt, sep, f=lambda x: x):
#    ls = []
#    s = 0
#    print("get ", sep)
#    for m in re.finditer(sep, tt):
#        print("made it inside")
#        e, y = (m.start(0), m.end(0))
#        cur = tt[s:e]            
#        ls.append(f(cur))
#        s = y
#    ls.append(f(tt[s:-1]))
#    return ls
#
#recurse_get = lambda sub: get(sub, email_sep)
#
#convs = get(t, conv_sep, recurse_get)
