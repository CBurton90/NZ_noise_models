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

def create_npz(network,station,location,channel,start,end,path):
	# create a list of days
	datelist = pd.date_range(start.datetime, end.datetime, freq="D")
	print(datelist)
	# add GeoNet FDSN clients
	c = Client(data_provider)
	nrt_client = Client("http://service-nrt.geonet.org.nz")
	# format if mseed is saved
	nslc = "{}.{}.{}.{}".format(network, station, location, channel)
	# make sure that wildcard characters are not in nslc
	nslc = nslc.replace("*", "").replace("?", "")
	for day in datelist:
		datestr = day.strftime("%Y-%m-%d")
		fn = "{}_{}.mseed".format(datestr, nslc)
		print(fn)
		if day != datelist[-1] and os.path.isfile(path+station+'/'+fn):
			continue
		else:
			args = (network, station, location, channel,
				UTCDateTime(day)-1801, UTCDateTime(day)+86400+1801,)
			try:
				st = c.get_waveforms(*args, attach_response=True)
			except Exception as e:
				print(e)
				st = nrt_client.get_waveforms(*args, attach_response=True)
			print(st)
			# st.write(fn)
			resp = c.get_stations(UTCDateTime(day), network=network, station=station, location=location,
	                      channel=channel, level="response")
			print(resp)

			for id in list(set([tr.id for tr in st])):
				fn_out = "{}_{}.npz".format(datestr, id)
				if os.path.isfile(path+station+'/'+fn_out):
					print("%s completed previously."%fn_out)
					continue
				st = st.select(id=id)
				st.attach_response(resp)
				ppsd = PPSD(st[0].stats, metadata=resp,
		                    ppsd_length=1800, overlap=0.5,
		                    period_smoothing_width_octaves=0.025,
		                    period_step_octaves=0.0125,
		                    period_limits=(0.008, 50),
		                    db_bins=(-200, 20, 0.25))
				ppsd.add(st)
				ppsd.save_npz(path+station+'/'+fn_out[:-4])
				print(st)
				del st, ppsd




start = UTCDateTime("2020-01-01")
end = UTCDateTime("2020-01-05")

network = "NZ"
stations = ["BFZ", "PXZ"]
location = "10"
channel = "HHZ"
dataset = "birchfarm"
time_zone = "Pacific/Auckland"
path = "/home/conradb/git/NZ_noise_models/NI_stations/"

data_provider = "GEONET"
bans = {"2020-03-23 23:59":'Level 3', 
        "2020-03-25 23:59":'Level 4'}



for station in stations:
	try:
		create_npz(network=network,station=station,location='10',channel=channel,start=start,end=end,path=path)
	except:
		try:
			create_npz(network=network,station=station,location='11',channel=channel,start=start,end=end,path=path)
		except:
			print('no FDSN data available for site ' + station)



# datelist = pd.date_range(start.datetime, end.datetime, freq="D")
# print(datelist)

# c = Client(data_provider)
# nrt_client = Client("http://service-nrt.geonet.org.nz")

# nslc = "{}.{}.{}.{}".format(network, station, location, channel)
# # make sure that wildcard characters are not in nslc
# nslc = nslc.replace("*", "").replace("?", "")
# for day in datelist:
#     datestr = day.strftime("%Y-%m-%d")
#     fn = "{}_{}_{}.mseed".format(dataset, datestr, nslc)
#     print(fn)
#     if day != datelist[-1] and os.path.isfile(fn):
#         continue
#     else:
#         args = (network, station, location, channel,
#                 UTCDateTime(day)-1801, UTCDateTime(day)+86400+1801,)
#         try:
#             st = c.get_waveforms(*args, attach_response=True)
#         except Exception as e:
#             print(e)
#             st = nrt_client.get_waveforms(*args, attach_response=True)
#         print(st)
#         # st.write(fn)
#         resp = c.get_stations(UTCDateTime(day), network=network, station=station, location=location,
#                       channel=channel, level="response")
#         print(resp)

#         for id in list(set([tr.id for tr in st])):
#         	fn_out = "{}_{}_{}.npz".format(dataset, datestr, id)
# 	        if os.path.isfile('/home/conradb/git/NZ_noise_models/NI_stations/'+station+'/'+fn_out):
# 	            print("%s completed previously."%fn_out)
# 	            continue
# 	        st = st.select(id=id)
# 	        st.attach_response(resp)
# 	        ppsd = PPSD(st[0].stats, metadata=resp,
# 	                    ppsd_length=1800, overlap=0.5,
# 	                    period_smoothing_width_octaves=0.025,
# 	                    period_step_octaves=0.0125,
# 	                    period_limits=(0.008, 50),
# 	                    db_bins=(-200, 20, 0.25))
# 	        ppsd.add(st)
# 	        ppsd.save_npz('/home/conradb/git/NZ_noise_models/NI_stations/'+station+'/'+fn_out[:-4])
# 	        print(st)
# 	        del st, ppsd

# print(os.path)


