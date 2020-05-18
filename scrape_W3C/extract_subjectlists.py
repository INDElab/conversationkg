# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import os
import pickle
from tqdm.auto import tqdm
import logging

top_dir = "collected/"
raw_page_dir = top_dir + "raw_subject_pages/"
save_dir = top_dir + "subject_lists/"
os.makedirs(save_dir)

logging.basicConfig(filename=save_dir+'log', filemode='w',
                    format='[%(asctime)s]: %(suburl)s: %(funcName)s: %(message)s', 
                    datefmt='%d-%m-%Y %I:%M:%S',
                    level=logging.INFO)


def easy_get_ul(soup):
    first_subj = soup.find(id="first").find_parent("li")
#    if not first_subj:
#        raise ValueError("div found but id=first not found!")
    return first_subj.find_parent("ul")


message_re = re.compile(r"[0-9][0-9][0-9][0-9]\.html")
def structural_get_ul(soup):
    for ul in soup.find_all("ul"):
        a_s = [[li.find("a", href=message_re) for li in sub_ul("li")] 
                for sub_ul in ul("ul")]
        if a_s and all(a_s):
            return ul
#    raise ValueError("No ul with the structural criterion found!")
    return None


def process_ul(ul, suburl=""):
        for i, li in enumerate(ul.find_all("li", recursive=False)):
            if not li.ul:
                if li.find("a", href=message_re):
                    logging.info(f"<li> {i} has no <ul>", 
                                 extra={"suburl": suburl})
                    subject_title = None
                    yield subject_title, [li.a.get("href")]
                else:                    
                    logging.info(f"<li> {i} contains no email links", 
                                 extra={"suburl": suburl})
                    yield None, None
                continue                    
            
             
            if li.dfn:
                subject_title = li.dfn.text
            elif li.strong:
                subject_title = li.strong.text
            else:
                logging.info(f"<li> {i} has no subject title", 
                                 extra={"suburl": suburl})
                subject_title = None
                
            links = [inner_li.a.get("href") for inner_li in li.ul.find_all("li")]
            yield subject_title, links
        

def extract_subject_list(html, suburl=""):
    soup = BeautifulSoup(html, "lxml")
    
    if soup.find("div", class_="messages-list"):
        subj_ul = easy_get_ul(soup)
    else:
        subj_ul = structural_get_ul(soup)
        
    if not subj_ul:
        logging.info("no <ul> with subjects found", 
                     extra={"suburl": suburl})
        return None
#        print(html)
#        raise ValueError("no unordered list of subjects found")
    return list(process_ul(subj_ul, suburl=suburl))



if __name__ == "__main__":
    print("Context: Extraction Started")
    
    with open(top_dir+"periods.pkl", "rb") as handle:
        periods = pickle.load(handle)
    
    loaded = {}
    for f in os.listdir(raw_page_dir):
        with open(raw_page_dir + f, "rb") as handle:
            page_ls = pickle.load(handle)
            loaded[f.replace(".pkl", "")] = page_ls
                    
    print("Context: Collected pages loaded")
    
      
    for listname, page_ls in tqdm(loaded.items()):
        extracted_subjects = []
        for period, page in zip(periods[listname], page_ls):
            current_subjects = extract_subject_list(page, 
                                    suburl=listname+"/"+period+"/subject.html")
            extracted_subjects.append(current_subjects)
        
        with open(save_dir+listname+".pkl", "wb") as handle:
            pickle.dump(extracted_subjects, handle)
            
        
            