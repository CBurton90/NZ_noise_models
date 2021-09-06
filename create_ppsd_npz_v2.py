#!/usr/bin/env python3

import datetime
import os
from glob import glob
import traceback

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




def create_npz(network,station,channel,start,end,path):
	# create a list of days
	datelist = pd.date_range(start.datetime, end.datetime, freq="D")
	# print(datelist)
	# add GeoNet FDSN clients
	c = Client(data_provider)
	nrt_client = Client("http://service-nrt.geonet.org.nz")
	# format if mseed is saved
	nslc = "{}.{}.{}".format(network, station, channel)
	# make sure that wildcard characters are not in nslc
	nslc = nslc.replace("*", "").replace("?", "")
	for day in datelist:
		datestr = day.strftime("%Y-%m-%d")
		fn = "{}_{}.mseed".format(datestr, nslc)
		# print(fn)
		if day != datelist[-1] and os.path.isfile(path+station+'/'+fn):
			continue
		else:
			try:
				location = '10'
				args = (network, station, location, channel,
					UTCDateTime(day)-1801, UTCDateTime(day)+86400+1801,)
				# print('Trying location code 10 for '+station)
				# print(day)
				# print(station)
				st = c.get_waveforms(*args, attach_response=True)
				st.merge(fill_value='interpolate')
				# print(st)
				ppsd(st=st,network=network,station=station,location=location,channel=channel,day=day,path=path,datestr=datestr)
			except Exception as e:
				try:
					location = '11'
					args = (network, station, location, channel,
						UTCDateTime(day)-1801, UTCDateTime(day)+86400+1801,)
					# print('Trying location code 11 for '+station)
					st = c.get_waveforms(*args, attach_response=True)
					st.merge(fill_value='interpolate')
					# print(st)
					ppsd(st=st,network=network,station=station,location=location,channel=channel,day=day,path=path,datestr=datestr)
				except Exception as e:
					# print(e)
					print(day)
					print('No broadband FDSN data available for '+station)


						
					
			# # st.write(fn)
			# try:
			# 	resp = c.get_stations(UTCDateTime(day), network=network, station=station, location='10',
			# 			channel=channel, level="response")
			# except Exception as e:
			# 	try:
			# 		resp = c.get_stations(UTCDateTime(day), network=network, station=station, location='11',
			# 				channel=channel, level="response")
			# 	except Exception as e:
			# 		print('No inventory can be found for '+station)
			# # print(resp)
			# for id in list(set([tr.id for tr in st])):
			# 	fn_out = "{}_{}.npz".format(datestr, id)
			# 	if os.path.isfile(path+station+'/'+fn_out):
			# 		print("%s completed previously."%fn_out)
			# 		continue
			# 	st = st.select(id=id)
			# 	st.attach_response(resp)
			# 	# ppsd = PPSD(st[0].stats, metadata=resp,
		 #  #                   ppsd_length=1800, overlap=0.5,
		 #  #                   period_smoothing_width_octaves=0.025,
		 #  #                   period_step_octaves=0.0125,
		 #  #                   period_limits=(0.008, 50),
		 #  #                   db_bins=(-200, 20, 0.25))
			# 	ppsd = PPSD(st[0].stats, metadata=resp)
			# 	ppsd.add(st)
			# 	ppsd.save_npz(path+station+'/'+fn_out[:-4])
			# 	print(st)
			# 	del st, ppsd

def ppsd(st,network,station,location,channel,day,path,datestr):
	c = Client(data_provider)
	resp = c.get_stations(UTCDateTime(day), network=network, station=station, location=location,
			channel=channel, level="response")
	print(resp)


	for id in list(set([tr.id for tr in st])):
			fn_out = "{}_{}.npz".format(datestr, id)
			#print(fn_out)
			if os.path.isfile(path+station+'/'+fn_out):
				print("%s completed previously."%fn_out)
				continue
			st = st.select(id=id)
			# print(st)
			st.attach_response(resp)
			# (after McNamara and Buland 2004, obspy default)
			ppsd = PPSD(st[0].stats, metadata=resp,
				db_bins=(-200, 20, 1.0), ppsd_length=3600.0,
				overlap=0.5, special_handling=None,
				period_smoothing_width_octaves=1.0,
				period_step_octaves=0.125)
			
		    # (testing after ThomasLecocq/SeismoRMS wherby the PSD is set to nervous rather than smooth "default PQLX" and half hour 50% overlaps,
		    # the binning period of 0.0125 octaves and averaging over 0.125 octaves at each central frequency is not required here and creates issues
		    # at longer periods)
			# ppsd = PPSD(st[0].stats, metadata=resp,
			# 	ppsd_length=1800, overlap=0.5,
		 #        period_smoothing_width_octaves=0.025,
		 #        period_step_octaves=0.0125,
		 #        period_limits=(0.008, 50),
		 #        db_bins=(-200, 20, 0.25))
			ppsd.add(st)
			ppsd.save_npz(path+station+'/'+fn_out[:-4])
			print(st)
			del st, ppsd

def main():
	pool = multiprocessing.Pool(processes=processes, maxtasksperchild=1)
	pool = multiprocessing.get_context('spawn').Pool(processes=processes)
	args = []
	for station in stations:
		args += [(network, station, channel, start, end, path)]
	print(args)
	pool.starmap(create_npz, args)
	pool.close()
	pool.join()



processes = cpu_count()

network = "NZ"
start = UTCDateTime("2020-01-01")
end = UTCDateTime("2020-01-03")
stations = loadtxt("NI_NN_list.txt", dtype=str, unpack=False)
channel = "HHZ"
path = "/home/conradb/git/NZ_noise_models/NI_stations/"
data_provider = "GEONET"

# some test sites and times to try sites with varying LC's and data gaps

# start = UTCDateTime('2021-03-06T00:00:00')
# end = UTCDateTime('2021-03-08T00:00:00')
# stations = ['BFZ', 'RIZ', 'FOZ', 'URZ']

# main program

if __name__ == "__main__":
	start_code = timer()
	multiprocessing.set_start_method("spawn")
	main()
	end_code = timer()
	print(end_code - start_code)


# non-multiprocessing option, if running comment out the main() function and the __name__ == "__main__" block above

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

# for reference using all NI stations (ex RIZ/CTZ) over 3 days processing times are:
# with multiprocessing = 246.40s
# without multiprocessing = 420.81s