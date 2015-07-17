#!/usr/bin/env python

"""
Program that generate a profile graph, see `profile_graph_comparison.py` for other graph options.
This one uses the "profile-curved-earth.png from the generate_curved_earth_plot function"
"""

import argparse
import ConfigParser
import math
import logging
import os

import numpy as np
from osgeo import gdal
from gdalconst import GA_ReadOnly
import matplotlib.pyplot as plt

import profile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

def manual_linear_scaled_range(data):
    data_min = np.amin(data)
    data_max = np.amax(data)

    log_diff = math.log10(data_max-data_min)
    step = 10 ** math.floor(log_diff)

    scaled_min = math.floor(data_min / step) * step
    scaled_max = math.ceil(data_max / step) * step

    return scaled_min, scaled_max

def generate_figure(profile_data, filename, file_format='png'):
    # Prepare data
    x = profile_data['distances'] / 1000
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

def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    config_dem_location = config.get('dem', 'location')

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('lat1', type=float, help="first point latitude, ex: 43.561725")
    parser.add_argument('long1', type=float, help="first point longitude, ex: 1.444796")
    parser.add_argument('lat2', type=float, help="second point latitude, ex: 43.671348")
    parser.add_argument('long2', type=float, help="second point longitude, ex: 1.225619")
    parser.add_argument('-d', '--dem', help="DEM file location, ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'",
                        default=config_dem_location)
    offset1_group = parser.add_mutually_exclusive_group()
    offset1_group.add_argument('-og1', '--offset-ground1', type=float, metavar='OFF1',
                               help="first point line of sight offset from the ground level, ex: 6")
    offset1_group.add_argument('-os1', '--offset-sea1', type=float, metavar='OFF1',
                               help="first point line of sight offset from the sea level, ex: 180")
    offset2_group = parser.add_mutually_exclusive_group()
    offset2_group.add_argument('-og2', '--offset-ground2', type=float, metavar='OFF2',
                               help="second point line of sight offset from the ground level, ex: 10")
    offset2_group.add_argument('-os2', '--offset-sea2', type=float, metavar='OFF2',
                               help="second point line of sight offset from the sea level, ex: 200")
    args = parser.parse_args()

    kwargs = {}
    if args.offset_sea1 is not None:
        kwargs['height1'] = args.offset_sea1
        kwargs['above_ground1'] = False
    elif args.offset_ground1 is not None:
        kwargs['height1'] = args.offset_ground1
        kwargs['above_ground1'] = True

    if args.offset_sea2 is not None:
        kwargs['height2'] = args.offset_sea2
        kwargs['above_ground2'] = False
    elif args.offset_ground1 is not None:
        kwargs['height2'] = args.offset_ground2
        kwargs['above_ground2'] = True

    LOGGER.debug("using the following DEM: %s", args.dem)
    LOGGER.debug("requesting profile for the following 'GPS' coordinates")
    LOGGER.debug("first wgs84 lat: %f, long: %f", args.lat1, args.long1)
    LOGGER.debug("second wgs84 lat: %f, long: %f", args.lat2, args.long2)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(args.dem, GA_ReadOnly)

    profile_data = profile.profile(data_source, args.lat1, args.long1, args.lat2, args.long2, **kwargs)

    generate_figure(profile_data, 'profile.png')

if __name__ == '__main__':
    main()
