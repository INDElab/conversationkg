# -*- coding: utf-8 -*-

import os
import pickle
from tqdm import tqdm
import logging
from time import strftime

import http.client
from bs4 import BeautifulSoup

import multiprocessing as mp

import numpy as np

top_dir = "collected/"
subject_lists_dir = top_dir + "subject_lists/"
save_dir = top_dir + "raw_email_pages/"
os.makedirs(save_dir)


#def log(handle, message_tup):
#    suburl, message = message_tup
#    handle.write(strftime('%d-%m-%Y %I:%M:%S'))
#    handle.write(f": {suburl}: {message}")
#    handle.write("\n")


with open(top_dir+"periods.pkl", "rb") as handle:
    periods = pickle.load(handle)
        
        
links = {}
for f in os.listdir(subject_lists_dir):
    if f == "log":
        continue
    with open(subject_lists_dir + f, "rb") as handle:
        subjects = pickle.load(handle)
        links[f.replace(".pkl", "")] = subjects

print("INFO: Collected periods and subject lists loaded")


processes = 4

with_urls = [(listname, list(zip(periods[listname], lists_per_period)))
            for listname, lists_per_period in links.items()]

with_urls_permuted = [with_urls[i] for i in np.random.permutation(len(with_urls))]

chunks = [with_urls_permuted[i::processes] for i in range(processes)]


totals = [sum(len(periods) for _, periods in chunk) for chunk in chunks]

zipped = list(zip(chunks, totals, range(1, processes+1)))

print(f"INFO: Load per process {totals}")


def create_dir(prefix, name):
    name_hash = str(hash(name)) + "/"
    
    if not os.path.isdir(prefix+name_hash):
        os.makedirs(prefix + name_hash)
        
    with open(prefix + name_hash + "name", "w") as handle:
        handle.write(name)
        
    return prefix + name_hash
        

def download(tup):
    chunk, total, position = tup
    this_pbar = tqdm(total=total, position=position, leave=True)
    
#    log_file = open(f"{save_dir}log_{position}", "w")
    
    conn = http.client.HTTPSConnection("lists.w3.org", port=443)
    
    
    for listname, period_ls in chunk:
        n = 0
        this_pbar.set_description(f"{position}: {listname}")

        for period, subject_ls in period_ls:
            this_pbar.update(1)

            if not subject_ls:
#                log(log_file, (f"{listname}/{period}", "no subjects"))
                os.makedirs(f"{save_dir}{listname}/{period}/")
                continue

            for subject, link_ls in subject_ls:
                if not link_ls:
#                    log(log_file, (f"{listname}/{period}/{subject}", "no links"))
                    dir_name = subject if subject else "NO_SUBJECT"
                    create_dir(f"{save_dir}{listname}/{period}/", dir_name)
                    continue    
                
                for link in link_ls:
                    url = f"/Archives/Public/{listname}/{period}/{link}"
                    try:                        
                        conn.request("GET", url)
                        response = conn.getresponse()
                    except http.client.RemoteDisconnected:
                        print(f"\nINFO: restarting connection at {url}")
                        conn = http.client.HTTPSConnection("lists.w3.org", port=443)
                        conn.request("GET", url)
                        response = conn.getresponse()
                                                    
                    dir_prefix = f"{save_dir}{listname}/{period}/"
                    dir_name = subject if subject else "NO_SUBJECT"
                        
                    cur_path = create_dir(dir_prefix, dir_name)

                            
                    with open(cur_path+link, "wb") as handle:  
                        handle.write(response.read())
                    n += 1
                        
        with open(f"{save_dir}{listname}/done", "w") as handle:
            handle.write(str(n))
                                                


with mp.Pool(4) as pool:
    pool.map(download, zipped)
    
    
    
    
    
    
    
    
    
    
    
    
# OBSOLETE
    
    
    
#logging.basicConfig(filename=save_dir+'log', filemode='w',
#                    format='[%(asctime)s]: %(suburl)s: %(message)s', 
#                    datefmt='%d-%m-%Y %I:%M:%S',
#                    level=logging.INFO)

#                    if not os.path.isdir(cur_dir):
#                        try:
#                            os.makedirs(cur_dir)
#                        except OSError:
#                            long_dir = cur_dir
#                            cur_dir = cur_dir[:100] + " [...] " + cur_dir[-100:]
#                            os.makedirs(cur_dir)
#                            with open(cur_dir+"long name", "w") as handle:
#                                handle.write(long_dir)            
    
    
#                            soup_str = BeautifulSoup(response.read(),
#                                                     "lxml").prettify()#(encoding="utf-8")
#                            handle.write(soup_str)