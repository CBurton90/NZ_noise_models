#!/usr/bin/env python3

import datetime
import os
from glob import glob

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd

from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client
from obspy.signal import PPSD


start = UTCDateTime("2020-01-01")
end = UTCDateTime("2020-01-05")

station = "BFZ"

path = "/home/conradb/git/NZ_noise_models/NI_stations/"

datelist = pd.date_range(start.datetime, end.datetime, freq="D")
print(datelist)


ppsds = {}
for day in datelist:
    datestr = day.strftime("%Y-%m-%d")
    print(datestr)
    fn_pattern = "{}_*.npz".format(datestr)
    print(fn_pattern)
    for fn in glob(path+station+'/'+fn_pattern):
    	print(fn)
    	mseedid = fn.replace(".npz", "").split("_")[-1]
    	print(mseedid)
    	if mseedid not in ppsds:
    		ppsds[mseedid] = PPSD.load_npz(fn, allow_pickle=True)
    	else:
            ppsds[mseedid].add_npz(fn, allow_pickle=True)

for mseedid, ppsd in ppsds.items():
	ppsd.plot()