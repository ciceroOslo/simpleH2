import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from simpleh2 import SIMPLEH2


def plot_results():
    lw = 1
    tot_prod = sh2_1.h2_prod_emis.loc[startyr:endyr].sum(axis=1) + nit_fix

    tot_emis = (sh2_1.h2_prod_emis["h2_antr"].loc[startyr:endyr] +
                sh2_1.h2_prod_emis["h2_bb_emis"].loc[startyr:endyr] +
                nit_fix)
    
    tot_atm_prod = (sh2_1.h2_prod_emis["h2_prod_ch4"].loc[startyr:endyr] +
                    sh2_1.h2_prod_emis["h2_prod_nmvoc"].loc[startyr:endyr])
                         
    
    #Plot emissions
    axs[0,0].plot(sh2_1.h2_prod_emis["h2_antr"],'--', linewidth=lw,label='H2 antr.')
    axs[0,0].plot(sh2_1.h2_prod_emis["h2_bb_emis"],'-', linewidth =lw,label='BB. em.')
    axs[0,0].plot([startyr,endyr],[nit_fix,nit_fix],'-', linewidth =lw,label='Nitrate fixation (ocean and land)')
    axs[0,0].plot(tot_emis,'-', linewidth=lw,label='Tot emis')

    #Plot production
    axs[0,1].plot(sh2_1.h2_prod_emis["h2_prod_ch4"],'-', linewidth=lw,label='H2 prod CH4')
    axs[0,1].plot(sh2_1.h2_prod_emis["h2_prod_nmvoc"],'--', linewidth=lw,label='H2 prod NMVOC')

    #Plot total production and emissions.
    axs[1,0].plot(tot_prod,'-', linewidth=lw,label='Total production')
    axs[1,0].plot(tot_atm_prod,'--', linewidth=lw,label='Total atm. production')
    axs[1,0].plot(tot_emis,'--', linewidth=lw,label='Total emissions')
    #Plot concentrations
    axs[1,1].plot(sh2_1.conc_h2,'-', linewidth=lw,label='Concentration')

    
startyr = 1850
endyr = 2019
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


pam_dict_osloctm ={"refyr": 2010,
                   "pre_ind_conc": 350.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix,
                   "bb_emis_file":"/div/qbo/hydrogen/OsloCTM3/lilleH2/emission/gfed_h2.txt"}

sh2_1 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths)


sh2_1.scale_emissions_antr(31.58)


sh2_1.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)
#iso1 = sh2.calc_isotope_timeseries()
#iso2 = sh2_test_2.calc_isotope_timeseries(const_oh=1)

print('Done calculations!')


fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

plot_results()

sh2_1.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
axs[1,1].plot(sh2_1.conc_h2,'--', linewidth=1,label='const_oh=1')


print(sh2_1.conc_h2)

axs[0,0].legend()
axs[1,0].legend()
axs[0,1].legend()
axs[1,1].legend()


#Plot production/emissions:
axs[0,0].set_xlabel("Years")
axs[0,0].set_ylabel("Emissions [Tg/yr]")
axs[0,0].set_title('H2')

axs[1,1].set_xlabel("Years")
axs[1,1].set_ylabel("H2 [ppb]")

#OsloCTM check:
pre_ind_conc_ctm = 327.0
prod_pre_ind = 32.5
emis_pre_ind = 18.32
axs[1,0].plot([1850,2010],[prod_pre_ind,56.3],'x', linewidth =2,label='OsloCTM')
axs[1,0].plot([1850,2010],[emis_pre_ind,31.6],'x', linewidth =2,label='OsloCTM')


axs[1,1].plot([1850],[pre_ind_conc_ctm],'x', linewidth =2,label='OsloCTM')

xlim = [startyr,endyr]
xlim = [1980,endyr]
axs[0,0].set_xlim(xlim)
axs[1,0].set_xlim(xlim)
axs[0,1].set_xlim(xlim)
axs[1,1].set_xlim(xlim)
axs[1,1].set_ylim(bottom=500)
plt.show()
exit()










