"""
SIMPLEH2
"""
import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


@dataclass
class SimpleH2DataPaths:
    """
    Dataclass to hold paths to files that the SimpleH2 class uses
    """

    meth_path: str = "/div/qbo/users/ragnhibs/Methane/INPUT/ch4_atm_cmip6_upd.txt"
    nmvoc_path: str = (
        "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_NMVOC_CEDS17.csv"
    )
    co_file: str = "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS17.csv"
    co_file1: str = "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS17.csv"
    co_file2: str = "/div/qbo/utrics/OsloCTM3/plot/emissions_csv/emis_CO_CEDS21.csv"
    gfed_file: str = "/div/qbo/hydrogen/OsloCTM3/lilleH2/emission/gfed_h2.txt"


def check_numeric_pamset(required, pamset):
    """
    Check numeric pamset conforms

    Check that pamset has required inputs
    If not insert defaults from required dict

    Parameters
    ----------
    required : dict
            Dictionary containing the required keys
            with default values
    pamset : dict
          Dictionary to be checked and filled in from
          required where necessary

    Returns
    -------
    dict
         pamset augmented with necessary default values
         from required
    """
    if pamset is None:
        pamset = {}
    for pam, value in required.items():
        if pam not in pamset:
            LOGGER.warning(  # pylint: disable=logging-fstring-interpolation
                f"Parameter {pam} not in pamset. Using default value {value}",
            )
            pamset[pam] = value
        elif not isinstance(pamset[pam], int) and not isinstance(pamset[pam], float):
            LOGGER.warning(  # pylint: disable=logging-fstring-interpolation
                f"Parameter {pam} must be a number. Using default value {value}",
            )
            pamset[pam] = value
    return pamset


def calc_ch4_lifetime_fact(
    year,
    anom_year=2000,
    path="/div/qbo/users/ragnhibs/Methane/OH/OsloCTM3/ForBoxModel/",
):
    """
    Calculate methane lifetime factor for timeseries of years

    Parameters
    ----------
    year : np.ndarray
           Array with years
    anom_year : int
           Anomaly/ reference year, default 2000
    path : str
           Path to methane timeseries data
    Returns
    -------
    pd.DataFrame
         Ratio of methane lifetime to methane lifetime in
         anomaly/reference year
    """
    lifetime_fact = np.ones(year.size)
    ch4lifetime_fact = pd.DataFrame({"lifetime_fact": lifetime_fact}, index=year)
    oh_anomaly = "OsloCTM3"
    oh_run = "histO3"
    startyr = year[0]
    endyear = year[-1]
    filename_oh = oh_anomaly + "_CH4lifetime_" + oh_run + ".txt"
    lifetime = pd.read_csv(path + filename_oh, delimiter=",", index_col=0)
    lifetime = lifetime.loc[startyr:endyear]
    lifetime_ref = lifetime["Lifetime"].loc[anom_year]
    ch4lifetime_fact.loc[lifetime.index] = lifetime / lifetime_ref
    return ch4lifetime_fact


def calc_h2_gfed(
    h2_gfed_temp,
    gfedfile="/div/qbo/hydrogen/OsloCTM3/lilleH2/emission/gfed_h2.txt",
):
    """
    Read in and make dataframe of biomass burning h2 data from gfed

    Parameters
    ----------
    h2_gfed_temp : pd.DataFrame
                  Dataframe template to fill in
    gfedfile : str
               Path to gfed data file

    Returns
    -------
    pd.DataFrame
                Inread biomass burning emissions
    """
    h2_gfed_org = pd.read_csv(gfedfile, index_col=0)
    h2_gfed_org.index.name = "Year"
    h2_gfed_temp.index.name = "Year"
    h2_gfed_temp["Emis"][:] = h2_gfed_org["Emis"].mean()
    return h2_gfed_temp.loc[:1996].append(h2_gfed_org)


class SIMPLEH2:  # pylint: disable=too-many-instance-attributes
    """
    Simple hydrogen concentration modelling class

    Attributes
    ----------
    parameter_dict : dict
         Could contain keywords:
         pre_ind_conc, preindustrial/ intial hydrogen concentrations (350.)
         tau_1, reference year OH lifetime (7.2)
         tau_2, soil sink lifetime (2.4)
         refyr, reference year for calculations (2010)
    conc_ch4 : Pandas.DataFrame
            Methane concentration data
    conc_h2 : Pandas.DataFrame
            Dataframe for hydrogen concetration data
    h2_prod_ch4 : Pandas.DataFrame
            Dataframe for hydrogen emissions from methane
    h2_prod_nmvoc : Pandas.DataFrame
            Dataframe for hydrogen emissions from nmvoc
    h2_antr :  Pandas.DataFrame
            Antrophogenic hydrogen emissions
    h2_gfed :  Pandas.DataFrame
            Dataframe for hydrogen emissions from biomass burning
    """

    def __init__(self, pam_dict=None, ceds21=True, paths=None):
        self.pam_dict = check_numeric_pamset(
            {
                "refyr": 2010,
                "pre_ind_conc": 350.0,
                "prod_ref": 75.6,
                "tau_2": 2.4,
                "tau_1": 7.2,
                "nit_fix": 5,
            },
            pam_dict,
        )
        if paths is None:
            paths = {}
        # frac numbers from Ehhalt and Roherer 2009
        frac_voc = 18.0 / 41.1 * self.pam_dict["prod_ref"]
        frac_ch4 = (1 - frac_voc / self.pam_dict["prod_ref"]) * self.pam_dict[
            "prod_ref"
        ]
        self.paths = SimpleH2DataPaths(**paths)

        self._prepare_concentrations()
        self._calc_h2_prod_nmvoc(
            frac_voc=frac_voc,
        )
        self.h2_prod_ch4 = (
            self.conc_ch4 / self.conc_ch4.loc[self.pam_dict["refyr"]] * frac_ch4
        )
        self.h2_prod_ch4.columns = ["Emis"]
        self.h2_prod_ch4.index.name = "Year"
        self._calc_h2_antr(ceds21)
        self.h2_gfed = calc_h2_gfed(self.h2_antr.copy() * 0.0, self.paths.gfed_file)

    def _prepare_concentrations(self):
        data_conc = pd.read_csv(self.paths.meth_path, index_col=0)
        data_conc.index.name = "Year"
        data_conc.columns = ["CH4"]

        # prepare concentration:
        self.conc_ch4 = data_conc.copy()

        self.conc_h2 = data_conc.copy()

        self.conc_h2.columns = ["H2"]
        self.conc_h2["H2"] = -1

    def _calc_h2_prod_nmvoc(self, frac_voc):
        # Natural emis NMVOC:
        # Sum NMVOC used in the model 2010 and 1850.
        # 764.1 vs 648.87, increase since pre-ind: 115.23
        # Increase in total VOC CEDS: 10.77 to 161.06, increase of 150.3
        frac_voc_used = 115.23 / 150.3
        nat_emis = 648.87 - 10.77 * frac_voc_used  # Used in the model

        nmvoc_emis = pd.read_csv(self.paths.nmvoc_path, index_col=0)
        nmvoc_emis = nmvoc_emis * frac_voc_used
        self.h2_prod_nmvoc = (
            (nmvoc_emis + nat_emis)
            / (nat_emis + nmvoc_emis.loc[self.pam_dict["refyr"]])
            * frac_voc
        )
        self.h2_prod_nmvoc.index.name = "Year"

    def _calc_h2_antr(self, ceds21=True):
        scaling_co = 0.47 * 2.0 / 28.0
        # scaling_co = 0.39*2.0/28.0

        if ceds21:
            h2_antr1 = pd.read_csv(self.paths.co_file1, index_col=0) * scaling_co
            h2_antr2 = pd.read_csv(self.paths.co_file2, index_col=0) * scaling_co
            self.h2_antr = pd.concat([h2_antr1.loc[:1950], h2_antr2.loc[1951:]])

        else:
            self.h2_antr = pd.read_csv(self.paths.co_file, index_col=0) * scaling_co

        self.h2_antr.index.name = "Year"

    def calculate_concentrations(
        self,
        const_oh=0,
        path_oh="/div/qbo/users/ragnhibs/Methane/OH/OsloCTM3/ForBoxModel/",
    ):
        """
        Calculate hydrogen concentrations

        Parameters
        ----------
        const_oh : float
                  If the value of this is 1, oh will be assumed constant
                  otherwise oh-concentrations will be calculated based on
                  methane concentraions, to give a varrying OH-sink lifetime
        path_oh : str
                  path to oh datafile
        """
        tot_prod = (
            self.h2_antr.loc[1850:2014]
            + self.h2_gfed.loc[1850:2014]
            + self.h2_prod_ch4.loc[1850:2014]
            + self.h2_prod_nmvoc.loc[1850:2014]
        )
        year = tot_prod.index.values

        self.pam_dict["nit_fix"] = 5.0

        # Factor converting emissions to mixing ratios (Tg CH4/ppbv)

        # Atmospheric mass conversion H2  [Tg/ppb]	0.37
        # *	(Burden H2/surface conc)
        # Atmospheric mass conversion H2  [Tg/ppb] (based on the perturbations)	0.352
        # (Burden H2/surface conc) Closer to the 0.344 Tg/ppb as Prather stated below.
        # NBNB: Surface conc increased by 10%, burden H2 increased by 9.5%
        #
        # exit()
        beta_h2 = 5.1352e9 * 2.0 / 28.97 * 1e-9  # 2.84

        if const_oh != 1:
            ch4_lifetime_fact = calc_ch4_lifetime_fact(year, path=path_oh)
        else:
            q = 1.0 / self.pam_dict["tau_1"] + 1 / self.pam_dict["tau_2"]
        conc_local = self.pam_dict["pre_ind_conc"]
        for y in year:
            if const_oh != 1:
                q = (
                    1.0
                    / (
                        self.pam_dict["tau_1"]
                        * ch4_lifetime_fact["lifetime_fact"].loc[y]
                    )
                    + 1 / self.pam_dict["tau_2"]
                )
            emis = tot_prod["Emis"].loc[y] + self.pam_dict["nit_fix"]
            point_conc = emis / beta_h2
            conc_local = point_conc / q + (conc_local - point_conc / q) * np.exp(-q)

            self.conc_h2.loc[y] = conc_local

    def calc_isotope_timeseries(
        self,
        parameter_dict=None,
        const_oh=0,
        path_oh="/div/qbo/users/ragnhibs/Methane/OH/OsloCTM3/ForBoxModel/",
    ):
        """
        Calculate isotopic compositions

        Parameters
        ----------
        parameter_dict : dict
                         Parameterdict which may include isotopic
                         fractionisation values. Unset values will
                         be set to default values
        const_oh : float
                  If the value of this is 1, oh will be assumed constant
                  otherwise oh-concentrations will be calculated based on
                  methane concentraions, to give a varrying OH-sink lifetime
        path_oh : str
                  path to oh datafile

        Returns
        -------
        pd.timeseries
                     Isotopic composition in the atmosphere timeseries
        """
        iso_atm_timeseries = self.conc_h2.copy()
        iso_atm_timeseries.columns = ["iso_atmos"]
        pam_dict = check_numeric_pamset(
            {
                "iso_h2_antr": 190,
                "iso_h2_gfed": -290,
                "iso_h2_prod_ch4": 160,
                "iso_h2_prod_nmvoc": 160,
                "iso_h2_nit_fix": -700,
                "frac_soil": 0.943,
                "frac_oh": 0.58,
            },
            parameter_dict,
        )
        tot_prod = (
            self.h2_antr.loc[1850:2014]
            + self.h2_gfed.loc[1850:2014]
            + self.h2_prod_ch4.loc[1850:2014]
            + self.h2_prod_nmvoc.loc[1850:2014]
        )
        year = tot_prod.index.values
        self.pam_dict["nit_fix"] = 5.0
        frac_sink = 0.943 * self.pam_dict["tau_1"] / (
            self.pam_dict["tau_1"] + self.pam_dict["tau_2"]
        ) + 0.58 * self.pam_dict["tau_2"] / (
            self.pam_dict["tau_1"] + self.pam_dict["tau_2"]
        )
        if const_oh != 1:
            ch4_lifetime_fact = calc_ch4_lifetime_fact(year, path=path_oh)
        for y in year:
            emis = tot_prod["Emis"].loc[y] + self.pam_dict["nit_fix"]
            iso_sources = (
                (pam_dict["iso_h2_antr"] * self.h2_antr.loc[y] / emis)
                + (pam_dict["iso_h2_gfed"] * self.h2_gfed.loc[y] / emis)
                + (pam_dict["iso_h2_prod_ch4"] * self.h2_prod_ch4.loc[y] / emis)
                + (pam_dict["iso_h2_prod_nmvoc"] * self.h2_prod_nmvoc.loc[y] / emis)
                + (pam_dict["iso_h2_nit_fix"] * self.pam_dict["nit_fix"] / emis)
            )
            if const_oh != 1:
                tau_1_here = (
                    self.pam_dict["tau_1"] / ch4_lifetime_fact["lifetime_fact"].loc[y]
                )

                frac_sink = 0.943 * tau_1_here / (
                    tau_1_here + self.pam_dict["tau_2"]
                ) + 0.58 * self.pam_dict["tau_2"] / (
                    tau_1_here + self.pam_dict["tau_2"]
                )
            iso_atm_timeseries.loc[y] = 1000 * (
                (iso_sources["Emis"] / 1000 + 1) / frac_sink - 1
            )

        return iso_atm_timeseries
