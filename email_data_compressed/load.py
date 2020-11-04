from pkg_resources import resource_string, resource_listdir
import json
import os

from ..conversations import EmailCorpus

def load_data_raw(mailinglist_name, n=-1):
    x = resource_string(__name__, mailinglist_name+'/all.json')
    json_list = json.loads(x)
    return json_list[:n]


def load_data_as_EmailCorpus(mailinglist_name, n=-1):
    json_data = load_data_raw(mailinglist_name)
    
    conversations = [(subj_str, mail_ls) for period, subj_d in json_data.items() 
                for subj_str, mail_ls in subj_d.items()][:n]
    
    return EmailCorpus.from_email_dicts(conversations)
    
def get_mailinglist_list():
    return resource_listdir("conversationkg", "sample_data")