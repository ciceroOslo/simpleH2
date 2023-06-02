import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



bb_file  =  "/div/qbo/hydrogen/OsloCTM3/lilleH2/emission/gfed_h2.txt"
h2_bb_emis_org = pd.read_csv(bb_file, index_col=0)
h2_bb_emis_org.index.name = "Year"

years = np.arange(1750,2101)
print(years)
h2_bb_emis_out = pd.DataFrame([],index=years)


h2_bb_emis_out["Emis"] = h2_bb_emis_org["Emis"]
h2_bb_emis_out["Emis"].loc[:h2_bb_emis_org.index[0]] = h2_bb_emis_org["Emis"].mean()
h2_bb_emis_out["Emis"].loc[h2_bb_emis_org.index[-1]+1:] = h2_bb_emis_org["Emis"].mean()
print(h2_bb_emis_org.index[0])

plt.plot(h2_bb_emis_out)

print(h2_bb_emis_out)

h2_bb_emis_out.to_csv('../input/bb_emis_gfed.csv')
h2_bb_emis_out["Emis"][:] = h2_bb_emis_org["Emis"].mean()
h2_bb_emis_out.to_csv('../input/bb_emis_constant.csv')

plt.show()
