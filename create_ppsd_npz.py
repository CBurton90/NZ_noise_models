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
import multiprocessing
from multiprocessing import cpu_count

from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client
from obspy.signal import PPSD

from timeit import default_timer as timer

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
				# ppsd = PPSD(st[0].stats, metadata=resp,
		  #                   ppsd_length=1800, overlap=0.5,
		  #                   period_smoothing_width_octaves=0.025,
		  #                   period_step_octaves=0.0125,
		  #                   period_limits=(0.008, 50),
		  #                   db_bins=(-200, 20, 0.25))
				ppsd = PPSD(st[0].stats, metadata=resp)
				ppsd.add(st)
				ppsd.save_npz(path+station+'/'+fn_out[:-4])
				print(st)
				del st, ppsd


def main():
	pool = multiprocessing.Pool(processes=2, maxtasksperchild=1)
	pool = multiprocessing.get_context('spawn').Pool(processes=4)
	args_10 = []
	args_11 = []
	for station in stations:
		args_10 += [(network, station , '10', channel, start, end, path)]
		args_11 += [(network, station , '11', channel, start, end, path)]


	# pool = multiprocessing.Pool(processes=4)
	# rst,sst,rst2,sst2,rst3,sst3,rst4,sst4,rst5,sst5,rst6,sst6,rst7,sst7,rst8,sst8,rst9,sst9,rst10,sst10 = pool.starmap(
	#     get_and_remove_response, args, chunksize=1)
	try:
		pool.starmap(create_npz, args_10)
	except Exception as e:
		print(e)
		try:
			pool.starmap(create_npz, args_11)
		except Exception as e:
			print(e)
			print('no FDSN data available for site')
		pool.close()
		pool.join()




start_code = timer()

start = UTCDateTime("2020-01-01")
end = UTCDateTime("2020-01-03")

network = "NZ"
stations = loadtxt("NI_NN_list.txt", dtype=str, unpack=False)
print(stations)
location = "10"
channel = "HHZ"
dataset = "birchfarm"
time_zone = "Pacific/Auckland"
path = "/home/conradb/git/NZ_noise_models/NI_stations/"

data_provider = "GEONET"
bans = {"2020-03-23 23:59":'Level 3', 
        "2020-03-25 23:59":'Level 4'}



if __name__ == "__main__":
	multiprocessing.set_start_method("spawn")
	main()

end_code = timer()
print(end_code - start_code)




# non-multiprocessing option, if running comment out the main() function and the if statement above

# for station in stations:
# 	try:
# 		create_npz(network=network,station=station,location='10',channel=channel,start=start,end=end,path=path)
# 	except:
# 		try:
# 			create_npz(network=network,station=station,location='11',channel=channel,start=start,end=end,path=path)
# 		except:
# 			print('no FDSN data available for site ' + station)



# end_code = timer()
# print(end_code - start_code)