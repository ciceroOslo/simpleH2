import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



bb_file  =  "/div/qbo/hydrogen/OsloCTM3/lilleH2/emission/gfed_h2.txt"
h2_bb_emis_org = pd.read_csv(bb_file, index_col=0)
h2_bb_emis_org.index.name = "Year"

h2_bb_emis_temp["Emis"][:] = h2_bb_emis_org["Emis"].mean()
h2_bb_emis_out =  h2_bb_emis_temp.loc[:1996].append(h2_bb_emis_org)

print(h2_bb_emis_out)

