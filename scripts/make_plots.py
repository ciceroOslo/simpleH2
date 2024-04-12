import os
import matplotlib.pyplot as plt

from simpleh2 import SIMPLEH2


sh2 = SIMPLEH2()
print(sh2.conc_ch4.head)


sh2.calculate_concentrations()


sh2_test_2 = SIMPLEH2(pam_dict={"refyr": "lastyear", "nit_fix": 4.5}, paths={"antr_file": os.path.join(
        os.path.dirname(__file__), "..", "input", "h2_antr_ceds21.csv"
    )})
sh2_test_2.calculate_concentrations(const_oh=1)
iso1 = sh2.calc_isotope_timeseries()
iso2 = sh2_test_2.calc_isotope_timeseries(const_oh=1)

print('Done calculations!')

print("Concentration is", sh2.conc_h2)

fig, axs = plt.subplots(nrows=2,ncols=2,sharex=False,sharey=False,squeeze=True,figsize=(12,10))
axs[1,0].plot(sh2.conc_h2,'-', linewidth =2,label='Concentration')
#axs[1,0].set_xlim([startyr,endyear])
axs[1,0].set_xlabel("Years")
axs[1,0].set_ylabel("H2 [ppb]")

plt.show()
