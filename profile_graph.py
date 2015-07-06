#!/usr/bin/env python

"""
    Script that generate a profile graph, based on `profile.py`.
"""

import logging
import os
import sys
from osgeo import gdal
from gdalconst import GA_ReadOnly
import ConfigParser

import profile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

def generate_plot(profile_data):
    x = [data['distance'] for data in profile_data]
    y_elev = [data['elevation'] for data in profile_data]
    y_elev_plus_correction = [data['elevation'] + data['overhead'] for data in profile_data]

    y2_correction = [data['overhead'] for data in profile_data]

    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    sub_plt.plot(x, y_elev_plus_correction, 'r--', label='Elevation + Correction', dashes=(5, 2))
    sub_plt.plot(x, y_elev, 'k-', label='Elevation')

    sub_plt_twin = sub_plt.twinx()
    sub_plt_twin.plot(x, y2_correction, 'r-', label='Correction')

    sub_plt.legend(loc=2, fontsize='small')
    sub_plt.grid()
    sub_plt.set_xlim(min(x), max(x))
    sub_plt.set_xlabel("Distance (m)")
    sub_plt.set_ylabel("Elevation (m)")

    sub_plt_twin.legend(loc=1, fontsize='small')
    sub_plt_min, sub_plt_max = sub_plt.get_ylim()
    sub_plt_twin.set_ylim(0, sub_plt_max - sub_plt_min)

    for tl in sub_plt_twin.get_yticklabels():
        tl.set_color('r')

    transparent = (1, 1, 1, 0)

    vert1 = list(zip(x, y2_correction))
    poly1 = Polygon(vert1, edgecolor=transparent, facecolor=(1, 0, 0, 0.1))
    sub_plt_twin.add_patch(poly1)

    vert2 = list(zip(x, y_elev_plus_correction)) + list(zip(reversed(x), reversed(y_elev)))
    poly2 = Polygon(vert2, edgecolor=transparent, facecolor=(1, 0, 0, 0.1))
    sub_plt.add_patch(poly2)

    fig.savefig('profile.png')


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
    generate_plot(profile_data)

if __name__ == '__main__':
    main()
