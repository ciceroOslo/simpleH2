import os

import numpy as np
import pandas as pd

from simpleh2 import SIMPLEH2


def test_simpleh2_functions():
    sh2 = SIMPLEH2()
    assert type(sh2.conc_h2) == pd.DataFrame
    assert len(sh2.conc_h2) == len(range(1700, 2023))
    assert sh2.conc_h2["H2"][1852] == -1

    sh2.calculate_concentrations()
    print(sh2.conc_h2[1750:2014])
    sh2_old = sh2.conc_h2["H2"][1852]
    print(sh2_old)
    assert sh2_old > 240
    # assert np.allclose(sh2.conc_h2["H2"][1852], 335.141493)

    sh2_test_2 = SIMPLEH2(
        pam_dict={"refyr": "lastyear", "nit_fix": 4.5},
        paths={
            "antr_file": os.path.join(
                os.path.dirname(__file__), "..", "..", "input", "h2_antr_ceds17.csv"
            )
        },
    )
    sh2_test_2.calculate_concentrations(const_oh=1)
    iso1 = sh2.calc_isotope_timeseries()
    iso2 = sh2_test_2.calc_isotope_timeseries(const_oh=1)

    assert iso1.columns == iso2.columns
    assert len(iso1["iso_atmos"]) == len(iso2["iso_atmos"])
    assert not any(np.isnan(iso1["iso_atmos"].values))
    assert not any(np.isnan(iso2["iso_atmos"].values))

    sh2.scale_emissions_antr(31.58)
    sh2.calculate_concentrations()
    assert sh2.conc_h2["H2"][1852] != sh2_old
