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
# import math

import profile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

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
    distance = [x['distance'] for x in profile_data]
    elevation = [x['elevation'] for x in profile_data]

    fig = plt.figure()
    sub_plt = fig.add_subplot(111)
    sub_plt.plot(distance, elevation, '-')
    fig.savefig('test.png')

if __name__ == '__main__':
    main()
