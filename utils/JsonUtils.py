import numpy as np
from scipy import signal


# Class that provides basic details about signal
class JsonUtil:
    
    def __init__(self, json_dict:dict):
        self.json_dict = json_dict
    
    # Return values of all channels of a signal
    @property    
    def signals(self):
        i = 0 
        chan_list = []
        while i < len(self.json_dict["channels"]):
            chan_list.append(self.json_dict["channels"][i]["values"])
            i = i +1
        return np.array(chan_list)
    
    # Returns number of channels of a signal
    @property    
    def channel_count(self):
        return len(self.json_dict["channels"])
    
    # Returns sample count of a signal
    @property    
    def sample_count(self):
        return len(self.json_dict["channels"][0]["values"])
    
    # Returns sample rate of a signal
    @property    
    def sample_rate(self):
        return self.json_dict["metadata"]["sample_rate"]
    
    #  Return values on x axis
    @property 
    def x_index(self):
            interval = 1.0 / self.sample_rate
            index = np.linspace(0.0, self.sample_count * interval, self.sample_count,
                                endpoint=False) - 0 * interval
            return index
    
    # Returns length of x axis
    @property 
    def sig_lenght(self):            
            return len(self.x_index)   
    
    # Returns length of a signal in seconds
    @property    
    def sig_duration_s(self):
        f = self.x_index[self.sig_lenght-1:]
        return float(f[0])    
    
    # Returns sample rate of resampled signal
    @property    
    def sig_resample_fs(self):

        return round(4096/self.sig_duration_s,0)

    # Returns all events from annotation collection
    @property  
    def annotation_events(self):
        
        if "annotations" in self.json_dict:
            r = self.json_dict["annotations"]
        else:
            return []
        i = 0

        events = []
        final = []
        while i<len(r):
            events.append(r[i]["events"])
            i=i+1
        i =0
        while i<len(events):
            r = 0
            while r < len(events[i]):
                final.append([events[i][r]["time"],events[i][r]["label"],events[i][r]["note"]])
                r=r+1
            i=i+1
        return final
  
    # Returns resampled signal
    def signal_resample(self):
        i = 0 
        json_resample = self.json_dict
        values = self.signals
        json_resample["metadata"]["sample_rate"] = self.sig_resample_fs
        while i < len(self.json_dict["channels"]):
            json_resample["channels"][i]["values"] = signal.resample(values[i], 4096)
            i = i +1
        return json_resample
    