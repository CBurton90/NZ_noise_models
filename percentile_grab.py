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
	print(st)
	inv = client.get_stations(
			network="NZ", station=station, 
            location=location, channel=channel, 
            level="response", startbefore=t1, endafter=t1 + duration)

	return st, inv

stations = ['BFZ','PXZ','KNZ','PUZ','VRZ','URZ']
t1 = UTCDateTime('2020-01-01T00:00:00')

p5_combined = []
p95_combined = []

for station in stations:
	st, inv = get_stream_inv(station=station, location='10', channel='HH*', t1=t1, duration=60*60*24)

	print(st)
	print(inv)


	tr = st.select(id="NZ."+station+".10.HHZ")[0]

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
	p5_combined += p5
	p95_combined += p95

# print(p5_combined)
# print(p95_combined)
print(range(len(p5_combined)))

# print(p5[0:121])
print(p5_combined[1])
print(p5_combined[3])
print(p5_combined[5])
print(p5_combined[7])
print(np.shape(p5_combined))

# a = np.minimum(p5_combined[1],p5_combined[3])
# b = np.minimum(p95_combined[1],p95_combined[3])

# a = np.minimum.reduce([p5_combined[1],p5_combined[3],p5_combined[5],p5_combined[7]])
# b = np.maximum.reduce([p95_combined[1],p95_combined[3],p95_combined[5],p5_combined[7]])

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



# pre_filt = (0.01, 0.02, 0.04, 0.08)
# st[n].detrend('linear')
# st[n].taper(max_percentage=0.1, type='cosine')
# st[n].remove_response(output=output, pre_filt=pre_filt, plot=False,
#                        water_level=60, inventory=inv)