import pandas as pd

from simpleh2 import SIMPLEH2


def test_simpleh2_functions():
    sh2 = SIMPLEH2()
    print(sh2.conc_ch4.head)
    assert type(sh2.conc_h2) == pd.DataFrame
    assert len(sh2.conc_h2) == len(range(1850, 2021))
    assert sh2.conc_h2["H2"][1852] == -1

    sh2.calculate_concentrations()
    assert sh2.conc_h2["H2"][1852] != -1

    sh2_test_2 = SIMPLEH2(pam_dict={"refyr": "lastyear", "nit_fix": 4.5}, ceds21=False)
    sh2_test_2.calculate_concentrations(const_oh=1)
    iso1 = sh2.calc_isotope_timeseries()
    iso2 = sh2_test_2.calc_isotope_timeseries(const_oh=1)

    assert iso1.columns == iso2.columns
    assert len(iso1["iso_atmos"]) == len(iso2["iso_atmos"])
