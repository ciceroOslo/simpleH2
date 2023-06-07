import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append('/div/no-backup/users/ragnhibs/simpleH2/simpleH2/src/simpleh2/')

def plot_results():
    tot_prod = (sh2_1.h2_antr.loc[startyr:endyr] +
                sh2_1.h2_bb_emis.loc[startyr:endyr] +
                sh2_1.h2_prod_ch4.loc[startyr:endyr] +
                sh2_1.h2_prod_nmvoc.loc[startyr:endyr])
    
    #Plot total production and emissions.
    axs[0].plot(tot_prod,'-', linewidth =1,label=setup)
    axs[1].plot(sh2_1.conc_h2,'-', linewidth =1,label=setup)
    

    
from simpleh2 import SIMPLEH2

startyr = 1850
endyr = 2020
antr_file = '../input/h2_antr_ceds21.csv'
ch4_file = '../input/ch4_historical.csv'
bb_file = '../input/bb_emis_gfed.csv'
nmvoc_file = '../input/nmvoc_emis_ssp245.csv'

#Input filepaths to be used:
paths = {'meth_path': ch4_file,
         'nmvoc_path':nmvoc_file,
         'antr_file':antr_file,
         'bb_file':bb_file}

#Specify nitrate fixation:
nit_fix = 9.0

fig, axs = plt.subplots(nrows=1,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

setup='standard'
pam_dict_osloctm ={"refyr": 2010,
                   "pre_ind_conc": 350.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}

sh2_1 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths)
sh2_1.scale_emissions_antr(31.58)
sh2_1.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
plot_results()

###############################
setup='const OH = 1'
sh2_1.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
plot_results()

###############################################################
setup='pre_ind_lower'
pam_dict_osloctm ={"refyr": 2010,
                   "pre_ind_conc": 250.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}

sh2_1 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths)
sh2_1.scale_emissions_antr(31.58)
sh2_1.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
plot_results()

###############################################################
setup='alternative nmvoc'

nmvoc_file_alt = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_NMVOC_CEDS17.csv'
paths_test = {'meth_path': ch4_file,
              'nmvoc_path':nmvoc_file_alt,
              'antr_file':antr_file,
              'bb_file':bb_file}
sh2_1 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths_test)
sh2_1.scale_emissions_antr(31.58)
sh2_1.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
plot_results()

###############################################################
setup='constant BB emis and alternative voc'

paths_test = {'meth_path': ch4_file,
              'nmvoc_path':nmvoc_file_alt,
              'antr_file':antr_file,
              'bb_file':'../input/bb_emis_constant.csv'}
sh2_1 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths_test)
sh2_1.scale_emissions_antr(31.58)
sh2_1.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
plot_results()



axs[0].set_ylim(bottom=0)
axs[1].set_ylim(bottom=200)
axs[0].legend()

axs[0].set_xlabel("Years")
axs[1].set_xlabel("Years")
axs[1].set_ylabel("H2 [ppb]")
axs[0].set_ylabel("Total production H2 [Tg/yr]")

xlim = [startyr,endyr]
axs[0].set_xlim(xlim)
axs[1].set_xlim(xlim)


plt.show()
