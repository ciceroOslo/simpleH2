"""
SIMPLEH2
"""
import logging
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


@dataclass
class SimpleH2DataPaths:
    """
    Dataclass to hold paths to files that the SimpleH2 class uses
    """

    meth_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "input", "ch4_historical.csv"
    )
    nmvoc_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "input", "nmvoc_emis_ssp245.csv"
    )
    bb_file: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "input", "bb_emis_gfed.csv"
    )
    antr_file: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "input", "h2_antr_ceds21.csv"
    )


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
           Path to oh file to inform methane lifetime
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


def calc_h2_bb_emis(bb_emis_file):
    """
    Read in and make dataframe of biomass burning h2 emissions

    Parameters
    ----------
    bb_emis_file : str
               Path to gfed data file

    Returns
    -------
    pd.DataFrame
                Inread biomass burning emissions
    """
    h2_bb_emis = pd.read_csv(bb_emis_file, index_col=0)
    h2_bb_emis.index.name = "Year"

    return h2_bb_emis


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
    h2_prod_emis : Pandas.DataFrame
            Dataframe for hydrogen production and emission terms
            After initialisation it will have four columns, h2_prod_nmvoc
            h2_prod_ch4, h2_antr and h2_bb_emis containing h2 production
            or emissions resulting from nmvoc or methane photooxidation
            or anthropogenic or biomass burning related hydrogen emissions
            (scaled from CO), respectively
    """

    def __init__(self, pam_dict=None, paths=None):
        self.pam_dict = check_numeric_pamset(
            {
                "refyr": 2010,
                "pre_ind_conc": 350.0,
                "prod_ref": 75.6,
                "tau_2": 2.4,
                "tau_1": 7.2,
                "nit_fix": 5,
                "scaling_co": 0.34 * 2.0 / 28.0,
                "natvoc": 600.0,
            },
            pam_dict,
        )
        if paths is None:
            paths = {}
        # frac numbers from Ehhalt and Roherer 2009
        frac_voc = 18.0 / 41.1 * self.pam_dict["prod_ref"]
        print(frac_voc)
        frac_ch4 = (1 - frac_voc / self.pam_dict["prod_ref"]) * self.pam_dict[
            "prod_ref"
        ]
        self.paths = SimpleH2DataPaths(**paths)

        self.paths = SimpleH2DataPaths(**paths)

        self._prepare_concentrations()

        self._initialise_emis_with_nmvoc(frac_voc=frac_voc)

        self.h2_prod_emis["h2_prod_ch4"] = (
            self.conc_ch4 / self.conc_ch4.loc[self.pam_dict["refyr"]] * frac_ch4
        )

        self._calc_h2_antr()

        self.h2_prod_emis["h2_bb_emis"] = calc_h2_bb_emis(self.paths.bb_file)

    def _prepare_concentrations(self):
        data_conc = pd.read_csv(self.paths.meth_path, index_col=0)
        data_conc.index.name = "Year"
        data_conc.columns = ["CH4"]

        # prepare concentration:
        self.conc_ch4 = data_conc.copy()
        self.conc_h2 = data_conc.copy()

        self.conc_h2.columns = ["H2"]
        self.conc_h2["H2"] = -1

    def _initialise_emis_with_nmvoc(self, frac_voc):
        # Natural emis NMVOC:
        # Sum NMVOC used in the model 2010 and 1850.
        # 764.1 vs 648.87, increase since pre-ind: 115.23
        # Increase in total VOC CEDS: 10.77 to 161.06, increase of 150.3

        # frac_voc_used = 115.23 / 150.3
        # nat_emis = 648.87 - 10.77 * frac_voc_used  # Used in the model

        nmvoc_emis = (
            pd.read_csv(self.paths.nmvoc_path, index_col=0) + self.pam_dict["natvoc"]
        )

        # nmvoc_emis = nmvoc_emis * frac_voc_used
        # self.h2_prod_nmvoc = (
        #    (nmvoc_emis + nat_emis)
        #    / (nat_emis + nmvoc_emis.loc[self.pam_dict["refyr"]])
        #    * frac_voc
        # )
        self.h2_prod_emis = (
            nmvoc_emis / nmvoc_emis.loc[self.pam_dict["refyr"]] * frac_voc
        )
        self.h2_prod_emis.index.name = "Year"
        self.h2_prod_emis = self.h2_prod_emis.rename(columns={"Emis": "h2_prod_nmvoc"})

    def _calc_h2_antr(self):
        h2_antr = (
            pd.read_csv(self.paths.antr_file, index_col=0) * self.pam_dict["scaling_co"]
        )
        self.h2_prod_emis["h2_antr"] = h2_antr["Emis"]

    def scale_emissions_antr(self, tot_emis):
        """
        Scale emissions according to anthropogenic emissions

        Parameters
        ----------
        tot_emis : float
                   Total emissions to scale to
        """
        model_emis_antr = (
            tot_emis
            - self.pam_dict["nit_fix"]
            - self.h2_prod_emis["h2_bb_emis"].loc[self.pam_dict["refyr"]]
        )
        print(model_emis_antr)
        self.h2_prod_emis["h2_antr"] = (
            self.h2_prod_emis["h2_antr"]
            / self.h2_prod_emis["h2_antr"].loc[self.pam_dict["refyr"]]
            * model_emis_antr
        )

    def calculate_concentrations(self, const_oh=0, startyr=1850, endyr=2014):
        """
        Calculate hydrogen concentrations

        Parameters
        ----------
        const_oh : float
                  If the value of this is 1, oh will be assumed constant
                  otherwise oh-concentrations will be calculated based on
                  methane concentraions, to give a varrying OH-sink lifetime
        startyr : int
                  Startyear for concentrations calculations
        endyr : int
                Endyear for concentrations calculations

        """
        tot_prod = self.h2_prod_emis.loc[startyr:endyr+1].sum(axis=1).values
        print(self.pam_dict)  # = 9.0

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
            ch4_lifetime_fact = calc_ch4_lifetime_fact(np.arange(startyr, endyr+1))
            
        else:
            q = 1.0 / self.pam_dict["tau_1"] + 1 / self.pam_dict["tau_2"]
        conc_local = self.pam_dict["pre_ind_conc"]
        for i, y in enumerate(np.arange(startyr, endyr+1)):
            if const_oh != 1:
                q = (
                    1.0
                    / (
                        self.pam_dict["tau_1"]
                        * ch4_lifetime_fact["lifetime_fact"].loc[y]
                    )
                    + 1 / self.pam_dict["tau_2"]
                )
            emis = tot_prod[i] + self.pam_dict["nit_fix"]
            point_conc = emis / beta_h2
            conc_local = point_conc / q + (conc_local - point_conc / q) * np.exp(-q)
            self.conc_h2.loc[y] = conc_local

    def calc_isotope_timeseries(
        self, parameter_dict=None, const_oh=0, startyr=1850, endyr=2014
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
        startyr : int
                  Startyear for isotopic calculations
        endyr : int
                Endyear for isotopic calculations

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
        tot_prod = self.h2_prod_emis.loc[startyr:endyr+1].sum(axis=1).values
        self.pam_dict["nit_fix"] = 5.0
        frac_sink = 0.943 * self.pam_dict["tau_1"] / (
            self.pam_dict["tau_1"] + self.pam_dict["tau_2"]
        ) + 0.58 * self.pam_dict["tau_2"] / (
            self.pam_dict["tau_1"] + self.pam_dict["tau_2"]
        )
        if const_oh != 1:
            ch4_lifetime_fact = calc_ch4_lifetime_fact(np.arange(startyr, endyr+1))
        for i, y in enumerate(np.arange(startyr, endyr+1)):
            emis = tot_prod[i] + self.pam_dict["nit_fix"]
            iso_sources = (
                (pam_dict["iso_h2_antr"] * self.h2_prod_emis["h2_antr"].loc[y] / emis)
                + (
                    pam_dict["iso_h2_gfed"]
                    * self.h2_prod_emis["h2_bb_emis"].loc[y]
                    / emis
                )
                + (
                    pam_dict["iso_h2_prod_ch4"]
                    * self.h2_prod_emis["h2_prod_ch4"].loc[y]
                    / emis
                )
                + (
                    pam_dict["iso_h2_prod_nmvoc"]
                    * self.h2_prod_emis["h2_prod_nmvoc"].loc[y]
                    / emis
                )
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
                (iso_sources / 1000 + 1) / frac_sink - 1
            )

        return iso_atm_timeseries
