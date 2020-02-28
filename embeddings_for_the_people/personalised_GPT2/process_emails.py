# -*- coding: utf-8 -*-


import pickle
#import os
from datetime import datetime
#from tqdm import tqdm
import re
#import numpy as np
#from collections import Counter

#import html
import email.utils as mailutil

from dateutil.parser import parse as du_parse
#import datetime
from datetime import timedelta

from urllib.parse import urlparse




# PATTERNS
header_pattern = re.compile(r"([a-z]+)=([\w\W]+)")
to_pattern = re.compile(r"[tT][oO]:([\w\W]+)")
cc_pattern = re.compile(r"[cC][cC]:([\w\W]+)")

email_address_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
url_pattern = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


# HELPER FUNCTIONS
def extract_meta(mail):
    d = {}
    mail_content = []
    for i, line in enumerate(mail):
        match_or_none = header_pattern.match(line)
        if match_or_none and i <= 11:
            k, v = match_or_none.groups()
            d[k.lower()] = v
        elif to_pattern.match(line):
            d["to"] = mailutil.parseaddr(line)
        elif cc_pattern.match(line):
            d["cc"] = mailutil.parseaddr(line)
        else:
            mail_content.append(line)
    mail_content = "".join(mail_content)
    return d, mail_content


def prep_line(s):
    return s.strip().strip("\"").strip('\'')

def process_time_sent(s):
    dt = du_parse(s)
    
    if not dt.tzinfo:
            raise ValueError("No timezone information in parse!", s)
            dt = dt.replace(tzinfo=datetime.timezone.utc)
    if dt.tzinfo.utcoffset(dt) > timedelta(hours=24) or\
            dt.tzinfo.utcoffset(dt) < -timedelta(hours=24):
        print("Timezone outside of 24 hours: ", dt.tzinfo.utcoffset(dt))
        raise ValueError("Timezone outside of 24 hours: ", dt.tzinfo.utcoffset(dt))
    return dt
    
    
def parse_header(d):
    d = {k: prep_line(v) if type(v) is str else v for k, v in d.items()}
    new_d = {}
    try:
        new_d["sent"] = process_time_sent(d["sent"])
        new_d["id"] = d["id"]
        new_d["name"] = d["name"]
        new_d["email"] = mailutil.parseaddr(d["email"])[1]
        new_d["subject"] = d["subject"]
        new_d["inreplyto"] = d["inreplyto"] if "inreplyto" in d else None
        new_d["to"] = d["to"]
        new_d["cc"] = d["cc"] if "cc" in d else None
        return new_d
    except Exception as e:
        parse_header.errors.append(e)
        return None     
parse_header.errors=[]



def group_into_convos(emails_temp_sorted):
    convos = []
    ids = {}

    i = 0   
    id_not_found = []  

    for mail in emails_temp_sorted:
        if mail.inreplyto is None or mail.inreplyto not in ids:
            convos.append([mail])
            ids[mail.id] = i # need to check if ID actually exists! ->  runs fine without (weird?)
            i += 1
                
            if mail.inreplyto not in ids:
                id_not_found.append(mail)
                    
        else:
            convos[ids[mail.inreplyto]].append(mail)
            ids[mail.id] = ids[mail.inreplyto] # again check
            
    return convos