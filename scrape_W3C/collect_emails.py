# -*- coding: utf-8 -*-

import os
import pickle
from tqdm import tqdm
import logging

import http.client
from bs4 import BeautifulSoup

import multiprocessing as mp

import numpy as np

top_dir = "collected/"
subject_lists_dir = top_dir + "subject_lists/"
save_dir = top_dir + "raw_email_pages/"
os.makedirs(save_dir)

logging.basicConfig(filename=save_dir+'log', filemode='w',
                    format='[%(asctime)s]: %(suburl)s: %(funcName)s: %(message)s', 
                    datefmt='%d-%m-%Y %I:%M:%S',
                    level=logging.INFO)


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

#pbar = tqdm(total=sum(len(periods) for _, periods in with_urls)//processes)

#pbar = tqdm(total=len([p for pls in periods.values() for p in pls]))
#pbar = tqdm(total=len(with_urls)//processes)

print(f"INFO: Load per process {totals}")

zipped = list(zip(chunks, totals, range(1, processes+1)))

def download(tup):
    chunk, total, position = tup
    this_pbar = tqdm(total=total, position=position, leave=True)
    
    conn = http.client.HTTPSConnection("lists.w3.org", port=443)
    
    for listname, period_ls in chunk:
        this_pbar.set_description(f"{position}: {listname}")

        for period, subject_ls in period_ls:
            this_pbar.update(1)

            for subject, link_ls in subject_ls:
                if not link_ls:
                    print(f"INFO: no links in {listname}/{period}/{subject}")
                    
                for link in link_ls:
                    url = f"/Archives/Public/{listname}/{period}/{link}"
                    try:                        
                        conn.request("GET", url)
                        response = conn.getresponse()
                    except http.client.RemoteDisconnected:
                        print(f"INFO: restarting connection at {url}")
                        conn = http.client.HTTPSConnection("lists.w3.org", port=443)
                        conn.request("GET", url)
                        response = conn.getresponse()
    
                    subject_str = subject if subject else "NO_SUBJECT"
                                                    
                    cur_dir = f"{save_dir}{listname}/{period}/{subject_str}/"
                        
                    if not os.path.isdir(cur_dir):
                        try:
                            os.makedirs(cur_dir)
                        except OSError:
                            long_dir = cur_dir
                            cur_dir = cur_dir[:100] + " [...] " + cur_dir[-100:]
                            os.makedirs(cur_dir)
                            with open(cur_dir+"long name", "w") as handle:
                                handle.write(long_dir)
                            
                    with open(cur_dir+link, "wb") as handle:  
                        handle.write(response.read())
                                                
#                            soup_str = BeautifulSoup(response.read(),
#                                                     "lxml").prettify()#(encoding="utf-8")
#                            handle.write(soup_str)
                    



with mp.Pool(4) as pool:
    pool.map(download, zipped)
            
    