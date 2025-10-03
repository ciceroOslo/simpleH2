import numpy as np
import matplotlib.pyplot as plt
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from conc_calc import conc_calc
from iso_calc import iso_calc

# Model values (name, x1, x2, x3, x4, x5, tau1, tau2, isovar1, isovar2, isovar3, isovar4, isovar5)
model_data = [
    ("Model Mean", 13.3, 13.3, 46.9, 9, 0, 7.74, 3.41, -196, -290, 162, -628, -385),
    ("OsloCTM", 11.3, 11.3, 56.3, 9, 0, 6.91, 3.3, -196, -290, 162, -628, -385),
    ("GFDL", 12.15, 12.15, 45, 9, 0, 8.66, 3.32, -196, -290, 162, -628, -385),
    ("INCA", 9.15, 9.15, 47.1, 9, 0, 8.66, 3.74, -196, -290, 162, -628, -385),
    ("UCI", 10.8, 10.8, 50.7, 9, 0, 8.33, 3.1, -196, -290, 162, -628, -385),
    ("UKCA", 6.85, 6.85, 48.4, 9, 0, 7.15, 4.32, -196, -290, 162, -628, -385),
    ("WACCM", 29.55, 29.55, 33.9, 9, 0, 6.72, 2.67, -196, -290, 162, -628, -385),
]

# Observed literature values
observed_data = [
    ("Seiler & Conrad, 1987", 20, 20, 40, 7, 0, 7.42, 2.92, -196, -290, 162, -628, -385),
    ("Warneck, 1988", 17, 15, 50, 7, 0, 14.8, 2.08, -196, -290, 162, -628, -385),
    ("Ehhalt, 1999", 20, 10, 35, 6, 0, 6, 3.75, -196, -290, 162, -628, -385),
    ("Novelli et al, 1999", 15, 16, 40, 6, 0, 8.16, 2.77, -196, -290, 162, -628, -385),
    ("Hauglustaine & Ehhalt, 2002", 16, 13, 31, 10, 0, 9.07, 2.47, -196, -290, 162, -628, -385),
    ("Sanderson et al, 2003", 20, 20, 30.2, 8, 0, 10.05, 2.95, -196, -290, 162, -628, -385),
    ("Rhee et al, 2006", 15, 16, 64, 12, 0, 7.89, 1.70, -270, -90, 190, -700, -385),
    ("Price et al, 2007", 18.3, 15.6, 34.3, 6, 0, 7.83, 2.56, -196, -290, 162, -628, -385),
    ("Derwent et al., 2020", None, None, None, None, None, None, None, None, None, None, None, None, None), # Only as a point
]

# Use a fixed value for cval (background concentration)
concval = 552.2  # Adjust as needed

# Prepare data for plotting
model_points = []
for name, x1, x2, x3, x4, x5, tau1, tau2, y1, y2, y3, y4, y5 in model_data:
    conc = conc_calc(x1, x2, x3, x4, x5, tau1, tau2, concval)
    iso = iso_calc(x1, x2, x3, x4, x5, y1, y2, y3, y4, y5, tau1, tau2)
    model_points.append((name, iso, conc))

obs_points = []
for entry in observed_data:
    name = entry[0]
    if name == "Derwent et al., 2020":
        obs_points.append((name, 133, 538))
    else:
        x1, x2, x3, x4, x5, tau1, tau2, y1, y2, y3, y4, y5 = entry[1:]
        conc = conc_calc(x1, x2, x3, x4, x5, tau1, tau2, concval)
        iso = iso_calc(x1, x2, x3, x4, x5, y1, y2, y3, y4, y5, tau1, tau2)
        obs_points.append((name, iso, conc))

# Plotting
fig, ax = plt.subplots(figsize=(10, 7))


# Plot model points and annotate
for name, iso, conc in model_points:
    ax.scatter(iso, conc, color='royalblue', marker='^')
    # Example offsets for clarity, adjust as needed
    if name == "Model Mean":
        ax.text(iso-8, conc+3, name, color='royalblue', fontsize=12)
    elif name == "OsloCTM":
        ax.text(iso+2, conc-2, name, color='royalblue', fontsize=12)
    elif name == "GFDL":
        ax.text(iso+2, conc-2, name, color='royalblue', fontsize=12)
    elif name == "INCA":
        ax.text(iso+2, conc-2, name, color='royalblue', fontsize=12)
    elif name == "UCI":
        ax.text(iso+2, conc-2, name, color='royalblue', fontsize=12)
    elif name == "UKCA":
        ax.text(iso-5, conc-5, name, color='royalblue', fontsize=12)
    elif name == "WACCM":
        ax.text(iso-5, conc+3, name, color='royalblue', fontsize=12)

# Plot observed points and annotate
for name, iso, conc in obs_points:
    ax.scatter(iso, conc, color='sienna', marker='o')
    # Example offsets for clarity, adjust as needed
    if name == "Seiler & Conrad, 1987":
        ax.text(iso-25, conc+3, name, color='sienna', fontsize=12)
    elif name == "Warneck, 1988":
        ax.text(iso-12, conc+3, name, color='sienna', fontsize=12)
    elif name == "Ehhalt, 1999":
        ax.text(iso+2, conc-5, name, color='sienna', fontsize=12)
    elif name == "Novelli et al, 1999":
        ax.text(iso+2, conc-5, name, color='sienna', fontsize=12)
    elif name == "Hauglustaine & Ehhalt, 2002":
        ax.text(iso-8, conc-5, name, color='sienna', fontsize=12)
    elif name == "Sanderson et al, 2003":
        ax.text(iso-5, conc-5, name, color='sienna', fontsize=12)
    elif name == "Rhee et al, 2006":
        ax.text(iso+2, conc-5, name, color='sienna', fontsize=12)
    elif name == "Price et al, 2007":
        ax.text(iso+2, conc-5, name, color='sienna', fontsize=12)
    elif name == "Derwent et al., 2020":
        ax.text(iso+2, conc-5, name, color='sienna', fontsize=12)


# Labels and legend

ax.errorbar(130, 530, xerr=4, yerr=6, color='black', marker='x')


ax.set_xlabel("dD$_{atmos}$ (‰)", fontsize=16)
ax.set_ylabel("Tropospheric H$_2$ (ppbv)", fontsize=16)
ax.set_title("Global mean H$_2$ concentration vs isotopic composition", fontsize=16)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
ax.set_ylim(450, 600)  # Set y-axis limits

plt.tight_layout()
plt.show()
