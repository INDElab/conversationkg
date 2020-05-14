# -*- coding: utf-8 -*-
import pickle
from tqdm.auto import tqdm

import http.client
from bs4 import BeautifulSoup


def collect_mailinglists(html):
    soup = BeautifulSoup(html, 'lxml')
    return [anchor.a.text.strip() for anchor in soup.find_all('dt')]
        

if __name__ == "__main__":
    top = "lists.w3.org"
    
    d  = "/Archives/Public/"
    
    
    conn = http.client.HTTPSConnection(top, port=443)
    
    conn.request("GET", d)
    
    response = conn.getresponse()
    
    listnames = collect_mailinglists(response.read())
    
    
    print(len(listnames))
    
    with open("collected/mailinglists.pkl", "wb") as handle:
        pickle.dump(listnames, handle)