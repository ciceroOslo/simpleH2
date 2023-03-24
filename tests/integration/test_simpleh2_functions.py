import pandas as pd

from simpleh2 import SIMPLEH2


def test_simpleh2_functions():
    sh2 = SIMPLEH2()
    print(sh2.conc_ch4.head)
    assert type(sh2.conc_h2) == pd.DataFrame
    assert len(sh2.conc_h2) == len(range(1850, 2014))
    assert sh2.conc_h2["H2"][1852] == -1

    sh2.calculate_concentrations()
    assert sh2.conc_h2["H2"][1852] != -1
