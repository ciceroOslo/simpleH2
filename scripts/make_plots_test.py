import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append('/div/no-backup/users/ragnhibs/simpleH2/simpleH2/src/simpleh2/')

from simpleh2 import SIMPLEH2


sh2 = SIMPLEH2()
print(sh2.conc_ch4.head)


sh2.calculate_concentrations()

startyr = 1850
endyr = 2019

nit_fix = 9.0
pam_dict_osloctm ={"refyr": 2010,
                   "pre_ind_conc": 350.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}

sh2_test_2 = SIMPLEH2(pam_dict=pam_dict_osloctm, ceds21=True)

#print(sh2_test_2.ch4_lifetime_fact)
#exit()

sh2_test_2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
#iso1 = sh2.calc_isotope_timeseries()
#iso2 = sh2_test_2.calc_isotope_timeseries(const_oh=1)

print('Done calculations!')

print("Concentration is", sh2.conc_h2)
print(sh2_test_2.h2_antr)

fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

#Plot production/emissions:
axs[0,0].plot(sh2_test_2.h2_antr,'-', linewidth =2,label='Anthr. em.')
axs[0,0].plot(sh2_test_2.h2_gfed,'-', linewidth =2,label='BB. em.')
axs[0,0].plot([startyr,endyr],[nit_fix,nit_fix],'-', linewidth =2,label='Nitrate fixation (ocean and land)')
axs[0,0].plot(sh2_test_2.h2_prod_ch4,'-', linewidth =2,label='Prod (ch4)')
axs[0,0].plot(sh2_test_2.h2_prod_nmvoc,'-', linewidth =2,label='Prod (nmvoc)')
#axs[0,0].plot(h2_prod_ch4_alt,'--', linewidth =2,label='Prod (ch4) alt')
axs[0,0].set_xlabel("Years")
axs[0,0].set_ylabel("Emissions/Production [Tg/yr]")
axs[0,0].set_title('H2')
axs[0,0].legend()



tot_prod = sh2_test_2.h2_antr.loc[startyr:endyr] + sh2_test_2.h2_gfed.loc[startyr:endyr] + sh2_test_2.h2_prod_ch4.loc[startyr:endyr] +sh2_test_2.h2_prod_nmvoc.loc[startyr:endyr] 
print(tot_prod.index.values)

tot_emis = sh2_test_2.h2_antr.loc[startyr:endyr] + sh2_test_2.h2_gfed.loc[startyr:endyr] + nit_fix
tot_atm_prod = sh2_test_2.h2_prod_ch4.loc[startyr:endyr] +sh2_test_2.h2_prod_nmvoc.loc[startyr:endyr]



#Plot total production and emissions.
axs[0,1].plot(tot_prod,'-', linewidth =2,label='Total production')
#axs[0,1].plot(startyr,prod_pre_ind,'d',color='C0')
axs[0,1].plot(tot_atm_prod,'-', linewidth =2,label='Total atm. production')
axs[0,1].plot(tot_emis,'-', linewidth =2,label='Total emissions')

#OsloCTM check:
pre_ind_conc_ctm = 327.0
prod_pre_ind = 32.5
emis_pre_ind = 18.32
axs[0,1].plot([1850,2010],[prod_pre_ind,56.3],'x', linewidth =2,label='OsloCTM')
axs[0,1].plot([1850,2010],[emis_pre_ind,31.6],'x', linewidth =2,label='OsloCTM')



axs[0,1].set_ylim(bottom=0)
axs[0,1].legend()

axs[1,0].plot(sh2.conc_h2,'-', linewidth =2,label='Concentration')
axs[1,0].plot(sh2_test_2.conc_h2,'-', linewidth =2,label='Concentration')
#axs[1,0].set_xlim([startyr,endyear])
axs[1,0].set_xlabel("Years")
axs[1,0].set_ylabel("H2 [ppb]")

plt.show()
