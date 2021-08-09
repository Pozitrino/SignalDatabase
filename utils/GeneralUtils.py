# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:54:11 2021

@author: Pozitrino
"""

import numpy as np
import pandas as pd
from typing import Union, Sequence, Dict, Set, Any
import collections.abc
from collections import defaultdict
from re import match, finditer


NON_THRESHOLD = {"IEMG", "MAV", "MMAV1", "MMAV2", "SSI", "VAR", "RMS", "WL", "LOG"}
WITH_THRESHOLD = {"WAMP", "SC", "ZC"}
ALL_SUPPORTED = NON_THRESHOLD | WITH_THRESHOLD


def seq_wrap(x: Any) -> Sequence[Any]:
    """
    Function wraps scalar values to one-item sequences (sequences are returned
    unmodified)

    Args:
        x: scalar value or sequence

    Returns:
        sequence
    """
    if isinstance(x, collections.abc.Sequence):
        return x
    else:
        return (x,)
    

def features(data: np.ndarray, features: Set[str],
             thresholds: Dict[str, Union[float, Sequence[float]]] = None) -> Dict[str, np.ndarray]:
    r = {}
    n = data.shape[1]
    if {"IEMG", "MAV"} & features:
        absum = np.sum(np.abs(data), axis=1)
        if "IEMG" in features:
            r["IEMG"] = absum
        if "MAV" in features:
            r["MAV"] = absum / n

    if {"MMAV1", "MMAV2"} & features:
        data1 = np.abs(data[:, :n // 4])
        data2 = np.abs(data[:, n // 4:3 * n // 4])
        data3 = np.abs(data[:, 3 * n // 4:])
        wsum = np.sum(data2, axis=1)
        if "MMAV1" in features:
            r["MMAV1"] = (0.5 * np.sum(data1, axis=1) + wsum + 0.5 * np.sum(data3, axis=1)) / n
        if "MMAV2" in features:
            koef1 = 4 * np.arange(1, n // 4 + 1, dtype=np.float64) / n
            koef3 = 4 * (n - np.arange(3 * n // 4 + 1, n + 1, dtype=np.float64)) / n
            r["MMAV2"] = (np.sum(koef1 * data1, axis=1) + wsum + np.sum(koef3 * data3, axis=1)) / n

    if {"SSI", "VAR", "RMS"} & features:
        qsum = np.sum(data * data, axis=1)
        if "SSI" in features:
            r["SSI"] = qsum
        if "VAR" in features:
            r["VAR"] = qsum / (n - 1)
        if "RMS" in features:
            r["RMS"] = np.sqrt(qsum / n)

    if {"WL", "WAMP"} & features:
        df = np.abs(data[:, 1:] - data[:, :-1])
        if "WL" in features:
            r["WL"] = np.sum(df, axis=1)
        if "WAMP" in features:
            thresh = seq_wrap(thresholds["WAMP"])
            for t in thresh:
                r[f"WAMP({t})"] = np.sum(np.where(df >= t, 1, 0), axis=1)
    if "LOG" in features:
        r["LOG"] = np.exp(np.sum(np.log(np.abs(data)), axis=1) / n)
    if "SC" in features:
        thresh = seq_wrap(thresholds["SC"])
        for t in thresh:
            r[f"SC({t})"] = np.sum(np.where((data[:, 1:-1] - data[:, :-2]) * (data[:, 1:-1] - data[:, 2:])
                     >= t, 1, 0), axis=1)

    if "ZC" in features:
        for diff_thresh, mul_thresh in thresholds["ZC"]:
            r[f"ZC({diff_thresh},{mul_thresh})"]  = np.sum(np.where(np.logical_and(data[:, :-1] * data[:, 1:] >= mul_thresh,
                                df >= diff_thresh), 1, 0), axis=1)
    return r

def features_dataframe(channel_count, dictionary:dict):
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
    
def Synergy_data(a:list):
            longline = None
            cline = False
            data = defaultdict(list)
            gsize = 0
            channel = 0
            fs=0
            for line in a:
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


def as_list(x):
        if type(x) is list:
            return x
        else:
            return [x]

                
    