#!/usr/bin/env python

"""
Program that computes a profile between two points referenced by their WGS 84 latitude and longitude.

The profile consists in a list of points equally distributed with their:

  * latitude
  * longitude
  * distance from the first point
  * elevation
  * overhead of the curvature of the earth
"""

import argparse
import ConfigParser
import logging
import math
import os

import numpy as np
from osgeo import gdal
from gdalconst import GA_ReadOnly

import geods
import geometry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

# TODO add radius correction based on the latitude, see: http://en.wikipedia.org/wiki/Earth_radius#Geocentric_radius
# TODO currently only 'sampling', to be 'exact' a full path should be performed on the actual dataset
# TODO rasterize a polyline:
# see: http://gis.stackexchange.com/questions/97306/rasterizing-polyline-data-with-qgis-gdal-custom-line-width

def profile(data_source, wgs84_lat1, wgs86_long1, wgs84_lat2, wgs84_long2,
            height1=0, height2=0, above_ground1=True, above_ground2=True, definition=512):
    profile_data = {}
    half_central_angle = geometry.half_central_angle(math.radians(wgs84_lat1), math.radians(wgs86_long1),
                                                     math.radians(wgs84_lat2), math.radians(wgs84_long2))
    max_overhead = geometry.overhead_height(half_central_angle, geometry.EARTH_RADIUS)
    start_sight = float(height1)
    if above_ground1:
        start_sight += float(geods.read_ds_value_from_wgs84(data_source, wgs84_lat1, wgs86_long1))

    end_sight = float(height2)
    if above_ground2:
        end_sight += float(geods.read_ds_value_from_wgs84(data_source, wgs84_lat2, wgs84_long2))

    profile_data['latitudes'] = latitudes = np.linspace(wgs84_lat1, wgs84_lat2, definition)
    profile_data['longitudes'] = longitudes = np.linspace(wgs86_long1, wgs84_long2, definition)
    profile_data['sights'] = np.linspace(start_sight, end_sight, definition)
    profile_data['elevations'] = geods.read_ds_value_from_wgs84(data_source, latitudes, longitudes)
    profile_data['distances'] = geometry.distance_between_wgs84_coordinates(wgs84_lat1, wgs86_long1, latitudes,
                                                                            longitudes)
    angles = 2 * geometry.half_central_angle(np.deg2rad(wgs84_lat1), np.deg2rad(wgs86_long1), np.deg2rad(latitudes),
                                             np.deg2rad(longitudes))
    profile_data['overheads'] = max_overhead - geometry.overhead_height(half_central_angle - angles,
                                                                        geometry.EARTH_RADIUS)
    return profile_data

def main():
    """Main entrypoint"""

    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    config_dem_location = config.get('dem', 'location')

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('first_lat', type=float, help="first point latitude, ex: 43.561725")
    parser.add_argument('first_long', type=float, help="first point longitude, ex: 1.444796")
    parser.add_argument('second_lat', type=float, help="second point latitude, ex: 43.671348")
    parser.add_argument('second_long', type=float, help="second point longitude, ex: 1.225619")
    parser.add_argument('-d', '--dem', help="DEM file location, ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'",
                        default=config_dem_location)
    args = parser.parse_args()

    LOGGER.debug("using the following DEM: %s", args.dem)
    LOGGER.debug("requesting profile for the following 'GPS' coordinates")
    LOGGER.debug("first wgs84 lat: %f, long: %f", args.first_lat, args.first_long)
    LOGGER.debug("second wgs84 lat: %f, long: %f", args.second_lat, args.second_long)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(args.dem, GA_ReadOnly)

    elevations = profile(data_source, args.first_lat, args.first_long, args.second_lat, args.second_long)

    print "elevation profile between coordinates %f, %f and %f, %f is"\
          % (args.first_lat, args.first_long, args.second_lat, args.second_long)
    print str(elevations)

if __name__ == '__main__':
    main()
