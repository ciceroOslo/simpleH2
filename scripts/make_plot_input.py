import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import io

from simpleh2 import SIMPLEH2



antr_file = '../input/h2_antr_ceds21.csv'
ch4_file = '../input/ch4_historical.csv'
bb_file = '../input/bb_emis_gfed.csv'
nmvoc_file = '../input/nmvoc_emis_ssp245.csv'
startyr = 1850
endyr = 2019


fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

antr = pd.read_csv(antr_file, index_col=0).loc[1850:2019]
axs[0,0].plot(antr)

bb = pd.read_csv(bb_file, index_col=0).loc[1850:2019]
axs[0,1].plot(bb)

ch4 = pd.read_csv(ch4_file,  index_col=0).loc[1850:2019]
axs[1,0].plot(ch4)

nmvoc =  pd.read_csv(nmvoc_file,  index_col=0).loc[1850:2019]
axs[1,1].plot(nmvoc)



axs[1,0].set_xlabel("Years")
axs[1,1].set_xlabel("Years")

axs[0,0].set_ylabel("Emissions [Tg yr$^{-1}$]")
axs[0,0].set_ylim(bottom=0)
axs[0,1].set_ylim(bottom=0)
axs[1,1].set_ylim(bottom=0)

axs[0,0].set_title('Anthropogenic emissions')
axs[0,1].set_title('Biomass burning emissions')
axs[1,0].set_title('Methane concentration')
axs[1,1].set_title('Anthropogenic VOC emissions')



plt.show()
