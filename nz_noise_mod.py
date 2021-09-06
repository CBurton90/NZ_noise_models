#!/usr/bin/env python3

import datetime
import os
from glob import glob

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as pe
import numpy as np
from numpy import loadtxt
import pandas as pd

from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client
from obspy.signal import PPSD


start = UTCDateTime("2020-01-01")
end = UTCDateTime("2020-01-05")

stations = loadtxt("NI_NN_list.txt", dtype=str, unpack=False)

path = "/home/conradb/git/NZ_noise_models/NI_stations/"

datelist = pd.date_range(start.datetime, end.datetime, freq="D")
print(datelist)


ppsds = {}

for station in stations:
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


p5_combined = []
p95_combined = []
mode_combined = []

for mseedid, ppsd in ppsds.items():
	# ppsd.plot()
	p5 = ppsd.get_percentile(percentile=5)
	p95 = ppsd.get_percentile(percentile=95)
	mode = ppsd.get_mode()
	# plt.plot(mode[0],mode[1])
	# plt.xscale('log')
	# plt.xlim(0.02,200)
	# plt.ylim(-200,-60)
	# plt.show()
	p5_combined += p5
	p95_combined += p95
	mode_combined += mode

print(range(len(p5_combined)))
# print(np.shape(p5_combined))

print(p5_combined[1::2])

lnm = np.minimum.reduce(p5_combined[1::2])
hnm = np.maximum.reduce(p95_combined[1::2])
mlnm = np.minimum.reduce(mode_combined[1::2])

print(lnm)
plt.plot(p5[0],lnm, label='lowest combined NI NZNSN 5th percentiles')
plt.plot(p5[0],hnm, label='highest combined NI NZNSN 95th percentiles')
plt.plot(p5[0],mlnm, label='NI MLNM')
plt.xscale('log')
plt.xlim(0.02,200)
plt.ylim(-200,-60)
plt.legend()
plt.show()