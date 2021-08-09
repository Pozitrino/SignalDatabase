# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 12:33:53 2021

@author: Pozitrino
"""

import os 
import json
import zipfile
import pandas as pd
import re


import base64
import io
from utils.GeneralUtils import as_list
import dash_html_components as html


class LocalUtil:
  def __init__(self,dir_path:str):
      self.dir_path = dir_path
      
  
  
  def Load(self,sig_id: int) -> dict:            
    dir_path = self.dir_path + "\signals" + "\id_{}.zip".format(sig_id)

    if os.path.isfile(dir_path):
     archive = zipfile.ZipFile(dir_path, 'r')
     imgdata = archive.read('{}.json'.format(sig_id))
    else:
        raise Exception("Signal with id {} does not exists".format(sig_id)) 
    
    return json.loads(imgdata)
  
  def Create_indexer(self):
      f = open("indexer.json", "x")
      f.write("[]")
      f.close()
      
  
  def Delete(self,sig_id: int): 
   
    dir_path = self.dir_path + "\signals" + "\id_{}.zip".format(sig_id)
    if os.path.exists(dir_path):
        os.remove(dir_path)
        self.rebuild_indexer() 

       
  
  
  

  def Save(self,json_dict: dict):   
   sig_id =  json_dict["metadata"]["id"] 
   dir_path = self.dir_path + "\signals" + "\id_{}.zip".format(sig_id)
   
   if os.path.isfile(self.dir_path + "\indexer.json") == False:
      self.rebuild_indexer() 
   
   if os.path.isfile(dir_path):
      raise Exception("Signal with id {} already exists".format(sig_id))
   else:   
       s = json.dumps(json_dict, indent=2, sort_keys=False)
       archive = zipfile.ZipFile(dir_path, 'w')
       archive.writestr("{}.json".format(sig_id), s,compress_type=zipfile.ZIP_DEFLATED)
       archive.close()
   self.rebuild_indexer() 

  def rebuild_indexer(self):   
    directory = self.dir_path + "\signals"
    
    if os.path.isfile("indexer.json") == False:
                 f = open("indexer.json", "x")
                 f.write("[]")
                 f.close() 
            
    f = open("indexer.json","r")
    file_str = f.read()
    f.close()
    
    if (len(file_str)) != 2:
        file_str = "[]"
        

    if os.path.isdir(directory):
        id_sorted=[]    
    
        for entry in os.scandir(directory):
 
            id_sorted.append(int(entry.name[3:-4]))
        
        id_sorted.sort()
        g = 0    
        for i in id_sorted:
            archive = zipfile.ZipFile(directory + "\id_{}.zip".format(id_sorted[g]), 'r')
            imgdata = json.loads(archive.read('{}.json'.format(id_sorted[g])))
            archive.close()
            g=g+1
            json_str = json.dumps(imgdata["metadata"],indent=2)
        


            if(len(file_str)) == 2:
                file_str = file_str[:-1] + json_str + "]"
           
            else:
                file_str = file_str[:-1] + "," + json_str + "]"

        

    else:
      os.mkdir(directory)


    f = open("indexer.json","w")
    f.write(file_str)   
    f.close()
     
  def Dataframe(self,json_list:list):
     i=0
     leaf  = []
     
     if len(json_list) == 0:
         return pd.DataFrame(leaf,columns=['ID','Name','Description','Author','Measurement','Technology type','Factor','Date','Sample rate','License'])
     
     json_dict = json_list
     while i<len(json_dict):
            atr_list = []
            for x in json_dict[i]: 
                
                atr_list = atr_list + [json_dict[i][x]]
            
            leaf = leaf + [atr_list[:-1]]
            i = i+1
            df = pd.DataFrame (leaf,columns=['ID','Name','Description','Author','Measurement','Technology type','Factor','Date','Sample rate','License'])

     return df

  def Search(self,key:str, value):
     if value == "":
        return []
     with open('indexer.json') as json_file:
        indexer = json.load(json_file)
     regx = re.compile("^.*" + str(value) + ".*", re.IGNORECASE) 
     key = key[9:]
     id_list =[]
     
     if key == "id" or key == "sample_rate":
         for i in indexer:
             if i[key]== value:
                 id_list.append(i) 
      
         return id_list
     elif key == "authors" or key == "factor_types":
          for i in indexer:
              for x in i[key]:
                 if re.match(regx, x):
                     id_list.append(i)
                     break
          return id_list           

     else:
          for i in indexer:
             if re.match(regx, i[key]):
                 id_list.append(i)
          return id_list

  def return_indexer(self):
     with open('indexer.json') as json_file:
        indexer = json.load(json_file)
     return indexer   


  def All_signals(self):
      id_list =[]
      
      if os.path.isfile("indexer.json") == False:
                  LocalUtil.rebuild_indexer() 
                  
      
      with open('indexer.json') as json_file:
        indexer = json.load(json_file)
      
      for i in indexer:
             id_list.append(i) 
             
      return id_list

  def next_id(self):      
      if os.path.isfile("indexer.json") == False:
                 self.rebuild_indexer() 
                  
      
      with open('indexer.json') as json_file:
        indexer = json.load(json_file)
      
      free_id =  1
      for i in indexer:
          if free_id == i["id"]:
              free_id = free_id+1
          
        
      return free_id  
    
      
      
  def update_metadata(self,sig_id,sig_name,sig_description,sig_authors,sig_measurement,sig_technology,sig_factor,sig_date,sig_license):
       json_dict = self.Load(sig_id)
       
       json_dict["metadata"]["name"] = sig_name
       
       json_dict["metadata"]["description"] = sig_description
       
       json_dict["metadata"]["authors"] = sig_authors
       
       json_dict["metadata"]["measurement"] = sig_measurement
       
       json_dict["metadata"]["technology_type"] = sig_technology
       
       json_dict["metadata"]["factor_types"] = sig_factor
       
       json_dict["metadata"]["date_taken"]= sig_date
       
       json_dict["metadata"]["license"] = sig_license
       

       self.Delete(sig_id)
       self.Save(json_dict)

      
      
      


  


  
  def create_event(self,time,label,note,channel):
      event = {
          "time": time,
          "label": label,
          "note": note,
		  "channel": channel
        }
      return event

  def add_event(self,annotations:list, event:list,ann_id:int): 

      anno = as_list(annotations)
      events = anno[ann_id]["events"]
      events = as_list(events)
      events.append(event)
      anno[ann_id]["events"] = events


  def create_annotation(self,main_label:str,main_note:str,channels:list,times:list,events:list):
        
        annot = {
            "label": main_label,
            "note": main_note,
            "channels":channels ,
            "time": times,
            "events": events
         }  
        
        
        return annot



      
    
  def create_metadata(self,fs):
        
        json_metadata={
        "metadata": {
        "id": self.next_id(),
        "name": "",
        "description": "",
        "authors": [""],
        "measurement": "",
        "technology_type": "",
        "factor_types": [""],
        "date_taken": "",
        "sample_rate": fs,
        "license":"",
        "subject": {
        "id": "",
        "age": "",
        "sex": "",
        "diagnoses": "",
        "medication": ""
        }
        }
        }
    
        metadata_str = json.dumps(json_metadata)
        
    
        return metadata_str[:-1] + ","
   
  def create_channels(self,chan_count,data):
        i = 0;
        channels_str='"channels":[' 
        while i<chan_count:
        
           
          json_channels={
              "name":"",
              "units":"",
              "measurement":"",
              "technology_type":[""],
              "factor_types":"",
              "values": data[i].tolist()
              }
          
          
          channels_str = channels_str + json.dumps(json_channels)                  
          
          if(i+1 != chan_count):
              channels_str = channels_str + ","
          i += 1
          

        return channels_str + "]}" 






# with open('8.json') as json_file:
#      indexer = json.load(json_file)

# a = LocalUtil.create_event(0,"label","note",1)
# b = LocalUtil.create_annotation("main_label", "main_note", 0, 0, a)
# d = indexer
# LocalUtil.add_event(d["annotations"], a, 2)
# LocalUtil.add_event(d["annotations"], a, 3)