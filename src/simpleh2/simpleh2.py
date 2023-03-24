import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def calc_ch4_lifetime_fact(year):
    lifetime_fact = np.ones(year.size)
    ch4lifetime_fact = pd.DataFrame( {"lifetime_fact": lifetime_fact},index=year)
    anom_year = 2000
    oh_anomaly = 'OsloCTM3'
    oh_run = 'histO3'
    path = '/div/qbo/users/ragnhibs/Methane/OH/OsloCTM3/ForBoxModel/'
    startyr = year[0]
    endyear = year[-1]
    filename_oh = oh_anomaly + '_CH4lifetime_' + oh_run +'.txt'
    lifetime = pd.read_csv(path+filename_oh,delimiter=',',index_col=0)
    lifetime = lifetime.loc[startyr:endyear]
    
    lifetime_ref = lifetime['Lifetime'].loc[anom_year]
    ch4lifetime_fact.loc[lifetime.index]=lifetime/lifetime_ref
    return ch4lifetime_fact



class SIMPLEH2:

    def __init__(self, startyr=1850, endyear=2010, refyr=2010, pre_ind_conc=350.0, prod_ref=75.6, TAU_2=2.4, TAU_1 = 7.2):
        self.pre_ind_conc = pre_ind_conc
        self.tau_2 = 2.4
        self.tau_1 = 7.2
        self.refyr = refyr
        #frac numbers from Ehhalt and Roherer 2009
        frac_voc = 18.0/41.1*prod_ref
        frac_ch4 = (1-frac_voc/prod_ref)*prod_ref
        
        self._prepare_concentrations(meth_path='/div/qbo/users/ragnhibs/Methane/INPUT/ch4_atm_cmip6_upd.txt')
        self._calc_h2_prod_nmvoc(nmvoc_path='/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_NMVOC_CEDS17.csv', frac_voc=frac_voc)
        self.h2_prod_ch4 = self.conc_ch4/self.conc_ch4.loc[self.refyr]*frac_ch4
        self.h2_prod_ch4.columns = ["Emis"]
        self.h2_prod_ch4.index.name = 'Year'
        self._calc_h2_antr_and_gfed()
        
    def _prepare_concentrations(self,meth_path):
        data_conc =  pd.read_csv(meth_path,index_col=0)
        data_conc.index.name = 'Year'
        data_conc.columns = ['CH4']

        #prepare concentration:
        self.conc_ch4 = data_conc.copy()

        self.conc_h2 = data_conc.copy()

        self.conc_h2.columns = ["H2"]
        self.conc_h2["H2"] = -1

    def _calc_h2_prod_nmvoc(self, nmvoc_path, frac_voc):

        
        #Natural emis NMVOC:
        #Sum NMVOC used in the model 2010 and 1850.
        #764.1 vs 648.87, increase since pre-ind: 115.23
        #Increase in total VOC CEDS: 10.77 to 161.06, increase of 150.3
        frac_voc_used = 115.23/150.3
        nat_emis = 648.87 - 10.77*frac_voc_used  #Used in the model
        
        nmvoc_emis = pd.read_csv(nmvoc_path,index_col=0) 
        nmvoc_emis = nmvoc_emis*frac_voc_used 
        self.h2_prod_nmvoc = (nmvoc_emis+nat_emis)/(nat_emis+nmvoc_emis.loc[self.refyr])*frac_voc
        self.h2_prod_nmvoc.index.name = 'Year'

    def _calc_h2_antr_and_gfed(self, ceds21=True):
        scaling_co = 0.47*2.0/28.0
        #scaling_co = 0.39*2.0/28.0
        co_file = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS17.csv'
        co_file1 = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS17.csv'
        co_file2 = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS21.csv'
        
        if ceds21 == True:
            h2_antr1 = pd.read_csv(co_file1,index_col=0)*scaling_co
            h2_antr2 = pd.read_csv(co_file2,index_col=0)*scaling_co
            self.h2_antr = pd.concat([h2_antr1.loc[:1950],h2_antr2.loc[1951:]])
    
        else:
            self.h2_antr = pd.read_csv(co_file,index_col=0)*scaling_co

        self.h2_antr.index.name = 'Year'
        self._calc_h2_gfed(self.h2_antr.copy()*0.0)

    def _calc_h2_gfed(self, h2_gfed_temp, gfedfile = '/div/qbo/hydrogen/OsloCTM3/lilleH2/emission/gfed_h2.txt'):
        h2_gfed_org = pd.read_csv(gfedfile,index_col=0)
        h2_gfed_org.index.name = 'Year'
        h2_gfed_temp.index.name = 'Year'
        h2_gfed_temp['Emis'][:] =  h2_gfed_org['Emis'].mean()
        self.h2_gfed = h2_gfed_temp.loc[:1996].append(h2_gfed_org)

        
    def calculate_concentrations(self, const_oh=0):
        tot_prod = self.h2_antr.loc[1850:2014] + self.h2_gfed.loc[1850:2014] + self.h2_prod_ch4.loc[1850:2014] +self.h2_prod_nmvoc.loc[1850:2014]
        year = tot_prod.index.values
        print(year)
        print(len(self.h2_prod_ch4.loc[1850:2014]))
        
        nit_fix = 5.0

        #Factor converting emissions to mixing ratios (Tg CH4/ppbv)
        Ma = 5.1352e9*2.0/28.97*1e-9
        print(Ma)
        print(0.37)
        print(0.352)

        #Atmospheric mass conversion H2  [Tg/ppb]	0.37
        #*	(Burden H2/surface conc)	
        #Atmospheric mass conversion H2  [Tg/ppb] (based on the perturbations)	0.352
        #(Burden H2/surface conc) Closer to the 0.344 Tg/ppb as Prather stated below.
        #NBNB: Surface conc increased by 10%, burden H2 increased by 9.5%	
        #
        #exit()
        beta_h2 = Ma #2.84
        if const_oh != 1:
            ch4_lifetime_fact = calc_lifetime_fact(year)
        else:
            q = 1./self.tau_1 + 1/self.tau_2
        conc_local = self.pre_ind_conc
        for y in year:
            
            if const_oh != 1:
                q = 1.0/(TAU_1*ch4lifetime_fact.loc[y]) + 1/self.tau_2

            emis = tot_prod['Emis'].loc[y] + nit_fix
            point_conc = emis/beta_h2
            conc_local = point_conc/q + (conc_local  -point_conc/q)*np.exp(-q)

            self.conc_h2.loc[y] = conc_local

    def calc_istope_timeseries(iso_h2_antr=190, iso_h2_gfed=-290, iso_h2_prod_ch4=160, iso_h2_prod_nmvoc=160,iso_h2_fix=-700, frac_soil=0.943,frac_oh=0.58):
        
        tot_prod = self.h2_antr.loc[1850:2014] + self.h2_gfed.loc[1850:2014] + self.h2_prod_ch4.loc[1850:2014] +self.h2_prod_nmvoc.loc[1850:2014]
        year = tot_prod.index.values
        nit_fix = 5.0
        frac_sink = 0.943*0.85+0.58*0.15
        if const_oh != 1:
            ch4_lifetime_fact = calc_lifetime_fact(year)
        else:
            frac_sink = 0.943*
        for y in year:
            em = tot_prod['Emis'].loc[y]  + nit_fix
            iso_sources = (iso_h2_antr*self.h2_antr.loc[year[i]]/em)+(iso_h2_gfed*self.h2_gfed.loc[y]/em)+(iso_h2_prod_ch4*self.h2_prod_ch4.loc[y]/em)+(iso_h2_prod_nmvoc*self.h2_prod_nmvoc.loc[y]/em)+(iso_h2_nit_fix*nit_fix/em)
            iso_atm = 1000*((iso_sources/1000+1)/frac_sink -1)
            
