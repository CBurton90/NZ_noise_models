#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df1 = pd.read_csv("/home/conradb/git/NZ_noise_models/North_Island_MLNM.csv")
df2 = pd.read_csv("/home/conradb/git/NZ_noise_models/South_Island_MLNM.csv")
df3 = pd.read_csv("/home/conradb/git/NZ_noise_models/North_Island_HNM.csv")
df4 = pd.read_csv("/home/conradb/git/NZ_noise_models/South_Island_HNM.csv")

sns.lineplot(data=df1, x='Period (s)', y='Power (dB[m^2/s^4/Hz])', label='NI_MLNM')
sns.lineplot(data=df2, x='Period (s)', y='Power (dB[m^2/s^4/Hz])', label='SI_MLNM')
sns.lineplot(data=df3, x='Period (s)', y='Power (dB[m^2/s^4/Hz])', label='NI_HNM')
sns.lineplot(data=df4, x='Period (s)', y='Power (dB[m^2/s^4/Hz])', label='SI_HNM')

plt.title("North and South Island Noise Model Comparison", fontsize=15)

plt.xscale('log')
plt.xlim(0.02,200)
plt.xlabel('Period (s)')
plt.ylim(-200,-60)
plt.ylabel('dB[m^2/s^4/Hz]')

# plt.show()
plt.savefig('/home/conradb/git/NZ_noise_models/figures/Comparison.png', dpi=400, format='png')