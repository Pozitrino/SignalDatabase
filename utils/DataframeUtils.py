import pandas as pd
from pymongo import cursor



class DataframeHandler:

    #Returns dataframe for signal table if mongoDb is selected.
    def dataframe(mongo_cursor : cursor) -> pd.DataFrame:
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
    
    #Returns dataframe for signal table if local is selected.
    def dataframe_local(json_list:list) -> pd.DataFrame:
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
    
    #Returns dataframe for signal properties.
    def features_dataframe(channel_count:int, dictionary:dict) -> pd.DataFrame:
        a=0

        channels = channel_count
        col_names = ['Properties']
        final = []

        while a < channels:
            col_names.append('{}.channel'.format(a+1))
            a=a+1
            

        
        for item in dictionary.items():
            g=0
            reg = []
            reg.append(item[0])
            while g < channels:
                reg.append(round(item[1][g],3))
                g=g+1
            final.append(reg)
           
        df = pd.DataFrame (final,columns=col_names)
        return df    