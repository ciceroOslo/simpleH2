import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

co_file = "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS17.csv"
co_file1 = "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS17.csv"
co_file2 = "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS21.csv"

scaling_co_first = 0.34*2.0/28.0

co_antr1 = pd.read_csv(co_file1, index_col=0) #* scaling_co
co_antr2 = pd.read_csv(co_file2, index_col=0) #* scaling_co
co_antr_ceds21 = pd.concat([co_antr1.loc[:1950], co_antr2.loc[1951:]])

ref_value = 14.3
print(co_antr_ceds21/co_antr_ceds21['Emis'].loc[2010]*ref_value)
print(co_antr_ceds21['Emis']*scaling_co_first)
h2_antr_ceds21 = co_antr_ceds21/co_antr_ceds21['Emis'].loc[2010]*ref_value
h2_antr_ceds17 = co_antr1/co_antr1['Emis'].loc[2010]*ref_value
#exit()

#scaling_co = ref_value/co_antr_ceds21['Emis'].loc[2010]
#print('Scaling CO')
#print(scaling_co_first)
#print(scaling_co)
#h2_antr_ceds21 = co_antr_ceds21['Emis']*scaling_co_first

h2_antr_ceds21.index.name = "Year"

print(h2_antr_ceds21)

h2_antr_ceds21.to_csv('/div/no-backup/users/ragnhibs/simpleH2/simpleH2/input/h2_antr_ceds21.csv')
h2_antr_ceds17.to_csv('/div/no-backup/users/ragnhibs/simpleH2/simpleH2/input/h2_antr_ceds17.csv')
plt.plot(h2_antr_ceds21, label='CEDS21')
plt.plot(h2_antr_ceds17, label='CEDS17')
plt.title('Anthropogenic H2 emissions (simple scaling CO)')
plt.legend()
plt.show()
