import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import signal
import heartpy as hp
from utils.JsonUtils import JsonUtil
from utils.GeneralUtils import as_list
import numpy as np
import scipy.fftpack  


# Class that handles annotations
class AnnotsUtil:
    
   # Method that returns dict with collection of annotations
   def create_event(self,time,label,note,channel):
      event = {
          "time": time,
          "label": label,
          "note": note,
		  "channel": channel
        }
      return event
  
   # Method for adding event to existing annotation collection
   def add_event(self,annotations:list, event:list,ann_id:int): 

      anno = as_list(annotations)
      events = anno[ann_id]["events"]
      events = as_list(events)
      events.append(event)
      anno[ann_id]["events"] = events


   # Method that creates complete annotation collection
   def create_annotation(self,main_label:str,main_note:str,channels:list,times:list,events:list):
        
        annot = {
            "label": main_label,
            "note": main_note,
            "channels":channels ,
            "time": times,
            "events": events
         }  
        
        
        return annot



# Class that contains basic methods for signal processing
class GraphUtil:
     def __init__(self,json_dict:dict):    
        self.json_dict = json_dict

     # Method for bandstop signal filtering
     def butter_bandstop_filter(self,data, lowcut, highcut, fs, order):


        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        i, u = signal.butter(order, [low, high], btype='bandstop')
        y = signal.lfilter(i, u, data)
        return y
    



     # Method that handles signal plotting 
     def simple_plot(self):
        
        json_handler = JsonUtil(self.json_dict)
        sig =json_handler.signals
        chan_count = json_handler.channel_count
        sig_duration = json_handler.x_index
        i = 0
        fig = make_subplots(rows=chan_count, cols=1,shared_xaxes=True)
        anots = json_handler.annotation_events
        
        while i < chan_count:
              
              fig.add_trace(
              go.Scatter(x=sig_duration, y=sig[i],name = f'{i+1} .channel'),
              row=i+1, col=1, 
              )
              fig.update_xaxes(title_text="Time (s)", row=i+1, col=1)
              fig.update_yaxes(title_text="mV", row=i+1, col=1)
              if anots != []:
                  g = 0
                  while g <len(anots):

                      fig.add_annotation(x=sig_duration[anots[g][0]], y=sig[i][anots[g][0]],
                      text="{}".format(anots[g][1]),
                      showarrow=True,       
                      ax=0,
                      ay=-50,
                      arrowhead=3,
                      row=i+1,
                      col=1,
                              align="center",

        arrowsize=1,
        arrowwidth=2,
        arrowcolor="black",
        bordercolor="black",
        borderwidth=2,
        borderpad=1,
        bgcolor="#e6e6e6",
        opacity=0.8
                      
                      )
                      g=g+1 
               
                    
                  
               
              
              
              i += 1
        fig.update_layout(clickmode='event+select')
        fig.update_layout(title_text="Graph of selected signal:" )
        return fig

     # Method that returns FFT of a signal
     def plot_fft(self,first_index,second_index):
         
        json_handler = JsonUtil(self.json_dict)
        data = json_handler.signals
        time = json_handler.sig_duration_s
        fs = json_handler.sample_rate
        chw = json_handler.channel_count
        
        
        
        time = np.arange(0, time, 1/fs)    
    
        hz = np.linspace(0, fs/2, int(np.floor(len(time)/2)+1))
        freq = scipy.fft.fft(data[0])/len(time)
        
        if first_index == -1:
            first_index = 0
            second_index = len(freq)-1
  
        i = 0
        fig = make_subplots(rows=chw, cols=1,shared_xaxes=True)
        
        while i < chw:

              freq = scipy.fft.fft(data[i][first_index:second_index])/len(time)
              fig.add_trace(
              go.Scatter(x=hz, y=2*np.abs(freq),name = f'{i+1} .channel'),
              row=i+1, col=1, 
              )
              fig.update_xaxes(title_text="Frequency (Hz)", row=i+1, col=1)
              fig.update_yaxes(title_text="Amplitude", row=i+1, col=1)
              i += 1    

    
        return fig





     # Method that handles signal plotting with added filters
     def filter_plot(self,cutoff,order,filtertype,selected,first_index,second_index):
        json_handler = JsonUtil(self.json_dict)
         
        sig =json_handler.signals
        weh = as_list(selected)
        chan_count = json_handler.channel_count
        sig_fs = json_handler.sample_rate
        sig_duration = json_handler.x_index
        if first_index != -1:
            sig_duration = sig_duration[first_index:second_index]
        else:
            first_index = 0
            second_index = len(sig_duration)-1
        
        i = 0
        fig = make_subplots(rows=chan_count, cols=1,shared_xaxes=True)

        weh = sorted(weh)
        while i < chan_count:
            
  
            if chan_count == 1 or weh == []:    
                if filtertype=="bandstop":
                    sig[i]=self.butter_bandstop_filter(sig[i], cutoff[0], cutoff[1], sig_fs, order) 
                else:
                        sig[i]= hp.filter_signal(sig[i], cutoff = cutoff, sample_rate = sig_fs, order = order, filtertype=filtertype)
            
                fig.add_trace(
                    go.Scatter(x=sig_duration, y=sig[i][first_index:second_index],name = f'{i+1} .channel'),
                    row=i+1, col=1, 
                    )
                fig.update_xaxes(title_text="Time (s)", row=i+1, col=1)
                fig.update_yaxes(title_text="mV", row=i+1, col=1)
            
                i += 1
            
            
            
            
            else:
                for x in weh:
                  if x == i+1:    
                    if filtertype=="bandstop":
                        sig[i]=self.butter_bandstop_filter(sig[i], cutoff[0], cutoff[1], sig_fs, order) 


                    else:
                        sig[i]= hp.filter_signal(sig[i], cutoff = cutoff, sample_rate = sig_fs, order = order, filtertype=filtertype)

            
                
                else:
                    sig[i] = sig[i]

                
                fig.add_trace(
                    go.Scatter(x=sig_duration, y=sig[i][first_index:second_index],name = f'{i+1} .channel'),
                    row=i+1, col=1
                    )
                fig.update_xaxes(title_text="Time (s)", row=i+1, col=1)
                fig.update_yaxes(title_text="mV", row=i+1, col=1)
              
                i += 1
                
            
            gur = ""
            if weh == []:
                gur = "all"
            else:
               gur =  weh
            if filtertype == "bandpass" or filtertype == "bandstop":
                fig.update_layout(title_text='Filter: {}, Filter cutoff: {} [Hz] to {}  [Hz], Filter order: {}, Channels filtered: {}'.format(filtertype,cutoff[0],cutoff[1],order,gur) )
            else:
                fig.update_layout(title_text='Filter: {}, Filter cutoff: {} [Hz], Filter order: {}, Channels filtered: {}'.format(filtertype,cutoff,order,gur) )
            


            
        return fig    
    
    
    
    
    
    