from pymongo import MongoClient
import re
import os
from utils.LocalUtils import LocalUtil




#Class for handling MongoDB
class DatabaseHandler:
    
    def __init__(self):    
        self.db = MongoClient("mongodb+srv://test:test@signals.xn9ot.mongodb.net/myFirstDatabase?retryWrites=true&w=majority").Signal_database
        
        
    #Saves signals to database
    def save_to_database(self,json_dict:dict):        
        self.db.signal.insert_one(json_dict)
        
    #Returns multiple signals from database
    def load_from_database(self,key:str,value):
        if key == "metadata.id" or key == "metadata.sample_rate":
            regx = value
        elif value=="":
            regx=value
        else:
            regx = re.compile("^.*" + str(value) + ".*", re.IGNORECASE)
        signal = self.db.signal.find({key: regx},{ "_id": 0})
        return signal

    #Returns single signal from database
    def load_from_database_one(self,value: int):
        signal = self.db.signal.find_one({"metadata.id":int(value)},{ "_id": 0})
        return signal
    
    #Returns all signals from database
    def all_signals(self):
        cursor = self.db.signal.find({},{ "_id": 0})
        return cursor
    
    #Edits and saves signal metadata
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
        
    #Deletes signal from database
    def delete(self,y):
        self.db.signal.delete_one({"metadata.id":int(y)})
    
    #Closes connection
    def close(self):
        self.db.close()

    #Imports signals from MongoDB to local storage
    def mongo_import(self,dir_path):
      Local = LocalUtil(dir_path)
      
      iterator = self.db.signal.find({},{ "_id": 0})
      for document in iterator:
          document["metadata"]["id"] = Local.next_id()
          Local.save(document) 
 

    #Imports signals from local storage to MongoDB
    def local_import(self,dir_path):
      Local = LocalUtil(dir_path)
      for entry in os.scandir(dir_path+ "\signals"):
            json_dict = Local.load(entry.name[3:-4])        
            self.save_to_database(json_dict)
 
    #Returns first free aviable id in database
    def next_id(self) -> int:      
      indexer = self.all_signals()  
                  
      
      free_id =  1
      for i in indexer:
          if free_id == i["metadata"]["id"]:
              free_id = free_id+1
          
        
      return free_id  
