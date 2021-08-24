#!/usr/bin/env python3

from obspy import read, read_inventory
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import matplotlib.pyplot as plt
import numpy as np

def get_stream_inv(station, channel, location, t1, duration):
	client = Client("http://service.geonet.org.nz")
	st = client.get_waveforms(
        network="NZ", station=station, location=location,
        channel=channel, starttime=t1, endtime=t1 + duration)
	st.merge(fill_value='interpolate')
	print(st)
	inv = client.get_stations(
			network="NZ", station=station, 
            location=location, channel=channel, 
            level="response", startbefore=t1, endafter=t1 + duration)

	return st, inv

def retrieve_percentiles(st,inv,station,location):
	tr = st.select(id="NZ."+station+"."+location+".HHZ")[0]
	ppsd = PPSD(tr.stats, metadata=inv)
	ppsd.add(tr)
	# ppsd.plot()
	p5 = ppsd.get_percentile(percentile=5)
	p95 = ppsd.get_percentile(percentile=95)
	# print(p5)
	# print(p95)
	plt.plot(p5[0],p5[1])
	plt.plot(p95[0],p95[1])
	plt.xscale('log')
	plt.xlim(0.02,200)
	plt.ylim(-200,-60)
	plt.suptitle(station+' HNM + LNM')
	plt.show()

	return p5, p95


stations = ['BKZ','BFZ','PXZ','KNZ','PUZ','VRZ','URZ','MWZ']
t1 = UTCDateTime('2020-01-01T00:00:00')
duration = 60*60*6
# t1 = UTCDateTime('2021-03-05T22:00:00')

p5_combined = []
p95_combined = []

for station in stations:
	try:
		st, inv = get_stream_inv(station=station, location='10', channel='HH*', t1=t1, duration=duration)
		print(st)
		print(inv)
		p5, p95 = retrieve_percentiles(st=st, inv=inv, station=station, location='10')
		p5_combined += p5
		p95_combined += p95

	except:
		try:
			st, inv = get_stream_inv(station=station, location='11', channel='HH*', t1=t1, duration=duration)
			print(st)
			print(inv)
			p5, p95 = retrieve_percentiles(st=st, inv=inv, station=station, location='11')
			p5_combined += p5
			p95_combined += p95

		except:
			print('no FDSN data available for site ' + station)

print(range(len(p5_combined)))
# print(np.shape(p5_combined))

print(p5_combined[1::2])
a = np.minimum.reduce(p5_combined[1::2])
b = np.maximum.reduce(p95_combined[1::2])

print(a)
plt.plot(p5[0],a)
plt.plot(p5[0],b)
plt.xscale('log')
plt.xlim(0.02,200)
plt.ylim(-200,-60)
plt.show()