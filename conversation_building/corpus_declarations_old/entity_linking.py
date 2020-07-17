# -*- coding: utf-8 -*-

import http
from urllib.parse import urlencode, quote_plus
import json

from corpus_declarations.entities import EntityInstance

from tqdm import tqdm

class APIError(Exception):
    def __init__(self, status, response):
        self.status = status
        self.received_response = response

    def __str__(self):
        return f"APIError: {self.status}"        


class EntityLinker:
    def __init__(self):
        self.api_base = "opentapioca.org"
        self.api_endpoint = "/api/annotate"
        self.headers = {'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*',
                   'Connection': 'keep-alive', 'Content-Length': None,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 
                   "X-Requested-With": "XMLHttpRequest"}
        
        self.body = b"query=None"
        
        self.params = {"query": None}
        
        self.connection = http.client.HTTPSConnection(self.api_base, port=443)


    def entities_from_text(self, text):
        self.body = b"query=" + text.encode("utf-8")
        
        self.params["query"] = text
        body = urlencode(self.params, quote_via=quote_plus).replace("-", "%2D").replace("-", "%2E")
        self.headers["Content-Length"] = len(body)

    
        try:
            self.connection.request("POST", self.api_endpoint, 
                                body, self.headers)
            response = self.connection.getresponse()
        except http.client.RemoteDisconnected as err:
            print("CONNECTION RESET!")
            self.connection = http.client.HTTPSConnection(self.api_base, port=443)
            self.connection.request("POST", self.api_endpoint, 
                                body, self.headers)
            response = self.connection.getresponse()


        if response.status != 200:
            raise APIError(f"HTTP status not 200 (is {response.status})",
                           response)
        try:
            result = json.loads(response.read())
        except json.JSONDecodeError as err:
            print("DECODE ERROR!")
        
        if result["text"] != text:
            raise APIError("Echoed text not equal original text (is {result['text']})",
                           response)
        
        return tuple(EntityInstance.from_tapioca_api(text, ent_dict) for ent_dict in result["annotations"])


    def to_WikiData_entities(self, entities):
        for entity in tqdm(entities, desc="Linking entities"):
            if not entity.instance_label:
                continue
            
            recognised = self.entities_from_text(entity.instance_label)
            
            if len(recognised) == 1:# and recognised[0].instance_label == entity.instance_label:
                recognised = recognised[0]
                print(recognised)
                entity.entity = recognised.entity

                entity.instance_score = recognised.instance_score
                entity.score = recognised.score
                entity.page_rank = recognised.page_rank
                entity.alternative_entities = recognised.alternative_entities
#                
#            else:
#                entity.entity = "NOT RECOGNISED"



    def enrich_email_bodies(self, corpus):
        for e in tqdm(corpus.iter_emails(), desc="Enriching email bodies"):
            found_entities = self.entities_from_text(e.body)
            e.body.entities = found_entities
