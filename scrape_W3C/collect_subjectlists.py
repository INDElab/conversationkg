# -*- coding: utf-8 -*-

import json
import pickle
from tqdm.auto import tqdm

import http.client
import os
            

if __name__ == "__main__":
    top = "lists.w3.org"
    
    d  = "/Archives/Public/"    
    
    with open("collected/periods.json", "rb") as handle:
        periods = json.load(handle)
    
    
    conn = http.client.HTTPSConnection(top, port=443)
    
    collected = {}
    
    save_dir = "collected/raw_subject_pages/"
    os.makedirs(save_dir)
    
    for listname, period_ls in tqdm(list(periods.items())):
        pages = []
        for period in tqdm(period_ls, desc=listname):
            try:
                conn.request("GET", d+listname+"/"+period+"/subject.html")
                response = conn.getresponse()
            except http.client.RemoteDisconnected:
                conn.close()
                print("RECONNECTING")
                conn = http.client.HTTPSConnection(top, port=443)
                conn.request("GET", d+listname+"/"+period+"/subject.html")
                response = conn.getresponse()
                
            pages.append(response.read())

        collected[listname] = pages
        
        with open(save_dir + listname + ".pkl", "wb") as handle:
            pickle.dump(pages, handle)
    
    print(len(collected))