from pkg_resources import resource_string, resource_listdir
import json

from ..conversations import EmailCorpus

from ..kgs import EmailKG, TextKG


def get_mailinglist_list():
    ignore = {"__pycache__", "load.py"}
    return [d for d in resource_listdir(__name__, ".") if not d in ignore]


def load_data_raw(mailinglist_name):
    x = resource_string(__name__, mailinglist_name+'/all.json')
    json_list = json.loads(x)
    return json_list

    
def load_data_as_EmailCorpus(mailinglist_name, n_conversations=-1, **email_corpus_args):
    json_data = load_data_raw(mailinglist_name)[:n_conversations]
    return EmailCorpus.from_email_dicts(json_data, **email_corpus_args)



def load_data_as_EmailKG(mailinglist_name, n_conversations=-1, **kwargs):
    corpus = load_data_as_EmailCorpus(mailinglist_name, n_conversations, **kwargs)
    return EmailKG(corpus)


def load_data_as_TextKG(mailinglist_name, n_conversations=-1, **kwargs):
    corpus = load_data_as_EmailCorpus(mailinglist_name, n_conversations, **kwargs)
    return TextKG(corpus)