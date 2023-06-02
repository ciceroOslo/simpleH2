import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
    filename = '/div/amoc/CSCM/SCM_Linux_v2019/RCMIP/input/'+scen+'_conc_RCMIP.txt'
    
    df_input = read_inputfile(filename)
    print(df_input['CH4'].loc[1750:2100])
    plt.plot(df_input['CH4'].loc[1750:2100],label=scen_list[scen])


#Lan, X., K.W. Thoning, and E.J. Dlugokencky: Trends in globally-averaged CH4, N2O, and SF6 determined from NOAA Global Monitoring Laboratory measurements. Version 2023-05, https://doi.org/10.15138/P8XG-AA10

df_obs_ch4 = pd.read_csv('/div/qbo/users/ragnhibs/Hydrogen/Scenarios/historical/ch4_annmean_gl.csv',header=60,index_col=0)
print(df_obs_ch4)

plt.plot(df_obs_ch4['mean'],color='black',label='NOAA')

#plt.xlim([1900,2100])
#plt.xlim([1970,2020])
plt.ylabel('Methane concentration [ppb]')
plt.legend()


df_obs_ch4_extended = df_input['CH4'].loc[:df_obs_ch4.index[0]-1]
print(df_obs_ch4_extended)
df_obs_ch4_extended.index.name = "Year"
df_obs_ch4_extended.columns = ["CH4"]

df_obs_ch4["CH4"]=df_obs_ch4['mean']
df_obs_ch4.index.name="Year"


print(df_obs_ch4_extended)
print(df_obs_ch4["CH4"])
print(pd.concat([df_obs_ch4_extended,df_obs_ch4["CH4"]]))

df_obs_ch4_out = pd.concat([df_obs_ch4_extended,df_obs_ch4["CH4"]])

plt.plot(df_obs_ch4_out,color='Pink')

print(df_obs_ch4['mean'])



df_obs_ch4_out.to_csv('../input/ch4_historical.csv')






plt.show()
