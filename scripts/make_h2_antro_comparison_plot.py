import pandas as pd
import sys
import matplotlib.pyplot as plt

variations = {
    "ceds17": "~/gitrepos/simpleH2/input/h2_antr_ceds17.csv", 
    "ceds21": "~/gitrepos/simpleH2/input/h2_antr_ceds21.csv",
    "from_fabien": "~/gitrepos/simpleH2/input/h2_antr_from_fabien.csv",
    "ceds21_sectors": "~/gitrepos/simpleH2/input/h2_antr_ceds21_sectors.csv",     
    "ceds24_sectors": "~/gitrepos/simpleH2/input/h2_antr_ceds24.csv",
    }

for version, datafile in variations.items():
    data = pd.read_csv(datafile, index_col=False)
    print(data)
    plt.plot(data.iloc[:,0], data.iloc[:,1], label=version)
    
plt.legend()
plt.show()