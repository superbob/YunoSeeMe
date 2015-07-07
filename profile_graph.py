#!/usr/bin/env python

"""
    Script that generate a profile graph, based on `profile.py`.
"""

import logging
import sys
import ConfigParser
import os
from osgeo import gdal
from gdalconst import GA_ReadOnly
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

import profile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

def manual_linear_scaled_range(data):
    data_min = min(data)
    data_max = max(data)
    log_diff = math.log10(abs(data_max-data_min))
    step = 10 ** math.floor(log_diff)

    scaled_max = math.ceil(data_max / step) * step
    scaled_min = math.floor(data_min / step) * step

    return scaled_min, scaled_max

def generate_detailed_plot(profile_data, filename):
    x = [data['distance'] for data in profile_data]
    y_elev = [data['elevation'] for data in profile_data]
    y_elev_plus_correction = [data['elevation'] + data['overhead'] for data in profile_data]
    y_sight = [data['sight'] for data in profile_data]

    y2_correction = [data['overhead'] for data in profile_data]

    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    sub_plt.set_title("Elevation (m) vs. Distance (m)", fontsize='small')

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='off', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.plot(x, y_elev_plus_correction, '--', label='Elevation + Correction', dashes=(5, 2), linewidth=0.5, color=(0.3, 0.3, 0))
    sub_plt.plot(x, y_elev, 'k-', label='Elevation', linewidth=0.5)
    sub_plt.plot(x, y_sight, 'g-', label='Sight', linewidth=0.5)

    y_min, y_max = manual_linear_scaled_range(y_elev_plus_correction)
    floor = [y_min + data['overhead'] for data in profile_data]

    sub_plt.fill_between(x, y_elev, floor, linewidth=0, facecolor=(0.7, 0.7, 0.7))

    sub_plt.fill_between(x, y_elev_plus_correction, y_elev, linewidth=0, facecolor=(0.5, 0.5, 0, 0.3))

    sub_plt_twin = sub_plt.twinx()

    sub_plt_twin.spines["top"].set_visible(False)
    sub_plt_twin.spines["bottom"].set_visible(False)
    sub_plt_twin.spines["right"].set_visible(False)
    sub_plt_twin.spines["left"].set_visible(False)

    sub_plt_twin.tick_params(axis='both', which='both', bottom='off', top='off',
                             labelbottom='off', left='off', right='off')

    sub_plt_twin.fill(x, y2_correction, '-', label='Correction', linewidth=0.5,
                      facecolor=(0.5, 0.5, 0, 0.3), edgecolor=(0.3, 0.3, 0))

    sub_plt.legend(loc=2, fontsize='small', frameon=False)
    sub_plt.grid()
    sub_plt.set_ylim(y_min, y_max)
    sub_plt.set_xlim(min(x), max(x))

    for tl in sub_plt.get_yticklabels():
        tl.set_fontsize('small')

    for tl in sub_plt.get_xticklabels():
        tl.set_fontsize('small')

    sub_plt_twin.legend(loc=1, fontsize='small', frameon=False)
    sub_plt_min, sub_plt_max = sub_plt.get_ylim()
    sub_plt_twin.set_ylim(0, sub_plt_max - sub_plt_min)

    for tl in sub_plt_twin.get_yticklabels():
        tl.set_color((0.3, 0.3, 0))
        tl.set_fontsize('small')

    fig.set_dpi(70)
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight')

def generate_curved_earth_plot(profile_data, filename):
    x = [data['distance'] for data in profile_data]
    y_elev_plus_correction = [data['elevation'] + data['overhead'] for data in profile_data]
    y_sight = [data['sight'] for data in profile_data]

    y2_correction = [data['overhead'] for data in profile_data]

    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    sub_plt.set_title("Elevation (m) vs. Distance (m)", fontsize='small')

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='off', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.plot(x, y_elev_plus_correction, 'k-', label='Elevation', linewidth=0.5)
    sub_plt.plot(x, y_sight, 'g-', label='Sight', linewidth=0.5)

    sub_plt_twin = sub_plt.twinx()

    sub_plt_twin.spines["top"].set_visible(False)
    sub_plt_twin.spines["bottom"].set_visible(False)
    sub_plt_twin.spines["right"].set_visible(False)
    sub_plt_twin.spines["left"].set_visible(False)

    sub_plt_twin.tick_params(axis='both', which='both', bottom='off', top='off',
                             labelbottom='off', left='off', right='off')

    sub_plt_twin.fill(x, y2_correction, '-', label='Correction', linewidth=0.5,
                      facecolor=(0.5, 0.5, 0, 0.3), edgecolor=(0.3, 0.3, 0))

    y_min, y_max = manual_linear_scaled_range(y_elev_plus_correction)
    sub_plt.set_ylim(y_min, y_max)

    floor = [y_min + data['overhead'] for data in profile_data]

    sub_plt.fill_between(x, y_elev_plus_correction, floor, linewidth=0, facecolor=(0.7, 0.7, 0.7))

    sub_plt.legend(loc=2, fontsize='small', frameon=False)
    sub_plt.grid()
    sub_plt.set_xlim(min(x), max(x))

    for tl in sub_plt.get_yticklabels():
        tl.set_fontsize('small')

    for tl in sub_plt.get_xticklabels():
        tl.set_fontsize('small')

    sub_plt_twin.legend(loc=1, fontsize='small', frameon=False)
    sub_plt_twin.set_ylim(0, y_max - y_min)

    for tl in sub_plt_twin.get_yticklabels():
        tl.set_color((0.3, 0.3, 0))
        tl.set_fontsize('small')

    fig.set_dpi(70)
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight')

def generate_curved_sight_plot(profile_data, filename):
    x = [data['distance'] for data in profile_data]
    y_elev = [data['elevation'] for data in profile_data]
    y_sight_minus_correction = [data['sight'] - data['overhead'] for data in profile_data]

    print(manual_linear_scaled_range(y_elev))

    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    sub_plt.set_title("Elevation (m) vs. Distance (m)", fontsize='small')

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='off', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.plot(x, y_elev, 'k-', label='Elevation', linewidth=0.5)
    sub_plt.plot(x, y_sight_minus_correction, 'g-', label='Sight', linewidth=0.5)

    y_min, y_max = manual_linear_scaled_range(y_elev)
    sub_plt.set_ylim(y_min, y_max)

    floor = [y_min for i in x]

    sub_plt.fill_between(x, y_elev, floor, label='Elevation', linewidth=0.5,
                         facecolor=(0.7, 0.7, 0.7), edgecolor=(0, 0, 0, 0))

    sub_plt.legend(loc=2, fontsize='small', frameon=False)
    sub_plt.grid()
    sub_plt.set_xlim(min(x), max(x))

    for tl in sub_plt.get_yticklabels():
        tl.set_fontsize('small')

    for tl in sub_plt.get_xticklabels():
        tl.set_fontsize('small')

    fig.set_dpi(70)
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight')

def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    ds_filename = config.get('dem', 'location')

    # data source file name
    if len(sys.argv) >= 6:
        ds_filename = sys.argv[5]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

    LOGGER.debug("using the following DEM: %s", ds_filename)

    # 'GPS' coordinates of the first point
    first_lat = float(sys.argv[1])  # ex: 43.561725
    first_long = float(sys.argv[2])  # ex: 1.444796

    # 'GPS' coordinates of the second point
    second_lat = float(sys.argv[3])  # ex: 43.671348
    second_long = float(sys.argv[4])  # ex: 1.225619

    LOGGER.debug("requesting profile for the following 'GPS' coordinates")
    LOGGER.debug("first wgs84 lat: %f, long: %f", first_lat, first_long)
    LOGGER.debug("second wgs84 lat: %f, long: %f", second_lat, second_long)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(ds_filename, GA_ReadOnly)

    profile_data = profile.profile(data_source, first_lat, first_long, second_lat, second_long)
    generate_detailed_plot(profile_data, 'profile-detailed.png')
    generate_curved_earth_plot(profile_data, 'profile-curved-earth.png')
    generate_curved_sight_plot(profile_data, 'profile-curved-sight.png')

if __name__ == '__main__':
    main()
