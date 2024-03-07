import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import sys


from simpleh2 import SIMPLEH2


def plot_results():
    #Calculate totals:
    
    tot_prod = sh2_1.h2_prod_emis.loc[startyr:endyr].sum(axis=1) + nit_fix

    tot_emis = (sh2_1.h2_prod_emis["h2_antr"].loc[startyr:endyr] +
                sh2_1.h2_prod_emis["h2_bb_emis"].loc[startyr:endyr] +
                sh2_1.h2_prod_emis["h2_leak"].loc[startyr:endyr] +
                nit_fix)
    
    tot_atm_prod = (sh2_1.h2_prod_emis["h2_prod_ch4"].loc[startyr:endyr] +
                    sh2_1.h2_prod_emis["h2_prod_nmvoc"].loc[startyr:endyr])
                         
    
    #Plot emissions
    axs[0,0].plot(sh2_1.h2_prod_emis["h2_antr"],'--', linewidth=lw,color=scens_colors[scen])
    axs[0,0].plot(sh2_1.h2_prod_emis["h2_leak"],'--', linewidth=lw,color=scens_colors[scen])

    axs[1,0].plot(tot_emis,'-', linewidth=lw,color=scens_colors[scen])

    #Plot production
    axs[0,1].plot(sh2_1.h2_prod_emis["h2_prod_ch4"],'-', linewidth=lw,color=scens_colors[scen])
    axs[0,1].plot(sh2_1.h2_prod_emis["h2_prod_nmvoc"],'--', linewidth=lw,color=scens_colors[scen])

    #Plot total production and emissions.
    
    axs[1,0].plot(tot_atm_prod,'--', linewidth=lw,color=scens_colors[scen])

    #Plot concentrations
    axs[1,1].plot(sh2_1.conc_h2,'-', linewidth=lw,color=scens_colors[scen],label=scen_list[scen])



scen_list = {'ssp119':'SSP1-1.9',
             'ssp126':'SSP1-2.6',
             'ssp245':'SSP2-4.5',
             'ssp370':'SSP3-7.0',
             #'ssp370-lowNTCF':'SSP3-7.0 LowNTCF',
             'ssp434':'SSP4-3.4',
             'ssp460':'SSP4-6.0',
             'ssp534-over':'SSP5-3.4-over',
             'ssp585':'SSP5-8.5'}

scens_colors = {'ssp119':"#1e9684", 
                'ssp126':"#1d3354",
                'ssp245':"#ead33d",
                'ssp370':"#f21111",
                'ssp370-lowNTCF':"pink",
                'ssp434':"#63bde5", 
                'ssp460':"#e88831", 
                'ssp534-over':"#9a6dc9", 
                'ssp585':"#840b12"}
#scen_color = ['C0','C1','C2','C3','C4','C5','C6','C7','C8']

startyr = 1850
endyr = 2100

#Specify nitrate fixation:
nit_fix = 9.0


pam_dict_osloctm ={"refyr": 2010,
                   "pre_ind_conc": 350.0,
                   "prod_ref": 56.3,
                   "tau_2": 3.3,
                   "tau_1": 6.9,
                   "nit_fix": nit_fix}


hydrogen_mass_field = pd.read_csv('../input/hydrogen_mass_ssps.csv',index_col=0)
print(hydrogen_mass_field)

leakrate_max = 0.1

#fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))


fig2, ax = plt.subplots(nrows=1,ncols=2,sharex=True,sharey=True,squeeze=True)
lw = 1.0

ch4_list = [True,False]
const_oh_val = [1,2]
markings = ['-', '-', ':']
fig2.suptitle('OH constant, methane dependent or according to TAR varrying', fontweight="bold")
ax[0].set_title('CH4 from scenario')
ax[1].set_title('CH4 from ssp434')
for i, ch4 in enumerate(ch4_list):
    
    for sc,scen in enumerate(scen_list):
  
        antr_file = '../input/h2_emis_'+scen+'.csv'    
        if ch4: 
            ch4_file = '../input/ch4_conc_'+scen+'.csv'
        else:
            ch4_file = '../input/ch4_conc_ssp434.csv'
        bb_file = '../input/bb_emis_zero.csv'
        nmvoc_file = '../input/nmvoc_emis_'+scen+'.csv'

        #Input filepaths to be used:
        paths = {'meth_path': ch4_file,
                 'nmvoc_path':nmvoc_file,
                 'antr_file':antr_file,
                 'bb_file':bb_file}


        sh2_1 = SIMPLEH2(pam_dict=pam_dict_osloctm,paths=paths)


        sh2_1.scale_emissions_antr(31.58)
        
        print(sh2_1.h2_prod_emis)
            
        for const_oh in const_oh_val:
            sh2_1.h2_prod_emis["h2_leak"] = 0
            sh2_1.calculate_concentrations(const_oh=const_oh,startyr=startyr,endyr=endyr)
        
            #plot_results()
            #Plot concentrations
            no_leak = sh2_1.conc_h2["H2"].to_numpy().copy()
            print(no_leak[-1])
            ax[i].plot(sh2_1.conc_h2,markings[const_oh], color=scens_colors[scen], linewidth=lw,label=scen_list[scen])
            if i == 1 or const_oh == 1:
                continue
            if scen in hydrogen_mass_field.columns:
                sh2_1.h2_prod_emis["h2_leak"].loc[hydrogen_mass_field.index] = hydrogen_mass_field[scen].multiply(leakrate_max)
                sh2_1.calculate_concentrations(const_oh=const_oh,startyr=startyr,endyr=endyr)
                print(sh2_1.conc_h2["H2"].to_numpy()[-1])
                print(no_leak[-1])
                ax[i].fill_between(sh2_1.conc_h2.index, sh2_1.conc_h2["H2"].to_numpy(), no_leak, alpha=0.4, color=scens_colors[scen], linewidth=lw,label=scen_list[scen])
            


xlim = [1950,endyr]
for i in range(len(ax)):
    ax[i].set_xlim(xlim)
    #ax[i].legend(ncol=3,loc='lower left',frameon=False)
    ax[i].set_title(f"{chr(i+97)})", fontsize=10, loc='left')
    ax[i].set_ylabel("H2 [ppb]")
    #axs[1,1].set_title('H2 concentrations')


    ax[i].set_ylim(bottom=300)
    ax[i].set_xlabel("Years")

#axs[1,1].legend(ncol=2)
custom_lines = [Line2D([0], [0], color=scens_colors[scen], lw=4) for scen in scen_list]
ax[1].legend(custom_lines, scen_list)
#plt.show()
plt.savefig("different_oh_lifetime_evolutions_ch4.png")
sys.exit(4)
#OsloCTM check:
pre_ind_conc_ctm = 327.0
prod_pre_ind = 32.5
emis_pre_ind = 18.32
axs[1,0].plot([1850,2010],[prod_pre_ind,56.3],'x', linewidth =2,label='OsloCTM')
axs[1,0].plot([1850,2010],[emis_pre_ind,31.6],'x', linewidth =2,label='OsloCTM')

axs[1,1].plot([1850],[pre_ind_conc_ctm],'x', linewidth =2,label='OsloCTM')


#axs[1,0].plot(sh2.conc_h2,'-', linewidth =2,label='Concentration')

#axs[1,0].set_xlim([startyr,endyear])



xlim = [1950,endyr]
axs[0,0].set_xlim(xlim)
axs[1,0].set_xlim(xlim)
axs[0,1].set_xlim(xlim)
axs[1,1].set_xlim(xlim)



