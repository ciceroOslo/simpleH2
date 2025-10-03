import numpy as np

def iso_calc(x1, x2, x3, x4, x5, y1, y2, y3, y4, y5, TAU_1, TAU_2):
    """
    Calculate atmospheric H2 isotopic composition.

    Parameters:
        x1, x2, x3, x4, x5 : float
            Source terms (e.g., anthropogenic, biomass burning, atm prod, nit fix, geo fix)
        y1, y2, y3, y4, y5 : float
            Isotopic signatures for each source
        TAU_1 : float
            OH lifetime
        TAU_2 : float
            Dry deposition lifetime

    Returns:
        float
            Calculated isotopic composition (dD, per mil)
    """
    em = x1 + x2 + x3 + x4 + x5
    iso_sources = (y1 * x1 / em) + (y2 * x2 / em) + (y3 * x3 / em) + (y4 * x4 / em) + (y5 * x5 / em)
    frac_sink = (0.94 * TAU_1 / (TAU_2 + TAU_1)) + (0.56 * (TAU_2 / (TAU_1 + TAU_2)))
    iso_atm = 1000 * ((iso_sources / 1000 + 1) / frac_sink - 1)
    return iso_atm