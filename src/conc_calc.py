import numpy as np
import pandas as pd

def conc_calc(x1, x2, x3, x4, x5, TAU_1, TAU_2, cval, BETA_H2=0.354, const_oh=1, ch4lifetime_fact=None, year=None):
    """
    Calculate atmospheric H2 concentration.

    Parameters:
        x1, x2, x3, x4, x5 : float
            Source terms (e.g., anthropogenic, biomass burning, atm prod, nit fix, geo fix)
        TAU_1 : float
            OH lifetime
        TAU_2 : float
            Dry deposition lifetime
        cval : float
            Initial concentration value
        BETA_H2 : float, optional
            Conversion factor (default: 0.354)
        const_oh : int, optional
            If 1, use constant OH lifetime; else, use ch4lifetime_fact (default: 1)
        ch4lifetime_fact : pd.DataFrame, optional
            DataFrame of CH4 lifetime factors (required if const_oh != 1)
        year : int, optional
            Year index for ch4lifetime_fact (required if const_oh != 1)

    Returns:
        float
            Calculated concentration
    """
    IDTM = 1
    if const_oh == 1:
        q = 1.0 / TAU_1
    else:
        if ch4lifetime_fact is None or year is None:
            raise ValueError("ch4lifetime_fact and year must be provided if const_oh != 1")
        q = 1.0 / (TAU_1 * ch4lifetime_fact.loc[year])
    q = q + 1.0 / TAU_2
    em = x1 + x2 + x3 + x4 + x5
    em = em / IDTM
    q = q / IDTM
    pc = em / BETA_H2
    ach = cval
    pc = np.array(pc)
    q = np.array(q)
    for _ in range(IDTM):
        ach = pc.item() / q.item() + (ach - (pc.item() / q.item())) * np.exp(-q.item() * 1.0)
    return ach