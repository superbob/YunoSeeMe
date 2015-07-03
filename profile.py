#!/usr/bin/env python

"""
    Script that computes a profile between two points referenced by their WGS 84 latitude and longitude.

    The profile consists in a list of points equally distributed with their:

      * latitude
      * longitude
      * distance from the first point
      * elevation
      * overhead of the curvature of the earth
"""

import logging
import os
import sys
from osgeo import gdal
from gdalconst import GA_ReadOnly
import ConfigParser
import math

import geods
import geometry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

# TODO enforce input arguments
# TODO add radius correction based on the latitude, see: http://en.wikipedia.org/wiki/Earth_radius#Geocentric_radius
# TODO currently only 'sampling', to be 'exact' a full path should be performed on the actual dataset

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

    definition = 512

    LOGGER.debug("requesting profile for the following 'GPS' coordinates")
    LOGGER.debug("first wgs84 lat: " + str(first_lat) + ", long: " + str(first_long))
    LOGGER.debug("second wgs84 lat: " + str(second_lat) + ", long: " + str(second_long))

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(ds_filename, GA_ReadOnly)

    elevations = []
    half_central_angle = geometry.half_central_angle(math.radians(first_lat), math.radians(first_long),
                                                     math.radians(second_lat), math.radians(second_long))
    max_overhead = geometry.overhead_height(half_central_angle, geometry.EARTH_RADIUS)

    for i in range(definition+1):
        i_lat = first_lat + ((second_lat - first_lat) * i) / definition
        i_long = first_long + ((second_long - first_long) * i) / definition
        elevation = geods.read_ds_value_from_wgs84(data_source, i_lat, i_long)
        distance = geometry.distance_between_wgs84_coordinates(first_lat, first_long, i_lat, i_long)
        angle = 2 * geometry.half_central_angle(math.radians(first_lat), math.radians(first_long),
                                                math.radians(i_lat), math.radians(i_long))
        overhead = max_overhead - geometry.overhead_height(half_central_angle - angle, geometry.EARTH_RADIUS)
        elevations.append({'lat': i_lat, 'long': i_long, 'distance': distance, 'elevation': elevation, 'overhead': overhead})

    print "elevation profile between coordinates " + str(first_lat) + ", " + str(first_long) + " and " + str(second_lat)\
          + ", " + str(second_long) + " is"
    print str(elevations)

if __name__ == '__main__':
    main()
