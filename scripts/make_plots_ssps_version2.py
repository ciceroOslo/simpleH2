import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
    axs[0,0].plot(sh2_1.h2_prod_emis["h2_antr"],'--', linewidth=lw,color=scen_color[sc])
    axs[0,0].plot(sh2_1.h2_prod_emis["h2_leak"],'--', linewidth=lw,color=scen_color[sc])

    axs[1,0].plot(tot_emis,'-', linewidth=lw,color=scen_color[sc])

    #Plot production
    axs[0,1].plot(sh2_1.h2_prod_emis["h2_prod_ch4"],'-', linewidth=lw,color=scen_color[sc])
    axs[0,1].plot(sh2_1.h2_prod_emis["h2_prod_nmvoc"],'--', linewidth=lw,color=scen_color[sc])

    #Plot total production and emissions.
    
    axs[1,0].plot(tot_atm_prod,'--', linewidth=lw,color=scen_color[sc])

    #Plot concentrations
    axs[1,1].plot(sh2_1.conc_h2,'-', linewidth=lw,label=scen_list[scen])



scen_list = {'ssp119':'SSP1-1.9',
             'ssp126':'SSP1-2.6',
             'ssp245':'SSP2-4.5',
             #'ssp370':'SSP3-7.0',
             #'ssp370-lowNTCF':'SSP3-7.0 LowNTCF',
             'ssp434':'SSP4-3.4',
             'ssp460':'SSP4-6.0',
             #'ssp534-over':'SSP5-3.4-over',
             'ssp585':'SSP5-8.5'}

scen_color = ['C0','C1','C2','C3','C4','C5','C6','C7','C8']

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

leakrate_list = [0.1,0.05,0.01,0]

fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))


fig2, ax = plt.subplots(nrows=4,ncols=2,sharex=True,sharey=True,squeeze=True,figsize=(12,20))
lw = 1.0

ch4_list = [True,False]
for ch4 in ch4_list:
    for sc,scen in enumerate(scen_list):
  
        
        antr_file = '../input/co_emis_'+scen+'.csv'
        if ch4:
            ch4_file = '../input/ch4_conc_'+scen+'.csv'
            ax1=0
            ax[0,ax1].set_title('Methane following the scenario')
        else:
            ch4_file = '../input/ch4_conc_'+'ssp434'+'.csv'
            ax1=1
            ax[0,ax1].set_title('Methane following SSP4-3.4')
        
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

        for l,leakrate in enumerate(leakrate_list):
            ax2=l
            sh2_1.h2_prod_emis["h2_leak"] = 0.0
            if(scen in hydrogen_mass_field.columns):
                sh2_1.h2_prod_emis["h2_leak"].loc[hydrogen_mass_field.index] = hydrogen_mass_field[scen].multiply(leakrate)
            else:
                print('No H2 energy')
            

    
    
            sh2_1.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)
        
            plot_results()


            #Plot concentrations
            ax[ax2,ax1].plot(sh2_1.conc_h2,'-', linewidth=lw,label=scen_list[scen])
            ax[ax2,ax1].text(1960,1100,'Leakage rate ' + str(leakrate))

xlim = [1950,endyr]
ax[0,0].set_xlim(xlim)
ax[3,0].legend(ncol=2,loc='lower left',frameon=False)

ax[0,0].set_ylabel("H2 [ppb]")
ax[1,0].set_ylabel("H2 [ppb]")
ax[2,0].set_ylabel("H2 [ppb]")
ax[3,0].set_ylabel("H2 [ppb]")


axs[0,0].set_title('Anth. and bio. burning emissions (--), Leakages (-)')
axs[0,1].set_title('Atm. production CH4 (-) and NMVOC (--)')
axs[1,0].set_title('Total emissions (-) and total atm production (--)')
axs[1,1].set_title('H2 concentrations')


axs[0,0].set_ylim(bottom=0)
axs[0,0].set_xlabel("Years")
axs[0,0].set_ylabel("Emissions [Tg/yr]")


axs[0,1].set_ylim(bottom=0)
axs[0,1].set_xlabel("Years")
axs[0,1].set_ylabel("Production [Tg/yr]")

axs[1,0].set_ylim(bottom=0)
axs[1,0].set_xlabel("Years")
axs[1,0].set_ylabel("Production [Tg/yr]")


#axs[1,1].legend(ncol=2)


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


plt.show()
