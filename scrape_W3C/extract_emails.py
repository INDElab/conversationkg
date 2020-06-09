# -*- coding: utf-8 -*-

import os
from tqdm import tqdm

import multiprocessing as mp
import numpy as np

import html
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import UnicodeDammit
import cchardet

import json
import pickle


d = "collected/raw_email_pages_new/"
extraction_d = "collected/emails3/"

total = 1876156

processes = 4


#%%##############################################################

mappings = []
with open(d + "mapping", encoding="utf-8") as handle:
    for line in tqdm(handle, total=total):
        filename_hash, pathname = line.strip().split(": ", 1)    
        *path, suffix = pathname.split("/", 4)
        path = path[2:]
        subj, filename = suffix.rsplit("/", 1)
        mappings.append((filename_hash, (*path, subj, filename)))
        
print(mappings[0])


#short_mappings = mappings[:7000]



#%%#####################################


grouped_by_ls = {}

for filename_hash, (ls, period, subj, filename) in mappings:
    if not ls in grouped_by_ls:
        grouped_by_ls[ls] = []
    grouped_by_ls[ls].append((filename_hash, (ls, period, subj, filename)))
    

#%%#####################################

def extract_encoding_from_html(html):
    if not type(html) is bytes:
        print("Input was already string which is unicode in Python 3!")
        return "unicode"
    first_line = html[:html.find(b"\n")]
    if not first_line.startswith(b"<?xml") and first_line.endswith(b"?>"):
        print("No encoding explicitly declared!")
        return None
    start = first_line.find(b'encoding="') + len(b'encoding="')
    end = first_line.rfind(b'"?>')
    return first_line[start:end].lower() # decode("utf-8").lower()

def determine_encoding(html):
    return extract_encoding_from_html(html)


#def determine_encoding(html):
#    reported = extract_encoding_from_html(html)
#    
#    UD_sniffed = UnicodeDammit(html).original_encoding.lower().encode()
#    
#    cchardet_sniffed = cchardet.detect(html)["encoding"].lower().encode()
#    
#    print(reported, UD_sniffed, cchardet_sniffed)
#    
#    
#    if UD_sniffed == cchardet_sniffed:
#        if reported == UD_sniffed:
#            return reported
#        else:
#            return UD_sniffed
#    else:
#        return reported
#    

#%%##############################################################



def get_meta_from_comments(soup):
    comments = soup.find_all(string=lambda t: isinstance(t, Comment))
    keys = ("isoreceived", "isosent", "sent", "name", "email", "subject", "id", "charset", "inreplyto", "charset")
    
    d = dict(l.strip().split("=", 1) for l in comments)
    return {k: (html.parser.unescape(d[k].strip('"')) if k in d else None) 
                for k in keys}
    
    
def get_meta_from_meta( soup):       
    author = soup.find("meta", {"name": "Author"}).get("content")
    subject = soup.find("meta", {"name": "Subject"}).get("content")
    date = soup.find("meta", {"name": "Date"}).get("content")
    return {"author": author, "subject_from_meta": subject,
            "date": date}


def safe_split(tag_or_none, split_by):
    try:
        str_ls = tag_or_none.text.strip().split(split_by)
        try:
            return str_ls[1].strip()
        except IndexError:
            return 
            print("\n"*5, tag_or_none, "\n"*5)
            raise
    except AttributeError:
        return None
        

def get_meta_from_body(soup):
    address = soup.find("address")
    
    try:
        from_ = safe_split(address.find(id="from"), "From:")
        date = safe_split(address.find(id="date"), "Date:")
        to = safe_split(address.find(id="to"), "To:")
        id_ = safe_split(address.find(id="message_id"), "Message-ID:")
    except IndexError:
        print(soup, "\n"*5)
        raise
        
    return {"from": from_, "date_from_body": date,
            "to": to, "id_from_body": id_}
    
    
def get_email_body(path, soup):
    return soup.find("pre", id="body").text


#def stash(e_dict, path, big_d):
#    mail_ls, period, subject, _ = path
#    
#    if not mail_ls in big_d:
#        big_d[mail_ls] = {}
#    
#    if not period in big_d[mail_ls]:
#        big_d[mail_ls][period] = {}
#    
#    if not subject in big_d[mail_ls][period]:
#        big_d[mail_ls][period][subject] = []
#    
#    big_d[mail_ls][period][subject].append(e_dict)


def stash(mail_dict, path, maills_dict):
    mail_ls, period, subject, _ = path
    
    if not period in maills_dict:
        maills_dict[period] = {}
        
    if not subject in maills_dict[period]:
        maills_dict[period][subject] = []
        
    maills_dict[period][subject].append(mail_dict)


def load_and_extract(tup):
    chunk, position = tup
    progressbar = tqdm(chunk, total=len(chunk),
                       position=position, desc=str(position))
    
    
    couldnt_extract = []
    for lsname, mail_ls in progressbar:
        progressbar.set_description(f"{position}: {lsname} ({len(mail_ls)})")
        maillist_dict = {}
        for fname, path in mail_ls:            
            with open(d + fname, "rb") as handle:
                html_bytes = handle.read()
            
            determined_encoding = determine_encoding(html_bytes)
            try:
                soup = BeautifulSoup(html_bytes, "lxml", 
                                     from_encoding=determined_encoding)
            except Exception:
                couldnt_extract.append(path)
                continue
    
            try:
                email_dict = {"body": get_email_body(path, soup)}
                email_dict.update(get_meta_from_meta(soup))
                email_dict.update(get_meta_from_comments(soup))
                email_dict.update(get_meta_from_body(soup))
                email_dict["original_path"] = path
                stash(email_dict, path, maillist_dict)
            except AttributeError as e:
                couldnt_extract.append(path)
        
        
        os.makedirs(extraction_d + lsname)    
        
        with open(extraction_d + lsname + "/all.json", "w", encoding="utf-8") as handle:
            json.dump(maillist_dict, handle, ensure_ascii=False)
    return couldnt_extract    


#%%##############################################################
  
randomised = np.random.permutation(list(grouped_by_ls.items()))
chunks = [randomised[i::processes] for i in range(processes)]
zipped = list(zip(chunks, range(1, processes+1)))
            
print("\nextracting...")

lens = [sum(len(tup[1]) for tup in chunk) for chunk in chunks]
print(f"loads: {tuple(lens)}")
with mp.Pool(processes) as pool:
    results = pool.map(load_and_extract, zipped)
    

not_extracted = [path for chunk in results for path in chunk]

print("\n\nextraction done\n")
print(len(not_extracted))        

with open(extraction_d + "not_extracted.pkl", "wb") as handle:
    pickle.dump(not_extracted, handle)


#%%################################################################

#for lsname, ls_d in extracted.items():
#    os.makedirs(extraction_d + lsname)    
#        
#    with open(extraction_d + lsname + "/all.json", "w", encoding="utf-8") as handle:
#        json.dump(ls_d, handle, ensure_ascii=False)
    
    



#def return_list(tup):
#    chunk, position = tup
#    
#    progressbar = tqdm(chunk, total=len(chunk),#total//processes,
#                       position=position, desc=str(position))
#    
#    results = []
#    for x in progressbar:
#        results.append(x**2)
#        
#    return results
#
#
#procs = 4
#
#ls = list(range(100))
#chunks = [ls[i::procs] for i in range(procs)]
#zipped = list(zip(chunks, range(1, procs+1)))
#
#with mp.Pool(procs) as pool:
#    chunks_processed = pool.map(return_list, zipped)
#    
#    
#print(chunks_processed)
