# -*- coding: utf-8 -*-

import json
from tqdm import tqdm

import http.client
from bs4 import BeautifulSoup


def collect_mailinglists(html):
    soup = BeautifulSoup(html, 'lxml')
    return [anchor.a.text.strip() for anchor in tqdm(soup.find_all('dt'))]
        

if __name__ == "__main__":
    top = "lists.w3.org"
    
    d  = "/Archives/Public/"
    
    
    conn = http.client.HTTPSConnection(top, port=443)
    
    conn.request("GET", d)
    
    response = conn.getresponse()
    
    listnames = collect_mailinglists(response.read())
    
    
    print(len(listnames))
    
    with open("collected/mailinglists.json", "w") as handle:
        json.dump(listnames, handle)