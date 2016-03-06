"""
Plot styles available to draw from PNGProfileFormat

 * detailed_plot: a detailed view of the profile
 * corrected_elevation: show the terrain with curvature correction and a straight line of sight
 * curved_sight: show the terrain without curvature correction and a curved line of sight
"""

import math
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt


def manual_linear_scaled_range(data):
    """
    Return the linear scaled limits (min and max) based on the log10 of the input data.

    :param data: the data to look the scale for
    :return: the min and max of the scale
    """
    data_min = np.amin(data)
    data_max = np.amax(data)

    log_diff = math.log10(data_max - data_min)
    step = 10 ** math.floor(log_diff)

    scaled_min = math.floor(data_min / step) * step
    scaled_max = math.ceil(data_max / step) * step

    return scaled_min, scaled_max


def detailed_plot(profile_data, filename, file_format='png'):
    # Prepare data
    x = profile_data['distances'] / 1000  # pylint: disable=invalid-name
    y_elev = profile_data['elevations']
    y_elev_plus_correction = profile_data['elevations'] + profile_data['overheads']
    y_sight = profile_data['sights']

    y_min, y_max = manual_linear_scaled_range(np.concatenate([y_elev_plus_correction, y_sight]))
    floor = np.full_like(x, y_min)

    floor_plus_correction = floor + profile_data['overheads']

    mid_x = x[int(len(x) / 2)]
    max_correction = max(profile_data['overheads'])

    # Prepare plot
    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    # Plot
    sub_plt.plot(x, y_sight, 'g-', label='Sight', linewidth=0.5, xunits=1000.0)

    sub_plt.fill_between(x, y_elev, floor_plus_correction, linewidth=0, facecolor=(0.7, 0.7, 0.7), xunits=1000.0)
    sub_plt.fill_between(x, y_elev_plus_correction, y_elev, linewidth=0, facecolor=(0.85, 0.85, 0.7), xunits=1000.0)
    sub_plt.fill_between(x, floor_plus_correction, floor, linewidth=0, facecolor=(0.85, 0.85, 0.7), xunits=1000.0)

    sub_plt.annotate("Max correction: %.2fm" % max_correction, xy=(mid_x, max_correction + y_min),
                     xytext=(-20, 30), textcoords='offset points',
                     arrowprops=dict(arrowstyle="simple", fc="0.3", ec="none"))

    # Fix limits
    sub_plt.set_xlim(min(x), max(x))
    sub_plt.set_ylim(y_min, y_max)

    # Style
    sub_plt.set_title("Elevation (m) vs. Distance (km)")

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='on', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.grid(axis='y')

    # Format and save
    # setting dpi with figure.set_dpi() seem to be useless, the dpi really used is the one in savefig()
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight', dpi=80, format=file_format)


def corrected_elevation(profile_data, filename, file_format='png'):
    """
    Generate a figure with the given profile data in the given filename.

    :param profile_data: a dict object having 'distances', 'elevations', 'overheads' and 'sights' keys defined
    each key is an array (or a numpy array) of the points
    :param filename: a string or a fd to write the figure in
    :param file_format: the format given to the Figure.savefig function, default is 'png'
    """
    # Prepare data
    x = profile_data['distances'] / 1000  # pylint: disable=invalid-name
    y_elev_plus_correction = profile_data['elevations'] + profile_data['overheads']
    y_sight = profile_data['sights']

    y_min, y_max = manual_linear_scaled_range(np.concatenate([y_elev_plus_correction, y_sight]))
    floor = np.full_like(x, y_min)
    floor_plus_correction = floor + profile_data['overheads']

    # Prepare plot
    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    # Plot
    sub_plt.plot(x, y_sight, 'g-', label='Sight', linewidth=0.5)

    sub_plt.fill_between(x, y_elev_plus_correction, floor_plus_correction, linewidth=0, facecolor=(0.7, 0.7, 0.7))
    sub_plt.fill_between(x, floor_plus_correction, floor, linewidth=0, facecolor=(0.85, 0.85, 0.7))

    # Fix limits
    sub_plt.set_xlim(min(x), max(x))
    sub_plt.set_ylim(y_min, y_max)

    # Style
    sub_plt.set_title("Elevation (m) vs. Distance (km)")

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='on', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.grid(axis='y')

    # Format and save
    # setting dpi with figure.set_dpi() seem to be useless, the dpi really used is the one in savefig()
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight', dpi=80, format=file_format)


def curved_sight(profile_data, filename, file_format='png'):
    # Prepare data
    x = profile_data['distances'] / 1000  # pylint: disable=invalid-name
    y_elev = profile_data['elevations']
    y_sight_minus_correction = profile_data['sights'] - profile_data['overheads']

    y_min, y_max = manual_linear_scaled_range(np.concatenate([y_elev, y_sight_minus_correction]))
    floor = np.full_like(x, y_min)

    # Prepare plot
    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    # Plot
    sub_plt.plot(x, y_sight_minus_correction, 'g-', label='Sight', linewidth=0.5)

    sub_plt.fill_between(x, y_elev, floor, label='Elevation', linewidth=0.5,
                         facecolor=(0.7, 0.7, 0.7), edgecolor=(0, 0, 0, 0))

    # Fix limits
    sub_plt.set_xlim(min(x), max(x))
    sub_plt.set_ylim(y_min, y_max)

    # Style
    sub_plt.set_title("Elevation (m) vs. Distance (km)")

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='on', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.grid(axis='y')

    # Format and save
    # setting dpi with figure.set_dpi() seem to be useless, the dpi really used is the one in savefig()
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight', dpi=80, format=file_format)
