#!/usr/bin/env python

"""
    Script that generate a profile graphs, see `profile_graph_comparison.py` for other graph options.
    This one uses the "profile-curved-earth.png from the generate_curved_earth_plot function"
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

def generate_figure(profile_data, filename):
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

    generate_figure(profile_data, 'profile.png')

if __name__ == '__main__':
    main()
