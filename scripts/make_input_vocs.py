import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read_inputfile(input_file, cut_years=False, year_start=1750, year_end=2100):
    """
    Read input from emissions or concentrations file

    Parameters
    ----------
    input_file : str
              Path to file to be read in
    cut_years : bool
             If unused years are to be cut, this option should
             be set to True, default is False
    year_start : int
             Start year for relevant input, default is 1750
    year_end : int
             End year for relevant input, default is 2100

    Returns
    -------
    pandas.Dataframe
        Dataframe with the intput from the file, possibly cut
        to relevant years
    """
    df_input = pd.read_csv(
        input_file, delim_whitespace=True, index_col=0, skiprows=[1, 2, 3]
    )
    if cut_years:
        min_year = df_input.index[0]
        max_year = df_input.index[0]
        cut_rows = [*range(min_year, year_start), *range(year_end + 1, max_year + 1)]
        df_input.drop(index=cut_rows, inplace=True)
    return df_input


scen_list = {'ssp119':'SSP1-1.9',
             'ssp126':'SSP1-2.6',
             'ssp245':'SSP2-4.5',
             'ssp370':'SSP3-7.0',
             'ssp370-lowNTCF':'SSP3-7.0 LowNTCF',
             'ssp434':'SSP4.3.4',
             'ssp460':'SSP4-6.0',
             'ssp534-over':'SSP5-3.4-over',
             'ssp585':'SSP5-8.5'}

for scen in scen_list:
    filename = '/div/amoc/CSCM/SCM_Linux_v2019/RCMIP/input/'+scen+'_em_RCMIP.txt'
    
    df_input = read_inputfile(filename)
    plt.plot(df_input['NMVOC'].loc[1750:2100],label=scen_list[scen])
    
    out_field = df_input['NMVOC'].loc[1750:2100]
    out_field.name = "Emis"
    out_field.index.name="Years"
    out_field.to_csv('../input/nmvoc_emis_'+scen+'.csv')
    

fileceds17 = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_NMVOC_CEDS17.csv'
fileceds21 = '/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_NMVOC_CEDS17.csv'
emis_ceds17 = pd.read_csv(fileceds17,index_col=0)
emis_ceds21 = pd.read_csv(fileceds21,index_col=0)

plt.plot(emis_ceds17,label='CEDS17',color='red')
plt.plot(emis_ceds21,label='CEDS21',color='blue')


plt.show()
