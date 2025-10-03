# simpleh2
Simple model that calculates hydrogen concentrations based on emissions and other data.

To modify the way of running, initialise the SIMPLEH2 object with parameters sent in the **pam_dict**, these include
* refyear - Reference year, default 2010
* pre_ind_conc - Preindustrial concentration, default 350.0 ppb
* prod_ref - Production in reference year, default 75.6 Tg/yr
* tau_2 - soil lifetime default value 2.4 years
* tau_1 - atmospheric lifetime, default value 7.2 years
* nit_fix - Nitrogen fixation strength, default value 5 Tg/yr

Choose to run with **ceds21** as True or False, and modify file paths in the **paths** dictionary with:
* meth_path : Path to methane input file
* nmvoc_path : Path to nmvoc emissions file
* gfed_file : Path to gfed data file 
* co_file : CEDS 2017 CO-file used when ceds 2021 is not used
* co_file1: CEDS 2017 CO-file used in combination with ceds 2021 data
* co_file2: CEDS 2021 CO-file used when ceds 2021 is not used

In the run to calculate concentrations or isotope value, you can choose to run with **const_oh** = 1 and a constant value, or a varrying oh-value by setting this parameter to zero (this is also the default behaviour). If oh is changing it will be read from the **path_oh** parameter path

Branch updates
Multiple year runs are run using the simpleH2 class module.
Single year runs are run using the conc_calc and iso_calc functions. These contain the geological terms, absent in the simpleH2 class. These will be merged.