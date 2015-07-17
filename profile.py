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
import json
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

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        if input object is a ndarray it will be converted into an array by calling ndarray.tolist
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return json.JSONEncoder.default(self, obj)

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

    elevations = profile(data_source, args.lat1, args.long1, args.lat2, args.long2, **kwargs)

    print json.dumps(elevations, cls=NumpyEncoder)

if __name__ == '__main__':
    main()
