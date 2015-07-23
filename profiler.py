"""
Function that computes a profile between two points referenced by their WGS 84 latitude and longitude.

The profile consists in a list of points equally distributed with their:

  * latitude
  * longitude
  * distance from the first point
  * elevation
  * overhead of the curvature of the earth
"""

import math

import numpy as np

import geods
import geometry


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
