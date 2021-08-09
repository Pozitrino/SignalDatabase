# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 16:59:20 2021

@author: Pozitrino
"""
import json
import base64
import io
from utils.GeneralUtils import Synergy_data
from utils.DatabaseUtils import DatabaseHandler
import dash_html_components as html
from utils.LocalUtils import LocalUtil

def parse_contents(contents, filename, date,storage,dir_path):
        Local = LocalUtil(dir_path)    
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
    

        try:
            if 'json' in filename:
     
                json_dict = json.loads(decoded)
 
            if 'txt' in filename:
                    txt_content = io.StringIO(decoded.decode('utf-16le')).readlines()
                    b = Synergy_data(txt_content)
                    json_dict=json.loads(Local.create_metadata(b[1]) + Local.create_channels(len(b[0]),b[0]))
            
            if storage == "Local":
                Local.Save(json_dict)
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