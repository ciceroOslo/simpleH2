import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import requests
import io


#sys.path.append("/div/no-backup/users/ragnhibs/simpleH2/simpleH2/src/")
sys.path.append("/div/qbo/users/srkri/HYDROGEN/manuscript/h2_simpleboxmodel/src/")


from simpleh2 import SIMPLEH2

def read_model_results():
    #Read budget values from github: 2010 values for the different models.    
    url = "https://raw.githubusercontent.com/ciceroOslo/Hydrogen_GWP/main/output/table_budget_h2.csv"
    s = requests.get(url).content
    df_budget = pd.read_csv(io.StringIO(s.decode('utf-8')),index_col=0)
    print(df_budget)

    return df_budget

def read_model_results_concentrations():
    #Read budget values from github: 2010 values for the different models.    
    url = "https://raw.githubusercontent.com/ciceroOslo/Hydrogen_GWP/main/input/H2_surfconc.txt"
    s = requests.get(url).content
    df_surfconc = pd.read_csv(io.StringIO(s.decode('utf-8')),sep=';',index_col=0)
    df_surfconc['UCI'] = df_surfconc['UKCA']*0.0
    print(df_surfconc)
    return df_surfconc.loc['CTRL']



#Input for simulation

#emis_list = ceds21_sectors, ceds24

#inputpath = '/div/no-backup/users/ragnhibs/simpleH2/simpleH2/input/'
inputpath = '/div/qbo/users/srkri/HYDROGEN/manuscript/h2_simpleboxmodel/input/'

startyr = 1850
endyr = 2019

antr_file_ceds21 = inputpath + 'h2_antr_ceds21_sectors.csv'
antr_file_ceds24 = inputpath + 'h2_antr_ceds24.csv'

ch4_file = inputpath + 'ch4_historical.csv'
bb_file = inputpath + 'bb_emis_gfed.csv'
nmvoc_file = inputpath + 'voc_emis_ssp245.csv'


#Input filepaths to be used:
paths_ceds21 = {'meth_path': ch4_file,
                'nmvoc_path':nmvoc_file,
                'antr_file':antr_file_ceds21,
                'bb_file':bb_file}
paths_ceds24 = {'meth_path': ch4_file,
                'nmvoc_path':nmvoc_file,
                'antr_file':antr_file_ceds24,
                'bb_file':bb_file}

#Specify nitrate fixation:
nit_fix = 9.0


#Model spesific input:
#Read model results to be used in the simple hydrogen model.    

#Specify model:
model = 'OSLOCTM3-emi'

df_budget = read_model_results()
print(df_budget.loc['OSLOCTM3-emi'])
#As the emission driven run is updated compared to what was published in Sand et al
#overwrite the numbers for OsloCTM3-emi.

df_budget.loc[model]['H2 burden [Tg]']= 204.6 
df_budget.loc[model]['H2 atm prod [Tg/yr]'] = 55.80309789
df_budget.loc[model]['H2 soil sink lifetime [yrs]'] =3.526146997
df_budget.loc[model]['H2 atm lifetime [yrs]'] = 7.014149379
df_budget.loc[model]['H2 estimated emissions [Tg/yr]'] = 32.24252915
print(df_budget.loc['OSLOCTM3-emi'])

#Make a similar table for pre-industrial. Numbers from OsloCTM3.
df_budget_preind = df_budget.copy()
df_budget_preind.loc[model]['H2 burden [Tg]']= 122.8
df_budget_preind.loc[model]['H2 atm prod [Tg/yr]'] = 32.31030702
df_budget_preind.loc[model]['H2 soil sink lifetime [yrs]'] =3.528483728
df_budget_preind.loc[model]['H2 atm lifetime [yrs]'] = 6.990632131
df_budget_preind.loc[model]['H2 estimated emissions [Tg/yr]'] = 20.8365481

print(df_budget_preind.loc['OSLOCTM3-emi'])

df_surfconc = read_model_results_concentrations()
print(df_surfconc)
df_surfconc.loc[model] = 559.0
df_surfconc_preind = df_surfconc.copy()
df_surfconc_preind.loc[model] = 337.0


beta_models = df_budget['H2 burden [Tg]']/df_surfconc
print(beta_models)
print(beta_models[model])
print(5.1352e9*2.0/28.97*1e-9)


beta_h2 = beta_models[model]
print(beta_h2)


frac_voc_org = 18.0/41.1
#print(frac_voc_org)
frac_voc_org_fabien = 0.297  #Fabien

pam_dict ={"refyr": 2010,
           "pre_ind_conc": 340.0,
           "prod_ref": df_budget.loc[model]['H2 atm prod [Tg/yr]'],
           "tau_2": df_budget.loc[model]['H2 soil sink lifetime [yrs]'],
           "tau_1": df_budget.loc[model]['H2 atm lifetime [yrs]'],
           "nit_fix": nit_fix,
           "beta_h2": beta_h2,
           "frac_voc_org":frac_voc_org,
           "beta_h2": beta_models[model]}

pam_dict_ceds24 = pam_dict.copy()

sh2_ceds21 = SIMPLEH2(pam_dict=pam_dict ,paths=paths_ceds21)
print(sh2_ceds21.pam_dict["nit_fix"])
sh2_ceds21.scale_emissions_nitrfix(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])
print(sh2_ceds21.pam_dict["nit_fix"])
sh2_ceds21.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)

sh2_ceds24 = SIMPLEH2(pam_dict=pam_dict_ceds24 ,paths=paths_ceds24)
print(sh2_ceds21.pam_dict["nit_fix"])
sh2_ceds24.scale_emissions_nitrfix(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])
print(sh2_ceds21.pam_dict["nit_fix"])
sh2_ceds24.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)


#Scale only the anthropogenic emissions to match the estimated emissions in the models.
#sh2_ceds21.scale_emissions_antr(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])
#sh2_ceds24.scale_emissions_antr(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])
#sh2_ceds21.scale_emissions_nitrfix(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])
#sh2_ceds24.scale_emissions_nitrfix(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])








#Plot results:

fig, axs = plt.subplots(nrows=1,ncols=3,squeeze=True,figsize=(12,6))

lw = 1
#CEDS21
lstyle = '-'

tot_prod_ceds21 = sh2_ceds21.h2_prod_emis.loc[startyr:endyr].sum(axis=1) + sh2_ceds21.pam_dict["nit_fix"]

tot_emis_ceds21 = (sh2_ceds21.h2_prod_emis["h2_antr"].loc[startyr:endyr] +
                   sh2_ceds21.h2_prod_emis["h2_bb_emis"].loc[startyr:endyr] +
                   sh2_ceds21.pam_dict["nit_fix"])

tot_atm_prod_ceds21= (sh2_ceds21.h2_prod_emis["h2_prod_ch4"].loc[startyr:endyr] +
                      sh2_ceds21.h2_prod_emis["h2_prod_nmvoc"].loc[startyr:endyr])

    
#Plot emissions

axs[0].plot(sh2_ceds21.h2_prod_emis["h2_antr"],linestyle=lstyle,color='blue', linewidth=lw,label='H$_2$ antr. emis.')
axs[0].plot(sh2_ceds21.h2_prod_emis["h2_bb_emis"],linestyle=lstyle,color='forestgreen', linewidth =lw,label='BB. em. emis.')
axs[0].plot([startyr,endyr],[sh2_ceds21.pam_dict["nit_fix"],sh2_ceds21.pam_dict["nit_fix"]],linestyle=lstyle, color='orange', linewidth =lw,label='Nit. fix. (ocean and land)')
axs[0].plot(sh2_ceds21.h2_prod_emis["h2_prod_ch4"],linestyle=lstyle, color='purple',linewidth =lw,label='Atm. Prod. (CH4)')
axs[0].plot(sh2_ceds21.h2_prod_emis["h2_prod_nmvoc"],linestyle=lstyle, color='darkblue',linewidth =lw,label='Atm. Prod. (NMVOC)')

#Plot total production and emissions.
axs[1].plot(tot_emis_ceds21,linestyle=lstyle, linewidth=lw,color='darkblue',label='Total emissions')
axs[1].plot(tot_atm_prod_ceds21,linestyle=lstyle, linewidth=lw, color='purple',label='Total atm. production')

#Plot concentrations
axs[2].plot(sh2_ceds21.conc_h2,linestyle=lstyle, color='darkgreen', linewidth=lw,label='SimpleH2 (CEDS21)')


#CEDS24
lstyle = '--'

tot_prod_ceds24 = sh2_ceds24.h2_prod_emis.loc[startyr:endyr].sum(axis=1) + sh2_ceds24.pam_dict["nit_fix"]

tot_emis_ceds24 = (sh2_ceds24.h2_prod_emis["h2_antr"].loc[startyr:endyr] +
            sh2_ceds24.h2_prod_emis["h2_bb_emis"].loc[startyr:endyr] +
            sh2_ceds24.pam_dict["nit_fix"])

tot_atm_prod_ceds24= (sh2_ceds24.h2_prod_emis["h2_prod_ch4"].loc[startyr:endyr] +
                sh2_ceds24.h2_prod_emis["h2_prod_nmvoc"].loc[startyr:endyr])

    
#Plot emissions

axs[0].plot(sh2_ceds24.h2_prod_emis["h2_antr"],linestyle=lstyle,color='blue', linewidth=lw) #,label='H$_2$ antr. emis.')
axs[0].plot(sh2_ceds24.h2_prod_emis["h2_bb_emis"],linestyle=lstyle,color='forestgreen', linewidth =lw) #,label='BB. em. emis.')
axs[0].plot([startyr,endyr],[sh2_ceds24.pam_dict["nit_fix"],sh2_ceds24.pam_dict["nit_fix"]],linestyle=lstyle, color='orange', linewidth =lw) #,label='Nit. fix. (ocean and land)')
axs[0].plot(sh2_ceds24.h2_prod_emis["h2_prod_ch4"],linestyle=lstyle, color='purple',linewidth =lw) #,label='Atm. Prod. (CH4)')
axs[0].plot(sh2_ceds24.h2_prod_emis["h2_prod_nmvoc"],linestyle=lstyle, color='darkblue',linewidth =lw) #,label='Atm. Prod. (NMVOC)')

#Plot total production and emissions.
axs[1].plot(tot_emis_ceds24,linestyle=lstyle, linewidth=lw,color='darkblue') #,label='Total emissions')
axs[1].plot(tot_atm_prod_ceds24,linestyle=lstyle, linewidth=lw, color='purple') #,label='Total atm. production')

#Plot concentrations
axs[2].plot(sh2_ceds24.conc_h2,linestyle=lstyle, color='darkgreen', linewidth=lw,label='SimpleH2 (CEDS24)')




#Add OsloCTM3 results
mcol = 'darkgray'

axs[1].plot([2010],df_budget.loc[model]['H2 estimated emissions [Tg/yr]'],'x', color=mcol)
axs[1].plot([2010],df_budget.loc[model]['H2 atm prod [Tg/yr]'],'x', color=mcol, label='OsloCTM3')
axs[2].plot([2010],df_surfconc.loc[model],'x',color=mcol, label='OsloCTM3')


axs[1].plot([1850],df_budget_preind.loc[model]['H2 estimated emissions [Tg/yr]'],'x', color=mcol)
axs[1].plot([1850],df_budget_preind.loc[model]['H2 atm prod [Tg/yr]'],'x', color=mcol)
axs[2].plot([1850],df_surfconc_preind.loc[model],'x',color=mcol)



    
xlim = [1850,2019]
#xlim = [2000,2019]
for i in np.arange(0,3):
    axs[i].set_xlabel("Years")
    axs[i].set_xlim(xlim)
    axs[i].set_ylim(bottom=0)
axs[0].set_title('a)',loc='left')
axs[1].set_title('b)',loc='left')
axs[2].set_title('c)',loc='left')
    
axs[0].set_ylabel("Emissions/Productions [Tg yr$^{-1}$]")
axs[1].set_ylabel("Emissions/Productions [Tg yr$^{-1}$]")
axs[2].set_ylabel("H$_2$ concentration [ppb]")


axs[0].legend(frameon=False)
axs[1].legend(frameon=False)
axs[2].legend(frameon=False)


axs[2].set_ylim(bottom=200)



plt.tight_layout()
plt.show()


print(tot_emis_ceds21.loc[2010])
print(tot_emis_ceds24.loc[2010])
print('Done calculations!')
