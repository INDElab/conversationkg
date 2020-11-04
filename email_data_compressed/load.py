from pkg_resources import resource_string, resource_listdir
import json
import os

from ..conversations import EmailCorpus

def load_data_raw(mailinglist_name):
    x = resource_string(__name__, mailinglist_name+'/all.json')
    return json.loads(x)


def load_data_as_EmailCorpus(mailinglist_name):
    json_data = load_data_raw(mailinglist_name)
    
    conversations = [(subj_str, mail_ls) for period, subj_d in json_data.items() 
                for subj_str, mail_ls in subj_d.items()]
    
    return EmailCorpus(conversations)
    
def get_mailinglist_list():
    return resource_listdir("conversationkg", "sample_data")