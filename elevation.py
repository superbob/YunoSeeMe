#!/usr/bin/env python

"""
    Simple script that prints the elevation in meters of a point referenced by its WGS 84 latitude and longitude.
"""

import logging
import os
import sys
from osgeo import gdal
from gdalconst import GA_ReadOnly
import ConfigParser

import geods

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

def main():
    """Main entrypoint"""

    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    ds_filename = config.get('dem', 'location')

    # data source file name
    if len(sys.argv) >= 4:
        ds_filename = sys.argv[3]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

    LOGGER.debug("using the following DEM: %s", ds_filename)

    # TODO enforce input arguments

    # 'GPS' coordinates to get pixel values for
    input_lat = float(sys.argv[1])  # ex: 43.561725
    input_long = float(sys.argv[2])  # ex: 1.444796

    LOGGER.debug("requesting elevation for wgs84 lat: %f, long: %f", input_lat, input_long)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(ds_filename, GA_ReadOnly)

    # get the value
    value = geods.read_ds_value_from_wgs84(data_source, input_lat, input_long)

    print 'elevation for coordinates: %f, %f is %f' % (input_lat, input_long, value)

if __name__ == '__main__':
    main()
