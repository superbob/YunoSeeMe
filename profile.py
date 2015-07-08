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
# TODO rasterize a polyline:
# see: http://gis.stackexchange.com/questions/97306/rasterizing-polyline-data-with-qgis-gdal-custom-line-width

def profile(data_source, wgs84_lat1, wgs86_long1, wgs84_lat2, wgs84_long2,
            height1=0, height2=0, above_ground1=True, above_ground2=True, definition=512):
    elevations = []
    half_central_angle = geometry.half_central_angle(math.radians(wgs84_lat1), math.radians(wgs86_long1),
                                                     math.radians(wgs84_lat2), math.radians(wgs84_long2))
    max_overhead = geometry.overhead_height(half_central_angle, geometry.EARTH_RADIUS)
    start_sight = float(height1)
    if above_ground1:
        start_sight += geods.read_ds_value_from_wgs84(data_source, wgs84_lat1, wgs86_long1)

    end_sight = float(height2)
    if above_ground2:
        end_sight += geods.read_ds_value_from_wgs84(data_source, wgs84_lat2, wgs84_long2)

    for i in range(definition+1):
        i_lat = wgs84_lat1 + ((wgs84_lat2 - wgs84_lat1) * i) / definition
        i_long = wgs86_long1 + ((wgs84_long2 - wgs86_long1) * i) / definition
        i_sight = start_sight + ((end_sight - start_sight) * i) / definition
        elevation = geods.read_ds_value_from_wgs84(data_source, i_lat, i_long)
        distance = geometry.distance_between_wgs84_coordinates(wgs84_lat1, wgs86_long1, i_lat, i_long)
        angle = 2 * geometry.half_central_angle(math.radians(wgs84_lat1), math.radians(wgs86_long1),
                                                math.radians(i_lat), math.radians(i_long))
        overhead = max_overhead - geometry.overhead_height(half_central_angle - angle, geometry.EARTH_RADIUS)
        elevations.append({'lat': i_lat, 'long': i_long, 'distance': distance, 'elevation': elevation,
                           'overhead': overhead, 'sight': i_sight})

    return elevations

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

    elevations = profile(data_source, first_lat, first_long, second_lat, second_long)

    print "elevation profile between coordinates %f, %f and %f, %f is"\
          % (first_lat, first_long, second_lat, second_long)
    print str(elevations)

if __name__ == '__main__':
    main()
