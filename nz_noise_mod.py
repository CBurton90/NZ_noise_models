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
from itertools import cycle
from cycler import cycler

from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client
from obspy.signal import PPSD


start = UTCDateTime("2020-01-01")
end = UTCDateTime("2020-12-31")

stations = np.loadtxt("NI_NN_list.txt", dtype=str, unpack=False)

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

# prop_cycle = plt.rcParams['axes.prop_cycle']
# colors = cycle(prop_cycle.by_key()['color'])

# plotting parameters

num = len(stations)
styles = ['solid', 'dashed', 'dashdot', 'dotted']
num_styles = len(styles)

fig = plt.figure()
ax = fig.add_subplot(111)

# trying a few different colormaps

# cm = plt.get_cmap('gist_rainbow')
# colors = [cm(1.*i/num) for i in range(num)]
# ax.set_prop_cycle(cycler('color', colors))

ax.set_prop_cycle('color',plt.cm.jet(np.linspace(0,1,num)))

# cycle through dictionary to grab individual station percentiles and modes 
# (modes also plotted) then combine in an array/list

for i, (mseedid, ppsd) in enumerate(ppsds.items()):
	# ppsd.plot()
	p5 = ppsd.get_percentile(percentile=5)
	p95 = ppsd.get_percentile(percentile=95)
	mode = ppsd.get_mode()
	lines = ax.plot(mode[0],mode[1], label=mseedid)
	# lines[0].set_color(cm(i//num_styles*float(num_styles)/num))
	# lines[0].set_color(cm(i//num))
	lines[0].set_linestyle(styles[i%num_styles])
	p5_combined += p5
	p95_combined += p95
	mode_combined += mode

print(range(len(p5_combined)))
# print(np.shape(p5_combined))

print(p5_combined[1::2])

# combine the minimum values within the set lower pecentiles from 
# odd array indexes (dB values) to create a LNM 

lnm = np.minimum.reduce(p5_combined[1::2])

# combine the maximum values within the set upper percentiles from
# odd array indexes (dB values) to create a HNM

hnm = np.maximum.reduce(p95_combined[1::2])

# combine the minimum values from the individual station modes from
# odd array indexes (dB values) to create a MLNM 

mlnm = np.minimum.reduce(mode_combined[1::2])

# save to csv file
period_idx = np.array(mode_combined[0])
power = np.array(mlnm[0:])
df = pd.DataFrame({"Period (s)" : period_idx, "Power (dB[m^2/s^4/Hz])" : power})
df.to_csv("North_Island_MLNM.csv", index=False)
# save to npy file
stacked = np.stack((period_idx, power))
print(stacked)
np.save('North_Island_MLNM.npy', stacked)

# print(lnm)
# plt.plot(p5[0],lnm, label='lowest combined NI NZNSN 5th percentiles')
# plt.plot(p5[0],hnm, label='highest combined NI NZNSN 95th percentiles')
ax.plot(p5[0],mlnm, c='k', linestyle='dashed', label='NI MLNM')
plt.xscale('log')
plt.xlim(0.02,200)
plt.ylim(-200,-60)
plt.legend()
plt.show()