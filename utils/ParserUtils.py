import json
import base64
import io

from utils.DatabaseUtils import DatabaseHandler
from utils.LocalUtils import LocalUtil
import dash_html_components as html
from collections import defaultdict
from re import match, finditer
import numpy as np


#Parses uloaded files to json.
def parse_contents(contents, filename, date,storage,dir_path):
        Local = LocalUtil(dir_path)    
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
    

        try:
            if 'json' in filename:
     
                json_dict = json.loads(decoded)
 
            if 'txt' in filename:
                    txt_content = io.StringIO(decoded.decode('utf-16le')).readlines()
                    SynergyData = Synergy_data(txt_content)
                    json_dict=json.loads(create_metadata(Local.next_id(),SynergyData[1]) + create_channels(len(SynergyData[0]),SynergyData[0]))
            
            if storage == "Local":
                Local.save(json_dict)
            else:
                database = DatabaseHandler()
                json_dict["metadata"]["id"] = database.next_id()
                database.save_to_database(json_dict)
            
            return html.Div([
                'File uploaded'
                ])
        except Exception as e:
            print(e)
            return html.Div([
                'Format not supported or signal with ID = {} already exists'.format(filename[:-5])
                ])
        
#Gets signal data and fs from SynergyLP format.        
def Synergy_data(txt_input:list):
            longline = None
            cline = False
            data = defaultdict(list)
            gsize = 0
            channel = 0
            fs=0
            for line in txt_input:
                line = line.rstrip()
                if cline:
                    longline += line.rstrip("/")
                else:
                    longline = line.rstrip("/")
                if line.endswith("/"):
                    longline += ","
                    cline = True
                    continue
                else:
                    cline = False

                m = match(r"Sampling Frequency\(kHz\)=(\d+,\d+)", longline)
                if m:
                    fs = 1000 * float(m.group(1).replace(",","."))
                    continue

                m = match(r"Channel\s+Number=(\d+)", longline)
                if m:
                    channel = int(m.group(1))-1
                    continue

                m = match(r"(?:Sweep|LivePlay)\s+Data\(mV\)<(\d+)>=(.*)", longline)
                if m:
                    gsize += int(m.group(1))
                    dataline = m.group(2)
                    for subm in finditer(r"(-?)(\d+),(\d+),?", dataline):
                        value = int(subm.group(2)) + int(subm.group(3)) / 100
                        if subm.group(1) == "-":
                            value = -value
                        data[channel].append(value)
            if list(data.keys()) == [0]:
                data = np.array(data[0]).reshape((1, len(data[0])))

            else:
                data = np.vstack(tuple(np.array(data[chan]).reshape(1, len(data[chan]))
                             for chan in sorted(data.keys())))

            return data,fs     

#Creates empty signal metadata       
def create_metadata(sig_id:int,fs:float):
        
        json_metadata={
        "metadata": {
        "id": sig_id,
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

#Creates signal channels with values.
def create_channels(chan_count:int,data):
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