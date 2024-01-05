import os
import sys
import pymongo as pmg
import json
import bson

current_dir = os.path.dirname(os.path.abspath(__file__))  
module_dir = os.path.abspath(os.path.join(current_dir, '..', 'modules'))  
sys.path.insert(0, module_dir) 

import gamesets

class CtrlInfo:
    _statusCode_creation = 403
    collection = None
    
    #obj_gamesets: gamesets.Gamesets
    def __init__(self, url: str, collection: str):
        # url example: 'mongodb://localhost:2717/'
        self.client = pmg.MongoClient(url)
        self.db = self.client.mydatabase
        
        totalCollections = self.db.list_collection_names()
        if totalCollections == []:
            self.collection = self.db.myFirstCollection
            self._statusCode_creation = 200
        else:
            for collections in totalCollections:
                if collection == collections:
                    self.collection = self.db[collection]
                    self._statusCode_creation = 200
                    break
                else:
                    self.client.close()
    
    
    def reset_cursor(self) -> list:
        return self.collection.find()
    
    
    def printalldocs(self) -> list:
        all_in_list = []
        reset = self.reset_cursor()
        for doc in reset:
            doc = self.convert_to_json_serializable(doc)
            formatted_json = json.dumps(doc, indent=4)
            all_in_list.append(formatted_json)
        return all_in_list
     
    def convert_to_json_serializable(self, obj: dict) -> str:
        '''
        Método usado para visualizar em formato json as informações 
        do banco de dados.
        '''
        for key, value in obj.items():
            if isinstance(value, bson.objectid.ObjectId):
                obj[key] = str(value)
        return obj
        
                             
    def send_to_nosql(self, obj: dict):
        _id = self.collection.insert_one(obj)
        return _id.inserted_id
    
    def close_connection(self):
        self.client.close()
   
  
        
        
    
    