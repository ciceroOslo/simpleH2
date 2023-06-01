import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import requests
import io

sys.path.append('/div/no-backup/users/ragnhibs/simpleH2/simpleH2/src/simpleh2/')

from simpleh2 import SIMPLEH2

def plot_results():
    axs[0,0].plot(h2_antr,'-', color=mcol, linewidth =1.5,label=model)
    axs[0,1].plot(sh2.h2_prod_ch4+sh2.h2_prod_nmvoc,'-',color=mcol, linewidth =1.5,label=model)
    axs[1,0].plot(h2_antr+sh2.h2_bb_emis+nit_fix,'-', color=mcol, linewidth =1.5,label=model)
    axs[1,1].plot(sh2.conc_h2,'-', linewidth =1.5,color=mcol,label=model)

#Read budget values from github: 2010 values for the different models.    
url = "https://raw.githubusercontent.com/ciceroOslo/Hydrogen_GWP/main/output/table_budget_h2.csv"
s = requests.get(url).content
df_budget = pd.read_csv(io.StringIO(s.decode('utf-8')),index_col=0)
print(df_budget)

#Add UCI:
df_budget_uci = pd.DataFrame(index=['UCI'],columns=df_budget.columns)
df_budget_uci['H2 burden [Tg]'] = 183.6458 #181.708
df_budget_uci['H2 atm loss [Tg/yr]'] = 22.04 #21.547
df_budget_uci['H2 atm prod [Tg/yr]'] = 50.67 #51.601
df_budget_uci['H2 soil sink [Tg/yr]'] =  59.2 #59.2
df_budget_uci['H2 estimated emissions [Tg/yr]'] = df_budget_uci['H2 atm loss [Tg/yr]']+df_budget_uci['H2 soil sink [Tg/yr]']- df_budget_uci['H2 atm prod [Tg/yr]']
df_budget_uci['H2 atm lifetime [yrs]'] = df_budget_uci['H2 burden [Tg]']/df_budget_uci['H2 atm loss [Tg/yr]']
df_budget_uci['H2 soil sink lifetime [yrs]']= df_budget_uci['H2 burden [Tg]']/df_budget_uci['H2 soil sink [Tg/yr]']
df_budget_uci['H2 total lifetime [yrs]'] =df_budget_uci['H2 burden [Tg]'] /(df_budget_uci['H2 soil sink [Tg/yr]']+df_budget_uci['H2 atm loss [Tg/yr]'])
df_budget_uci    

df_budget = pd.concat([df_budget,df_budget_uci])
df_budget

color_list = ['C0','C1','C2','C3','C4','C5','C6','C7']
model_list = df_budget.index
print(model_list)


#print(c)    
startyr = 1850
endyr = 2019
h2_antr_org = pd.read_csv('../input/h2_antr_ceds21.csv',index_col=0)
print(h2_antr_org)

#startyr = 1850
#endyr = 2014
#h2_antr_org = pd.read_csv('../input/h2_antr_ceds17.csv',index_col=0)
#print(h2_antr_org)



nit_fix = 9.0



fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))

for m,model in enumerate(model_list):
    mcol = color_list[m]
    pam_dict ={"refyr": 2010,
               "pre_ind_conc": 350.0,
               "prod_ref": df_budget.loc[model]['H2 atm prod [Tg/yr]'],
               "tau_2": df_budget.loc[model]['H2 soil sink lifetime [yrs]'],
               "tau_1": df_budget.loc[model]['H2 atm lifetime [yrs]'],
               "nit_fix": nit_fix}
              
    
    h2_emis_antr_model = df_budget.loc[model]['H2 estimated emissions [Tg/yr]']-nit_fix-9.0
    print(h2_emis_antr_model)
    scale_factor_antr = h2_emis_antr_model/h2_antr_org.loc[2010]
    h2_antr = h2_antr_org*scale_factor_antr
    sh2 = SIMPLEH2(pam_dict=pam_dict ,ceds21=True)
    sh2.calculate_concentrations(const_oh=0,h2_antr_emi=h2_antr,startyr=startyr,endyr=endyr)
    plot_results()
    axs[1,0].plot([2010],df_budget.loc[model]['H2 estimated emissions [Tg/yr]'],'x', color=mcol)
    axs[0,1].plot([2010],df_budget.loc[model]['H2 atm prod [Tg/yr]'],'x', color=mcol)


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
#axs[0,1].legend()
#axs[1,0].legend()
axs[1,1].legend()

xlim = [1970,2019]
axs[0,0].set_xlim(xlim)
axs[1,0].set_xlim(xlim)
axs[0,1].set_xlim(xlim)
axs[1,1].set_xlim(xlim)

axs[0,0].set_ylim(bottom=0)
axs[1,0].set_ylim(bottom=0)
axs[0,1].set_ylim(bottom=0)
axs[1,1].set_ylim(bottom=400)

plt.show()
