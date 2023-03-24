import numpy as np
import pandas as pd

from simpleh2 import simpleh2


def test_calc_ch4_lifetim_fact():
    year = np.arange(1850, 2015)
    ch4lifetime_fact = simpleh2.calc_ch4_lifetime_fact(year)
    assert type(ch4lifetime_fact) == pd.DataFrame
