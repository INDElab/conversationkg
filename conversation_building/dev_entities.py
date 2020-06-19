# -*- coding: utf-8 -*-

import requests
import json

#
#base_url = "http://api.dbpedia-spotlight.org/en/annotate"
#
#params = {"text": "My name is Sundar. I am currently doing Master's in Artificial Intelligence at NUS. I love Natural Language Processing.", "confidence": 0.35}
#
#
## Response content type
#headers = {'accept': 'text/html'}
#
## GET Request
#res = requests.get(base_url, params=params, headers=headers)
#if res.status_code != 200:
#    # Something went wrong
#    raise APIError(res.status_code)
## Display the result as HTML in Jupyter Notebook
#display(HTML(res.text))





#%%


base_url = "https://opentapioca.org/api/annotate"


headers = {"accept": "text/html"}

params = {"query": "Associated Press writer Julie Pace contributed from Washington."}


params = {"query": "Washington is the capitol of the U.S.."}

res = requests.get(base_url, params=params, headers=headers)

results = json.loads(res.text)#["annotations"]

#%%

class APIError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"APIError: {self.status}"        



class Annotator:
    def __init__(self):
        self.base_url = "https://opentapioca.org/api/annotate"
        self.headers = {"accept": "text/html"}
        
    def annotate(self, text):
        response = requests.get(self.base_url, params={"query":text}, 
                                headers=self.headers)
        
        if response.status_code != 200:
            raise APIError(f"HTTP status not 200 (is {response.status_code})")
        
        result = json.loads(response.text)
        
        if result["text"] != text:
            raise APIError("Echoed text not equal original text (is {result['text']})")
            
            
        return tuple(Annotation(a, text) for a in result["annotations"])
    
    
class Annotation:
    def __init__(self, annotation_dict, text):
        self.log_likelihood = annotation_dict["log_likelihood"]
        self.best_qid = annotation_dict["best_qid"]
        self.start, self.end = annotation_dict["start"], annotation_dict["end"]
        self.term = text[self.start:self.end]
        
    def __repr__(self):
        return f"{self.term} ({self.best_qid}, {self.log_likelihood:2.3f})"
    
    def __str__(self):
        return repr(self)
        
        
        
        
#%%
        
for d in results["annotations"]:
    print(d["best_qid"], d["log_likelihood"])
    print([(t["label"], t["id"], t["score"], t["rank"]) for t in d["tags"]])
    print()



