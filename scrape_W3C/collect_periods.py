# -*- coding: utf-8 -*-

import pickle
from tqdm.auto import tqdm

import http.client
from bs4 import BeautifulSoup
import re

def collect_periods(html):
    soup = BeautifulSoup(html, 'lxml')
    return [anchor.a.text.strip() for anchor in soup.find_all('dt')]

def collect_periods_directly(html):
    soup = BeautifulSoup(html, "lxml")
    subject_re = re.compile(r"[0-9][0-9][0-9][0-9].*/subject\.html")        
    return [anchor.get("href").split("/")[0] for anchor in soup.find_all("a", href=subject_re)]


if __name__ == "__main__":
    top = "lists.w3.org"
    
    d  = "/Archives/Public/"
    
    
    with open("collected/mailinglists.pkl", "rb") as handle:
        listnames = pickle.load(handle)
    
    
    conn = http.client.HTTPSConnection(top, port=443)
    
    periods = {}
    
    for name in tqdm(listnames):
        try:
            conn.request("GET", d+name+"/")
            response = conn.getresponse()

        except http.client.RemoteDisconnected:
            conn.close()
            conn = http.client.HTTPSConnection(top, port=443)
            conn.request("GET", d+name+"/")
            response = conn.getresponse()
    
        cur_periods = collect_periods_directly(response.read())
        cur_periods = [p for p in cur_periods if p]
        periods[name] = cur_periods
    
    with open("collected/periods.pkl", "wb") as handle:
        pickle.dump(periods, handle)