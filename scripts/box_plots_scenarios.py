import numpy as np
import matplotlib.pyplot as plt
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from conc_calc import conc_calc
from iso_calc import iso_calc

# --- Define scenarios and isotope scenarios ---
scenarios = [
    {"Anthropogenic": 13.3, "Biomass Burning": 13.3, "Atmospheric Production": 46.9, "Nitrogen Fixation": 9, "Geological Sources": 0, "OH": 7.74, "drydep": 3.41, "OH Sink": -24.617, "Soil Uptake": -56.058},
    {"Anthropogenic": 13.3, "Biomass Burning": 13.3, "Atmospheric Production": 77, "Nitrogen Fixation": 9, "Geological Sources": 0, "OH": 7.74, "drydep": 2.300, "OH Sink": -24.617, "Soil Uptake": -82.7},
    {"Anthropogenic": 20, "Biomass Burning": 20, "Atmospheric Production": 30, "Nitrogen Fixation": 9, "Geological Sources": 0, "OH": 7.74, "drydep": 3.41, "OH Sink": -24.617, "Soil Uptake": -56.058},
    {"Anthropogenic": 13.3, "Biomass Burning": 13.3, "Atmospheric Production": 46.9, "Nitrogen Fixation": 9, "Geological Sources": 20, "OH": 7.74, "drydep": 2.41, "OH Sink": -24.617, "Soil Uptake": -76.35}
]

isotope_scenarios = [
    {"Anthropogenic": 13.3, "Biomass Burning": 13.3, "Atmospheric Production": 46.9, "Nitrogen Fixation": 9, "Geological Sources": 0, "Anthropogenic Iso": -196, "Biomass Burning Iso": -290, "Atmospheric Production Iso": 162, "Nitrogen Fixation Iso": -628, "Geological Iso": -385, "OH": 7.74, "drydep": 3.41},
    {"Anthropogenic": 13.3, "Biomass Burning": 13.3, "Atmospheric Production": 77, "Nitrogen Fixation": 9, "Geological Sources": 0, "Anthropogenic Iso": -196, "Biomass Burning Iso": -290, "Atmospheric Production Iso": 162, "Nitrogen Fixation Iso": -628, "Geological Iso": -385, "OH": 7.74, "drydep": 2.30},
    {"Anthropogenic": 20.0, "Biomass Burning": 20.0, "Atmospheric Production": 30, "Nitrogen Fixation": 9, "Geological Sources": 0, "Anthropogenic Iso": -196, "Biomass Burning Iso": -290, "Atmospheric Production Iso": 162, "Nitrogen Fixation Iso": -628, "Geological Iso": -385, "OH": 7.74, "drydep": 3.41},
    {"Anthropogenic": 13.3, "Biomass Burning": 13.3, "Atmospheric Production": 46.9, "Nitrogen Fixation": 9, "Geological Sources": 20, "Anthropogenic Iso": -196, "Biomass Burning Iso": -290, "Atmospheric Production Iso": 162, "Nitrogen Fixation Iso": -628, "Geological Iso": -385, "OH": 7.74, "drydep": 2.41}
]

# --- Input labels and plot setup ---
input_labels = ['Anthropogenic', 'Biomass Burning', 'Atmospheric Production', 'Nitrogen Fixation', 'Geological Sources', 'OH Sink', 'Soil Uptake']
isotope_input_labels = ['Anthropogenic Iso', 'Biomass Burning Iso', 'Atmospheric Production Iso', 'Nitrogen Fixation Iso', 'Geological Iso']
labels = ['Base Case', 'High Atm. Production', 'Low Atm. Production', 'Geological Sources']
colors = ['#003f5c', '#7a5195', '#ef5675', '#ffa600']

x = np.arange(len(input_labels))
isotope_x = np.arange(len(isotope_input_labels))
width = 0.1

# --- Calculate results ---
concval = 550.0  # Or set to your desired value

results = []
for scenario in scenarios:
    result = conc_calc(
        scenario["Anthropogenic"],
        scenario["Biomass Burning"],
        scenario["Atmospheric Production"],
        scenario["Nitrogen Fixation"],
        scenario["Geological Sources"],
        scenario["OH"],
        scenario["drydep"],
        concval
    )
    results.append(result)

isotope_results = []
for scenario in isotope_scenarios:
    result = iso_calc(
        scenario["Anthropogenic"],
        scenario["Biomass Burning"],
        scenario["Atmospheric Production"],
        scenario["Nitrogen Fixation"],
        scenario["Geological Sources"],
        scenario["Anthropogenic Iso"],
        scenario["Biomass Burning Iso"],
        scenario["Atmospheric Production Iso"],
        scenario["Nitrogen Fixation Iso"],
        scenario["Geological Iso"],
        scenario["OH"],
        scenario["drydep"]
    )
    isotope_results.append(result)

# --- Prepare values for plotting ---
all_values = []
for scenario in scenarios:
    values = [scenario[key] for key in input_labels]
    all_values.append(values)

first_scenario = isotope_scenarios[2]
isotope_values = [[first_scenario[key] for key in isotope_input_labels]]
isotope_uncertainties = [10, 60, 57, 35, 0]

x_results = np.arange(2)
width_results = 0.0025

# --- Plotting ---
fig = plt.figure(figsize=(18, 18))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 2])

# Top-left panel: Input values
ax1 = fig.add_subplot(gs[0, 0])
ax1.text(0.05, 0.95, '(a)', transform=ax1.transAxes, verticalalignment='top')
for i, values in enumerate(all_values):
    ax1.bar(x + i * width, values, width, label=labels[i], color=colors[i])
ax1.set_ylabel('Sources/Sinks (Tg/yr)')
ax1.set_xticks(x + width * 2)
ax1.set_xticklabels(input_labels, rotation=45, ha='right')
ax1.legend(loc='lower left')
ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)

# Top-right panel: Isotope values
ax2 = fig.add_subplot(gs[0, 1])
ax2.text(0.05, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top')
for i, values in enumerate(isotope_values):
    bars = ax2.bar(isotope_x + i * width, values, width, label=labels[i], color="cornflowerblue")
    if i == 0:
        ax2.errorbar(
            isotope_x + i * width, values,
            yerr=isotope_uncertainties,
            fmt='none', ecolor='black', elinewidth=2, capsize=6, capthick=2
        )
ax2.set_ylabel('Isotope Values for sources/sinks (‰)')
ax2.set_xticks(isotope_x)
ax2.set_xticklabels(isotope_input_labels, rotation=45, ha='right')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)

# Bottom-left panel: conc_calc results
ax3 = fig.add_subplot(gs[1, 0])
ax3.text(0.05, 0.95, '(c)', transform=ax3.transAxes, verticalalignment='top')
for i, result in enumerate(results):
    ax3.bar(x_results[0] + i * width_results, result[0] if isinstance(result, np.ndarray) else result, width_results, label=labels[i], color=colors[i])
ax3.set_ylabel('Atm. H2 Concentration (ppb)')
ax3.set_xticks([x_results[0]])
ax3.set_xticklabels([''])
ax3.set_ylim(0, 650)
ax3.axhspan(530, 550, xmin=0.0, xmax=5.0, facecolor='none', edgecolor='black', linestyle='--')

# Bottom-right panel: iso_calc results
ax4 = fig.add_subplot(gs[1, 1])
ax4.text(0.05, 0.95, '(d)', transform=ax4.transAxes, verticalalignment='top')
for i, result in enumerate(isotope_results):
    ax4.bar(x_results[1] + i * width_results, result[0] if isinstance(result, np.ndarray) else result, width_results, label=labels[i], color=colors[i])
ax4.set_ylabel('Atm. H2 Isotopic values (‰)')
ax4.set_xticks([x_results[1]])
ax4.set_xticklabels([''])
ax4.set_ylim(0, 250)
ax4.axhspan(130, 160, xmin=0.0, xmax=5.0, facecolor='none', edgecolor='black', linestyle='--')
ax4.legend()

# Add uncertainty bars to ax4 for all scenarios
for i, scenario in enumerate(isotope_scenarios):
    iso_base = [
        scenario["Anthropogenic Iso"],
        scenario["Biomass Burning Iso"],
        scenario["Atmospheric Production Iso"],
        scenario["Nitrogen Fixation Iso"],
        scenario["Geological Iso"]
    ]
    iso_lower = iso_calc(
        scenario["Anthropogenic"], scenario["Biomass Burning"], scenario["Atmospheric Production"], scenario["Nitrogen Fixation"], scenario["Geological Sources"],
        iso_base[0] - isotope_uncertainties[0],
        iso_base[1] - isotope_uncertainties[1],
        iso_base[2] - isotope_uncertainties[2],
        iso_base[3] - isotope_uncertainties[3],
        iso_base[4],
        scenario["OH"], scenario["drydep"]
    )
    iso_upper = iso_calc(
        scenario["Anthropogenic"], scenario["Biomass Burning"], scenario["Atmospheric Production"], scenario["Nitrogen Fixation"], scenario["Geological Sources"],
        iso_base[0] + isotope_uncertainties[0],
        iso_base[1] + isotope_uncertainties[1],
        iso_base[2] + isotope_uncertainties[2],
        iso_base[3] + isotope_uncertainties[3],
        iso_base[4],
        scenario["OH"], scenario["drydep"]
    )
    iso_central = isotope_results[i][0] if isinstance(isotope_results[i], (np.ndarray,)) else isotope_results[i]
    iso_lower_val = iso_lower[0] if isinstance(iso_lower, (np.ndarray,)) else iso_lower
    iso_upper_val = iso_upper[0] if isinstance(iso_upper, (np.ndarray,)) else iso_upper
    yerr = np.array([[iso_central - iso_lower_val], [iso_upper_val - iso_central]])
    ax4.errorbar(
        x_results[1] + i * width_results,
        iso_central,
        yerr=yerr,
        fmt='none',
        ecolor='black',
        elinewidth=2,
        capsize=6,
        capthick=2
    )

plt.tight_layout()
plt.subplots_adjust(hspace=0.4, wspace=0.20)
plt.show()