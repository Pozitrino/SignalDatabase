import os 
import json
import zipfile
import re


#Class that handles work with local storage
class LocalUtil:
  def __init__(self,dir_path: str = ""):
      self.dir_path = dir_path
      
  
  #Loads signal from storage
  def load(self,sig_id: int) -> dict:            
    dir_path = self.dir_path + "\signals" + "\id_{}.zip".format(sig_id)

    if os.path.isfile(dir_path):
     archive = zipfile.ZipFile(dir_path, 'r')
     data = archive.read('{}.json'.format(sig_id))
    else:
        raise Exception("Signal with id {} does not exists".format(sig_id)) 
    
    return json.loads(data)

  #Creates file indexer
  def create_indexer(self):
      f = open("indexer.json", "x")
      f.write("[]")
      f.close()
      
  #Deletes signal from local storage
  def delete(self,sig_id: int): 
   
    dir_path = self.dir_path + "\signals" + "\id_{}.zip".format(sig_id)
    if os.path.exists(dir_path):
        os.remove(dir_path)
        self.rebuild_indexer() 

  #Saves signal to local storage  
  def save(self,json_dict: dict, idnext: bool = True): 
     
   if idnext == True:   
       sig_id = self.next_id()
       json_dict["metadata"]["id"]  = sig_id
   else:
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

  #Updates indexer file.
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
     
  #Returns signal with matching metadata when compared to user input.
  def search(self,key:str, value) -> list:
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
          return 
      
  #Returns indexer with metadata 
  def return_indexer(self) -> dict:
     with open('indexer.json') as json_file:
        indexer = json.load(json_file)
     return indexer   

  #Returns all signals in local storage
  def all_signals(self) -> list:
      id_list =[]
      
      if os.path.isfile("indexer.json") == False:
                  LocalUtil.rebuild_indexer() 
                  
      
      with open('indexer.json') as json_file:
        indexer = json.load(json_file)
      
      for i in indexer:
             id_list.append(i) 
             
      return 
  
  #Returns first aviable id
  def next_id(self) -> int:      
      if os.path.isfile("indexer.json") == False:
                 self.rebuild_indexer() 
                  
      
      with open('indexer.json') as json_file:
        indexer = json.load(json_file)
      
      free_id =  1
      for i in indexer:
          if free_id == i["id"]:
              free_id = free_id+1
          
        
      return free_id  
    
      
  #Updates signal metadata
  def update_metadata(self,sig_id,sig_name,sig_description,sig_authors,sig_measurement,sig_technology,sig_factor,sig_date,sig_license):
       json_dict = self.load(sig_id)
       
       json_dict["metadata"]["name"] = sig_name
       
       json_dict["metadata"]["description"] = sig_description
       
       json_dict["metadata"]["authors"] = sig_authors
       
       json_dict["metadata"]["measurement"] = sig_measurement
       
       json_dict["metadata"]["technology_type"] = sig_technology
       
       json_dict["metadata"]["factor_types"] = sig_factor
       
       json_dict["metadata"]["date_taken"]= sig_date
       
       json_dict["metadata"]["license"] = sig_license
       

       self.delete(sig_id)
       self.save(json_dict)

      
      
      