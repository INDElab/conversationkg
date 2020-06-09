# -*- coding: utf-8 -*-

import os
import pickle
from tqdm import tqdm

import http.client

import multiprocessing as mp

import numpy as np

top_dir = "collected/"
subject_lists_dir = top_dir + "subject_lists/"
save_dir = top_dir + "raw_email_pages_2/"




continuing = True


if not continuing:
    os.makedirs(save_dir)


def load_lists():
    with open(top_dir+"periods.pkl", "rb") as handle:
        periods = pickle.load(handle)
    
    links = {}
    for f in os.listdir(subject_lists_dir):
        if f == "log":
            continue
        with open(subject_lists_dir + f, "rb") as handle:
            subjects = pickle.load(handle)
            links[f.replace(".pkl", "")] = subjects
    return periods, links


def get_urls(periods, links):
    with_urls = [(listname, list(zip(periods[listname], lists_per_period)))
                for listname, lists_per_period in links.items()]
    with_urls_permuted = [with_urls[i] for i in 
                          np.random.permutation(len(with_urls))]
    return with_urls_permuted





def remove_finished(save_dir, url_list):
    not_done = []
    for listname, period_ls in url_list:
        if not os.path.isdir(f"{save_dir}{listname}"):
            not_done.append((listname, period_ls))
        else:
            if not os.path.isfile(f"{save_dir}{listname}/done"):
                period_shortlist = [(period, period_ls) 
                    for period, period_ls in period_ls 
                    if not os.path.isdir(f"{save_dir}{listname}/{period}/")]
                
                if period_shortlist:
                    not_done.append((listname, period_shortlist))
    return not_done


##############################################################################

with_urls_permuted = get_urls(*load_lists())


if continuing: 
    with_urls_permuted = remove_finished(save_dir, with_urls_permuted)



processes = 4

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
        
    conn = http.client.HTTPSConnection("lists.w3.org", port=443)
    
    
    for listname, period_ls in chunk:                       
        n = 0
        this_pbar.set_description(f"{position}: {listname}")
        
        if not period_ls:
            os.makedirs(f"{save_dir}{listname}")
            period_ls = []


        for period, subject_ls in period_ls:
            this_pbar.update(1)

            if not subject_ls:
                os.makedirs(f"{save_dir}{listname}/{period}/")
                subject_ls = []

            for subject, link_ls in subject_ls:
                dir_prefix = f"{save_dir}{listname}/{period}/"
                dir_name = subject if subject else "NO_SUBJECT"                        
                cur_path = create_dir(dir_prefix, dir_name)

                if not link_ls:
                    link_ls = []
                
                for link in link_ls:                    
                    url = f"/Archives/Public/{listname}/{period}/{link}"
                    
                    try:                        
                        conn.request("GET", url)
                        response = conn.getresponse()
                        body = response.read()
                    except http.client.IncompleteRead as e:
                        body = e.partial
                    except http.client.HTTPException as e:
                        conn = http.client.HTTPSConnection("lists.w3.org", port=443)
                        conn.request("GET", url)
                        response = conn.getresponse()
                        body = response.read()
                            
                    with open(cur_path+link, "wb") as handle:  
                        handle.write(body)
                    n += 1
                        
        with open(f"{save_dir}{listname}/done", "w") as handle:
            handle.write(str(n))
                                                


with mp.Pool(4) as pool:
    pool.map(download, zipped)