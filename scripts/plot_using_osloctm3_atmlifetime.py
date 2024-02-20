import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import io

from simpleh2 import SIMPLEH2

def plot_results():
    #Function that plot input and results for each model
    axs[0,0].plot(sh2.h2_prod_emis["h2_antr"],'-', color=mcol, linewidth =1.5,label=model)
    axs[0,1].plot(sh2.h2_prod_emis["h2_prod_ch4"]+
                  sh2.h2_prod_emis["h2_prod_nmvoc"],
                  '-',color=mcol, linewidth =1.5,label=test)
    
    axs[1,0].plot(sh2.h2_prod_emis["h2_antr"]
                  + sh2.h2_prod_emis["h2_bb_emis"]
                  +nit_fix,'-', color=mcol, linewidth=1.5,label=test)
    
    axs[1,1].plot(sh2.conc_h2,'-', linewidth =1.5,color=mcol,label=test)

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


    
#Read model results to be used in the simple hydrogen model.    
df_budget = read_model_results()

model = 'OSLOCTM3-emi'
df_budget.loc[model]['H2 burden [Tg]']= 204.6 
df_budget.loc[model]['H2 atm prod [Tg/yr]'] = 55.80309789
df_budget.loc[model]['H2 soil sink lifetime [yrs]'] =3.526146997
df_budget.loc[model]['H2 atm lifetime [yrs]'] = 7.014149379
df_budget.loc[model]['H2 estimated emissions [Tg/yr]'] = 32.24252915
print(df_budget.loc['OSLOCTM3-emi'])


df_budget_preind = df_budget.copy()
df_budget_preind.loc[model]['H2 burden [Tg]']= 122.8
df_budget_preind.loc[model]['H2 atm prod [Tg/yr]'] = 32.31030702
df_budget_preind.loc[model]['H2 soil sink lifetime [yrs]'] =3.528483728
df_budget_preind.loc[model]['H2 atm lifetime [yrs]'] = 6.990632131
df_budget_preind.loc[model]['H2 estimated emissions [Tg/yr]'] = 20.8365481

print(df_budget_preind.loc['OSLOCTM3-emi'])


           
color_list = ['C0','C1','C2','C3','C4','C5','C6','C7']
model_list = ['OSLOCTM3-emi'] # df_budget.index

df_surfconc = read_model_results_concentrations()
print(df_surfconc)
df_surfconc.loc[model] = 559.0
df_surfconc_preind = df_surfconc.copy()
df_surfconc_preind.loc[model] = 337.0


#h2_file = '../input/h2_antr_ceds17.csv'
#startyr = 1850
#endyr = 2019

antr_file = '../input/h2_antr_ceds21.csv'
ch4_file = '../input/ch4_historical.csv'
bb_file = '../input/bb_emis_gfed.csv'
nmvoc_file = '../input/nmvoc_emis_ssp245.csv'
startyr = 1850
endyr = 2019


#Input filepaths to be used:
paths = {'meth_path': ch4_file,
         'nmvoc_path':nmvoc_file,
         'antr_file':antr_file,
         'bb_file':bb_file}

#Specify nitrate fixation:
nit_fix = 9.0


beta_models = df_budget['H2 burden [Tg]']/df_surfconc
print(beta_models[model])


fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

#
#beta_h2 = 0.37
#beta_h2 =  0.37 #5.1352e9 * 2.0 / 28.97 * 1e-9
#beta_h2 = 5117248794.956313* 2.0 / 28.97 * 1e-9
beta_h2 = beta_models[model]
print(beta_h2)

frac_voc_org = 18.0/41.1
print(frac_voc_org)
frac_voc_org_fabien = 0.297

test = 'constant OH'
for m,model in enumerate(model_list):
    mcol = color_list[m]
    pam_dict ={"refyr": 2010,
               "pre_ind_conc": 340.0,
               "prod_ref": df_budget.loc[model]['H2 atm prod [Tg/yr]'],
               "tau_2": df_budget.loc[model]['H2 soil sink lifetime [yrs]'],
               "tau_1": df_budget.loc[model]['H2 atm lifetime [yrs]'],
               "nit_fix": nit_fix,
               "beta_h2": beta_h2,
               "frac_voc_org":frac_voc_org,
               "beta_h2": beta_models[model]}
                  
    sh2 = SIMPLEH2(pam_dict=pam_dict ,paths=paths)
    print(sh2.paths)

    #Scale only the anthropogenic emissions to match the estimated emissions in the models.
    sh2.scale_emissions_antr(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])

    #Calculate the H2 concentrations
    sh2.calculate_concentrations(const_oh=1,startyr=startyr,endyr=endyr)

    #Plot the results:
    plot_results()
    
    axs[1,0].plot([2010],df_budget.loc[model]['H2 estimated emissions [Tg/yr]'],'x', color=mcol)
    axs[0,1].plot([2010],df_budget.loc[model]['H2 atm prod [Tg/yr]'],'x', color=mcol)
    axs[1,1].plot([2010],df_surfconc.loc[model],'x',color=mcol, label='OsloCTM3 present day and pre ind')


    axs[1,0].plot([1850],df_budget_preind.loc[model]['H2 estimated emissions [Tg/yr]'],'x', color=mcol)
    axs[0,1].plot([1850],df_budget_preind.loc[model]['H2 atm prod [Tg/yr]'],'x', color=mcol)
    axs[1,1].plot([1850],df_surfconc_preind.loc[model],'x',color=mcol)

    test = 'variable OH '
    mcol = color_list[m+1]
    pam_dict ={"refyr": 2010,
               "pre_ind_conc": 340.0,
               "prod_ref": df_budget.loc[model]['H2 atm prod [Tg/yr]'],
               "tau_2": df_budget.loc[model]['H2 soil sink lifetime [yrs]'],
               "tau_1": df_budget.loc[model]['H2 atm lifetime [yrs]'],
               "nit_fix": nit_fix,
               "beta_h2": beta_h2,
               "frac_voc_org":frac_voc_org,
               "beta_h2": beta_models[model]}
                  
    sh2 = SIMPLEH2(pam_dict=pam_dict ,paths=paths)
    print(sh2.paths)

    #Scale only the anthropogenic emissions to match the estimated emissions in the models.
    sh2.scale_emissions_antr(df_budget.loc[model]['H2 estimated emissions [Tg/yr]'])

    #Calculate the H2 concentrations
    sh2.calculate_concentrations(const_oh=0,startyr=startyr,endyr=endyr)

   
   
    
    #Plot the results:
    plot_results()
    
axs[1,0].set_xlabel("Years")
axs[1,1].set_xlabel("Years")

axs[0,0].set_ylabel("Anthropogenic [Tg/yr]")
axs[0,0].set_title('Anthropogenic emissions')

axs[1,0].set_ylabel("Total emissions [Tg/yr]")
axs[1,0].set_title('Total emissions')

axs[0,1].set_ylabel("Atmospheric production (Tg/yr)")
axs[0,1].set_title('Atmospheric production')

axs[1,1].set_ylabel("H2 [ppb]")
axs[1,1].set_title("H2 concentrations")

axs[0,0].legend()
axs[1,1].legend()

xlim = [1850,2019]
axs[0,0].set_xlim(xlim)
axs[1,0].set_xlim(xlim)
axs[0,1].set_xlim(xlim)
axs[1,1].set_xlim(xlim)

axs[0,0].set_ylim(bottom=0)
axs[1,0].set_ylim(bottom=0)
axs[0,1].set_ylim(bottom=0)
axs[1,1].set_ylim(bottom=200)

plt.show()
