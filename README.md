# NZ_noise_models
Attempt at creating a high-noise and low-noise model for both the North and South Island of NZ

## Motivation

To characterise the background ambient seismic noise at a station over a range of frequencies the construction of a noise model reflected from the stations power spectral density (PSD) is often the standard. Different approaches have been taken over the years to extract a low-noise and high-noise baseline/threshold but by far the most commonly used has been that of Peterson (Peterson 1993) in which he computed a New Low Noise Model (NLNM) and New High Noise Model (NHNM) by estimating the PSD's of the background noise from 75 stations in the Global Seismograph network (GSN). McNamara and Buland (McNamara and Buland 2004) further extended Petersons noise estimation method by examining the distribution of PSD's using a probability density function (PDF) which is often referred to as a probabilistic power spectral density (PPSD). Due to the age of Petersons NLNM/NHNM (20+ years) and the fact that extremely quiet GSN stations from large contiental interiors were used (ANMO/QSPA) it is often seen that such low noise levels of the NLNM are unattainable for other national seismic networks. With population growth and increased urbanisation near stations these noise levels from 20/30 years ago will progressively become an unrealistic threshold thus McNamara and Buland suggested that for routine monitoring purposes a low noise model produced from a stations PPSD statistical mode (highest probability) should be used to create a Mode Low Noise Model (MLNM). The MLNM is created from the minimum of all station PPSD mode values (per octave) of the vertical component to form a combined low noise threshold for the particular network under examination and may change with time as population increases and technology evolves.

For McNamara and Buland their particular focus for creating a MLNM was the Advanced National Seismic System (ANSS) in the United States. S.J Rastin (S.J Rastin 2012) further investigated the concept of a MLNM presented above for the North Island of New Zealand by analysing 5 years of recordings (2005-2009) from the New Zealand National Seismograph Network (NZNSN). A North Island MLNM was produced from processing done in PQLX and a comprehensive discussion had on the comparisons of each station to this low-noise mode baseline.

My desire here is to do two things really: 

1. "Pythonise" the creation of the MLNM so it can be done for any seismic network and output the model into a csv and numpy binary format so it can be read in with any seismic PSD plot produced in python/obspy for a realistic low noise baseline comparison for that particular station(s) and related seismic network.        

2. Create a MLNM and HNM (high-noise model) for both the North and South Islands of New Zealand from NZNSN recordings in 2020 and save each in the formats above.

### Using the scripts (work in progress)

First you need to define a list of stations to create the model. I have created two `.txt` files; `NI_NN_list.txt` defines the North Island stations of the NZNSN and `SI_NN_list.txt` defines the South Island NZNSN stations.

Run `create_folders.sh` to create the station folders from the `.txt` station lists. The newly created individual station folders are used to store the daily ppsd files. Some changes to the path may be needed depending on how you name your folder (i.e. different seismic network).

The script used to produce the daily station ppsd's is `create_ppsd_npz_v2.py`. It is designed to run with parrallel processing and therefore you can change the number of cpu cores to use. As I was processing seismic data for the entire year of 2020 (for all NI/SI stations) I ran this externally within a more powerful compute space of 80 cores of which I used 30. For example processing all the North Island station daily ppsd's for 2020 takes 5040 seconds (84 minutes) with 30 cores used. You can also edit the station list, network, channel/component, FDSN client, path, and timeframe.

Finally, to create the MLNM, plot, and save it in csv/npy format run `nz_noise_mod.py`. Again editing the timeframe, station list, and file paths will be needed. The repo in it's present state has all of the North Island station ppsd's for 2020 already stored in their folders so you can run the script as is to create the North Island MLNM for 2020.

## The NZNSN North Island Mode Low Noise Model (NI_MLNM)

![Image description](https://github.com/CBurton90/NZ_noise_models/blob/main/figures/NI_MLNM.png)      
