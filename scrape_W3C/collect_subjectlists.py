# -*- coding: utf-8 -*-

import pickle
from tqdm.auto import tqdm

import http.client
from bs4 import BeautifulSoup
import re

def easy_get_ul(soup):
    first_subj = soup.find(id="first").find_parent("li")
    if not first_subj:
        raise ValueError("div found but id=first not found!")
    return first_subj.find_parent("ul")
#    return [s for s in first_subj.find_parent("ul")("li", recursive=False)]


message_re = re.compile(r"[0-9][0-9][0-9][0-9]\.html")

def structural_get_ul(soup):
    for ul in soup.find_all("ul"):
        a_s = [[li.find("a", href=message_re) for li in sub_ul("li")] for sub_ul in ul("ul")]
        if a_s and all(a_s):
            return ul
            
#            for subj in ul.find_all("li", recursive=False):
#                subjs.append(subj.dfn.text)
#                print("Subject:\t", subj.dfn.text)
#                print("\n")
#            print("--------------------------")


def process_ul(ul):
    return ul

def process_ul2(ul):
    
    for li in ul.find_all("li", recursive=False):
        if li.dfn:
            subject_title = li.dfn.text
            print("TITLE: ", subject_title)
            
        for inner_li in li.ul.find_all("li"):
            print(inner_li.a.get("href"))
        
        print("\n-------\n")

def extract_subject_list(html):
    soup = BeautifulSoup(html, "lxml")
    
    if soup.find("div", class_="messages-list"):
        subj_ul = easy_get_ul(soup)
#        print("easy")
    else:
        subj_ul = structural_get_ul(soup)
#        print("structural")
        
    if not subj_ul:
        raise ValueError("no unordered list of subjects found")

    return process_ul(subj_ul)
        
            
        
            
        


if __name__ == "__main__":
    top = "lists.w3.org"
    
    d  = "/Archives/Public/"    
    
    with open("collected/periods.pkl", "rb") as handle:
        periods = pickle.load(handle)
    
    
    conn = http.client.HTTPSConnection(top, port=443)
    
    collected = {}
    
    for listname, period_ls in tqdm(list(periods.items())):
        subjects = []
        for period in tqdm(period_ls, desc=listname):
#            print(d+listname+"/"+period+"/subject.html")
            try:
                conn.request("GET", d+listname+"/"+period+"/subject.html")
                response = conn.getresponse()
            except http.client.RemoteDisconnected:
                conn.close()
                print("RECONNECTING")
                conn = http.client.HTTPSConnection(top, port=443)
                conn.request("GET", d+listname+"/"+period+"/subject.html")
                response = conn.getresponse()
            
            ul = extract_subject_list(response.read())
                
            subjects.append(ul.prettify())

        collected[listname] = subjects
    
    print(collected)
    
    with open("collected/raw_subject_uls.pkl", "wb") as handle:
        pickle.dump(collected, handle)
        
        
        
        
        
        
        
        
        
        
        
        
        
