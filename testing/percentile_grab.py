#!/usr/bin/env python3

from obspy import read, read_inventory
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from itertools import cycle
from cycler import cycler

def get_stream_inv(station, channel, location, t1, duration):
	client = Client("http://service.geonet.org.nz")
	st = client.get_waveforms(
        network="NZ", station=station, location=location,
        channel=channel, starttime=t1, endtime=t1 + duration)
	st.merge(fill_value='interpolate')
	# print(st)
	inv = client.get_stations(
			network="NZ", station=station, 
            location=location, channel=channel, 
            level="response", startbefore=t1, endafter=t1 + duration)

	return st, inv

def retrieve_percentiles(st,inv,station,location):
	tr = st.select(id="NZ."+station+"."+location+".HHZ")[0]
	print(tr)
	# (after McNamara and Buland 2004, obspy default)
	ppsd = PPSD(tr.stats, metadata=inv,
		db_bins=(-200, -50, 1.0), ppsd_length=3600.0,
		overlap=0.5, special_handling=None,
		period_smoothing_width_octaves=1.0,
		period_step_octaves=0.125)
    # (after ThomasLecocq/SeismoRMS wherby the PSD is set to nervous rather than smooth)
	# ppsd = PPSD(tr.stats, metadata=inv,
	# 	ppsd_length=1800, overlap=0.5,
 #        period_smoothing_width_octaves=0.025,
 #        period_step_octaves=0.0125,
 #        period_limits=(0.008, 50),
 #        db_bins=(-200, 20, 0.25))
	ppsd.add(tr)
	print(ppsd)
	ppsd.save_npz(station+"_24hrs.npz")
	# ppsd.plot()
	p5 = ppsd.get_percentile(percentile=5)
	p95 = ppsd.get_percentile(percentile=95)
	mode = ppsd.get_mode()
	# print(p5)
	# print(p95)
	# plt.plot(p5[0],p5[1])
	# plt.plot(p95[0],p95[1])
	# plt.xscale('log')
	# plt.xlim(0.02,200)
	# plt.ylim(-200,-60)
	# plt.suptitle(station+' HNM + LNM')
	# plt.show()

	return p5, p95, mode


stations = ['BKZ','BFZ','PXZ','KNZ','PUZ','VRZ','URZ','MWZ','WEL','OUZ','RPZ','QRZ','LTZ','WCZ','KUZ','TLZ','URZ']
t1 = UTCDateTime('2020-01-01T00:00:00')
duration = 60*60*1
# t1 = UTCDateTime('2021-03-05T22:00:00')

p5_combined = []
p95_combined = []
mode_combined = []

# prop_cycle = plt.rcParams['axes.prop_cycle']
# colors = cycle(prop_cycle.by_key()['color'])

# val = cm.jet(np.linspace(0,1,len(stations)))

num = len(stations)
styles = ['solid', 'dashed', 'dashdot', 'dotted']
num_styles = len(styles)

# cm = plt.get_cmap('gist_rainbow')
   
fig = plt.figure()
ax = fig.add_subplot(111)


# colors = [cm(1.*i/num) for i in range(num)]
# ax.set_prop_cycle(cycler('color', colors))

ax.set_prop_cycle('color',plt.cm.plasma(np.linspace(0,1,num)))

for i, station in enumerate(stations):
	try:
		st, inv = get_stream_inv(station=station, location='10', channel='HH*', t1=t1, duration=duration)
		print(st)
		print(inv)
		p5, p95, mode = retrieve_percentiles(st=st, inv=inv, station=station, location='10')
		p5_combined += p5
		p95_combined += p95
		mode_combined += mode
		lines = ax.plot(mode[0],mode[1], label=station)
		# lines[0].set_color(cm(i//num_styles*float(num_styles)/num))
		# lines[0].set_color(cm(i//num))
		lines[0].set_linestyle(styles[i%num_styles])

	except Exception as e:
		print(e)
		try:
			st, inv = get_stream_inv(station=station, location='11', channel='HH*', t1=t1, duration=duration)
			print(st)
			print(inv)
			p5, p95, mode = retrieve_percentiles(st=st, inv=inv, station=station, location='11')
			p5_combined += p5
			p95_combined += p95
			mode_combined += mode

		except:
			print('no FDSN data available for site ' + station)

print(range(len(p5_combined)))
# print(np.shape(p5_combined))

print(p5_combined[1::2])
a = np.minimum.reduce(p5_combined[1::2])
b = np.maximum.reduce(p95_combined[1::2])
c = np.minimum.reduce(mode_combined[1::2])

print(a)
# plt.plot(p5[0],a, color=c, label='5th Percentile')
# plt.plot(p5[0],b, color=c, label='95th Percentile')
ax.plot(p5[0],c, color='k', linestyle='dashed', label='MLNM')
plt.xscale('log')
plt.xlim(0.02,200)
plt.ylim(-200,-60)
plt.legend()
plt.show()