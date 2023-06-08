import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from simpleh2 import SIMPLEH2

def plot_results():
    tot_prod = sh2.h2_prod_emis.loc[startyr:endyr].sum(axis=1) + nit_fix

    
    #Plot total production and emissions.
    axs[0].plot(tot_prod,'-', linewidth =1,label=setup)
    axs[1].plot(sh2.conc_h2,'-', linewidth =1,label=setup)
    

    


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
print(setup)
pam_dict_osloctm_org ={"refyr": 2010,
                   "pre_ind_conc": 350.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}

sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm_org,paths=paths)
sh2.scale_emissions_antr(31.58)
sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
plot_results()

###############################
setup='const OH = 0'
print(setup)
sh2.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
plot_results()

###############################################################
setup='pre_ind_lower'
print(setup)
pam_dict_osloctm ={"refyr": 2010,
                   "pre_ind_conc": 250.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}

sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths)
sh2.scale_emissions_antr(31.58)
sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
plot_results()

###############################################################
#setup='alternative nmvoc'
#print(setup)
#
#nmvoc_file_alt = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_NMVOC_CEDS17.csv'
#paths_test = {'meth_path': ch4_file,
#              'nmvoc_path':nmvoc_file_alt,
#              'antr_file':antr_file,
#              'bb_file':bb_file}
#sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths_test)
#sh2.scale_emissions_antr(31.58)
#sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
#plot_results()

###############################################################
setup='constant BB emis'
print(setup)

paths_test = {'meth_path': ch4_file,
              'nmvoc_path':nmvoc_file,
              'antr_file':antr_file,
              'bb_file':'../input/bb_emis_constant.csv'}
sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm_org,paths=paths_test)
sh2.scale_emissions_antr(31.58)
sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
plot_results()

###############
setup='Nat VOC 300'
print(setup)
pam_dict_osloctm_alt ={"refyr": 2010,
                       "pre_ind_conc": 350.0,
                       "prod_ref": 56.3,
                       "tau_2": 3.3,
                       "tau_1": 6.9,
                       "nit_fix": nit_fix,
                       "natvoc":300.0}

sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm_alt,paths=paths)
sh2.scale_emissions_antr(31.58)
sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
plot_results()

###############
setup='Nat VOC 300'
print(setup)
pam_dict_osloctm_alt ={"refyr": 2010,
                       "pre_ind_conc": 350.0,
                       "prod_ref": 56.3,
                       "tau_2": 3.3,
                       "tau_1": 6.9,
                       "nit_fix": nit_fix,
                       "natvoc":900.0}

sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm_alt,paths=paths)
sh2.scale_emissions_antr(31.58)
sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
plot_results()


#xlim = [startyr,endyr]
xlim = [1970,2020]
axs[0].set_xlim(xlim)
axs[1].set_xlim(xlim)

axs[0].set_ylim(bottom=0)
axs[1].set_ylim(bottom=450)
#axs[1].set_ylim(bottom=200)
axs[0].legend()

axs[0].set_xlabel("Years")
axs[1].set_xlabel("Years")
axs[1].set_ylabel("H2 [ppb]")
axs[0].set_ylabel("Total production H2 [Tg/yr]")




plt.show()
