import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from simpleh2 import SIMPLEH2

def plot_results(setup, plot_tot_prod=True):
    tot_prod = sh2.h2_prod_emis.loc[startyr:endyr].sum(axis=1) + nit_fix

    
    #Plot total production and emissions.
    if plot_tot_prod:
        axs[0].plot(tot_prod,'-', linewidth =1,label=setup)
    axs[1].plot(sh2.conc_h2,'-', linewidth =1,label=setup)
    

    


startyr = 1850
endyr = 2020
ceds_versions = {"ceds17":2014, "ceds21":2019, "ceds24":2022}
ch4_file = '../input/ch4_historical.csv'
bb_file = '../input/bb_emis_gfed.csv'

#Specify nitrate fixation:
nit_fix = 9.0

pam_dict_osloctm_org ={"refyr": 2010,
                   "pre_ind_conc": 350.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}

fig, axs = plt.subplots(nrows=1,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

for ceds_version,endyr in ceds_versions.items():
    antr_file = f'../input/h2_antr_{ceds_version}.csv'
    nmvoc_file = f'/home/masan/make_emissions_data/nmvoc_emis_{ceds_version}.csv'

    #Input filepaths to be used:
    paths = {'meth_path': ch4_file,
             'nmvoc_path':nmvoc_file,
             'antr_file':antr_file,
            'bb_file':bb_file}

    setup='const_oh'
    print(setup)

    sh2 = SIMPLEH2(pam_dict=pam_dict_osloctm_org,paths=paths)
    sh2.scale_emissions_antr(31.58)
    sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
    plot_results(f"{setup}_{ceds_version}")

    ###############################
    setup='osloctm3_oh'
    print(setup)
    sh2.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
    plot_results(f"{setup}_{ceds_version}", plot_tot_prod=False)

    ###############################
    setup='tar_oh'
    print(setup)
    sh2.calculate_concentrations(const_oh=2,startyr=startyr,endyr=endyr)
    plot_results(f"{setup}_{ceds_version}", plot_tot_prod=False)


#xlim = [startyr,endyr]
xlim = [1970,2020]
axs[0].set_xlim(xlim)
axs[1].set_xlim(xlim)

axs[0].set_ylim(bottom=0)
axs[1].set_ylim(bottom=450)
#axs[1].set_ylim(bottom=200)
axs[0].legend()
axs[1].legend()

axs[0].set_xlabel("Years")
axs[1].set_xlabel("Years")
axs[1].set_ylabel("H2 [ppb]")
axs[0].set_ylabel("Total production H2 [Tg/yr]")




plt.savefig("ceds_h2_comparison.png")
