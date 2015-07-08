#!/usr/bin/env python

"""
    Script that generate a comparison of different profile graphs, based on `profile.py` to get profile data.
"""

import logging
import sys
import ConfigParser
import os
from osgeo import gdal
from gdalconst import GA_ReadOnly
import matplotlib.pyplot as plt
import math

import profile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

def manual_linear_scaled_range(data):
    data_min = min(data)
    data_max = max(data)

    log_diff = math.log10(data_max-data_min)
    step = 10 ** math.floor(log_diff)

    scaled_min = math.floor(data_min / step) * step
    scaled_max = math.ceil(data_max / step) * step

    return scaled_min, scaled_max

def generate_detailed_plot(profile_data, filename):
    # Prepare data
    x = [data['distance'] / 1000 for data in profile_data]
    y_elev = [data['elevation'] for data in profile_data]
    y_elev_plus_correction = [data['elevation'] + data['overhead'] for data in profile_data]
    y_sight = [data['sight'] for data in profile_data]

    y_min, y_max = manual_linear_scaled_range(y_elev_plus_correction)
    floor = [y_min for i in x]
    floor_plus_correction = [y_min + data['overhead'] for data in profile_data]

    mid_x = x[int(len(x)/2)]
    max_correction = max([data['overhead'] for data in profile_data])

    # Prepare plot
    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    # Plot
    sub_plt.plot(x, y_sight, 'g-', label='Sight', linewidth=0.5, xunits=1000.0)

    sub_plt.fill_between(x, y_elev, floor_plus_correction, linewidth=0, facecolor=(0.7, 0.7, 0.7), xunits=1000.0)
    sub_plt.fill_between(x, y_elev_plus_correction, y_elev, linewidth=0, facecolor=(0.85, 0.85, 0.7), xunits=1000.0)
    sub_plt.fill_between(x, floor_plus_correction, floor, linewidth=0, facecolor=(0.85, 0.85, 0.7), xunits=1000.0)

    sub_plt.annotate("Max correction: %.2fm" % max_correction, xy=(mid_x, max_correction + y_min),
                     xytext=(-20, 30), textcoords='offset points', arrowprops=dict(arrowstyle="simple", fc="0.3", ec="none"))

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
    fig.savefig(filename, bbox_inches='tight', dpi=80)

def generate_curved_earth_plot(profile_data, filename):
    # Prepare data
    x = [data['distance'] / 1000 for data in profile_data]
    y_elev_plus_correction = [data['elevation'] + data['overhead'] for data in profile_data]
    y_sight = [data['sight'] for data in profile_data]

    y_min, y_max = manual_linear_scaled_range(y_elev_plus_correction)
    floor = [y_min for i in x]
    floor_plus_correction = [y_min + data['overhead'] for data in profile_data]

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
    fig.savefig(filename, bbox_inches='tight', dpi=80)

def generate_curved_sight_plot(profile_data, filename):
    # Prepare data
    x = [data['distance'] / 1000 for data in profile_data]
    y_elev = [data['elevation'] for data in profile_data]
    y_sight_minus_correction = [data['sight'] - data['overhead'] for data in profile_data]

    y_min, y_max = manual_linear_scaled_range(y_elev)
    floor = [y_min for i in x]

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
    fig.savefig(filename, bbox_inches='tight', dpi=80)

def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    ds_filename = config.get('dem', 'location')

    # data source file name
    if len(sys.argv) >= 2:
        ds_filename = sys.argv[1]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

    LOGGER.debug("using the following DEM: %s", ds_filename)

    # 'GPS' coordinates of the first point
    first_lat = 43.561725
    first_long = 1.444796

    # 'GPS' coordinates of the second point
    second_lat = 43.671348
    second_long = 1.225619

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
