# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 01:25:13 2021

@author: Pozitrino
"""


import pandas as pd
from pymongo import cursor
from pymongo import MongoClient
import re

import gridfs
import json
import os
import zipfile
from bson import BSON
from utils.LocalUtils import LocalUtil




class DataframeHandler:
    
  
  
        
  def dataframe(mongo_cursor : cursor):
        i=0
        leaf  = []
        json_dict = []
        for cur in mongo_cursor:
            json_dict.append(cur)

        
        while i<len(json_dict):
            atr_list = []
            for x in json_dict[i]["metadata"]: 
                
                atr_list = atr_list + [json_dict[i]["metadata"][x]]
            
            leaf = leaf + [atr_list[:-1]]
            i = i+1
        df = pd.DataFrame (leaf,columns=['ID','Name','Description','Authors','Measurement','Technology type','Factor','Date','Sample rate','License'])
        return df
    
    
    
class DatabaseHandler:
    
    def __init__(self):    
        self.db = MongoClient("mongodb+srv://test:test@signals.xn9ot.mongodb.net/myFirstDatabase?retryWrites=true&w=majority").Signal_database
        
        

    def save_to_database(self,json_dict:dict):        
        self.db.signal.insert_one(json_dict)
    
    def load_from_database(self,x,y):
        if x == "metadata.id" or x == "metadata.sample_rate":
            regx = y
        elif y=="":
            regx=y
        else:
            regx = re.compile("^.*" + str(y) + ".*", re.IGNORECASE)
        signal = self.db.signal.find({x: regx},{ "_id": 0})
        return signal

    def load_from_database_one(self,y):
        signal = self.db.signal.find_one({"metadata.id":int(y)},{ "_id": 0})
        return signal
    
    def all_signals(self):
        cursor = self.db.signal.find({},{ "_id": 0})
        return cursor
    
    def update(self,sig_id,sig_name,sig_description,sig_authors,sig_measurement,sig_technology,sig_factor,sig_date,sig_license):
        self.db.signal.find_one_and_update({"metadata.id":int(sig_id)}, {"$set": {
                                                                             "metadata.name": sig_name,
                                                                             "metadata.description": sig_description,
                                                                             "metadata.authors": sig_authors,
                                                                             "metadata.measurement": sig_measurement,
                                                                             "metadata.technology_type":sig_technology,
                                                                             "metadata.factor_types":sig_factor,
                                                                             "metadata.date_taken":sig_date,
                                                                             "metadata.license":sig_license
                                                                             }})
    
    def delete(self,y):
        self.db.signal.delete_one({"metadata.id":int(y)})
    
    def close(self):
        self.db.close()


    def mongo_import(self,dir_path):
      Local = LocalUtil(dir_path)
      
      iterator = self.db.signal.find({},{ "_id": 0})
      for document in iterator:
          document["metadata"]["id"] = Local.next_id()
          Local.Save(document) 
  
    def local_import(self,dir_path):
      Local = LocalUtil(dir_path)
      for entry in os.scandir(dir_path+ "\signals"):
            json_dict = Local.Load(entry.name[3:-4])        
            self.save_to_database(json_dict)
 

    def next_id(self):      
      indexer = self.all_signals()  
                  
      
      free_id =  1
      for i in indexer:
          if free_id == i["metadata"]["id"]:
              free_id = free_id+1
          
        
      return free_id  
# dir_path = os.path.dirname(os.path.realpath(__file__)) + "\signals" + "\id_1.zip"
#a = MongoClient("mongodb+srv://test:test@signals.xn9ot.mongodb.net/myFirstDatabase?retryWrites=true&w=majority").Signal_database   
# fs = gridfs.GridFS(a,collection="signal")


# w = LocalUtil.Load(2)

# raw_bson = BSON.encode(w)
# wew = BSON.decode(raw_bson)
# fs.put(raw_bson, filename="1")

# fs.get

# for ID in fs.find({'filename': '2'}).distinct('_id'):
#     fs.delete(ID)





# 
# for document in cursor:
#       LocalUtil.Save(document) 