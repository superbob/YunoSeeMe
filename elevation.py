#!/usr/bin/env python

"""
Simple program that prints the elevation in meters of a point referenced by its WGS 84 latitude and longitude.
"""

import argparse
import ConfigParser
import logging
import os

from osgeo import gdal
from gdalconst import GA_ReadOnly

import geods

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))


def main():
    """Main entrypoint"""

    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    config_dem_location = config.get('dem', 'location')

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('lat', type=float, help="latitude, ex: 43.561725")
    parser.add_argument('long', type=float, help="longitude, ex: 1.444796")
    parser.add_argument('-d', '--dem', help="DEM file location, ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'",
                        default=config_dem_location)
    args = parser.parse_args()

    LOGGER.debug("requesting elevation for wgs84 lat: %f, long: %f using the following DEM: %s", args.lat, args.long,
                 args.dem)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(args.dem, GA_ReadOnly)

    # get the value
    value = geods.read_ds_value_from_wgs84(data_source, args.lat, args.long)

    print "elevation for coordinates: %f, %f is %f" % (args.lat, args.long, value)


if __name__ == '__main__':
    main()
