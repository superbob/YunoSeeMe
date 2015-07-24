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


def compute_curved_earth_correction(wgs84_lat1, wgs84_long1, wgs84_lat2, wgs84_long2, latitudes, longitudes):
    """
    Compute the curved earth correction with the given parameters.

    :param wgs84_lat1: the latitude of the starting point
    :param wgs84_long1: the longitude of the starting point
    :param wgs84_lat2: the latitude of the ending point
    :param wgs84_long2: the longitude of the ending point
    :param latitudes: latitudes of the points to compute the correction at
    :param longitudes: longitudes of the points to compute the correction at
    :return:
    """
    half_central_angle = geometry.half_central_angle(math.radians(wgs84_lat1), math.radians(wgs84_long1),
                                                     math.radians(wgs84_lat2), math.radians(wgs84_long2))
    max_overhead = geometry.overhead_height(half_central_angle, geometry.EARTH_RADIUS)
    angles = geometry.central_angle(np.deg2rad(wgs84_lat1), np.deg2rad(wgs84_long1), np.deg2rad(latitudes),
                                             np.deg2rad(longitudes))
    return max_overhead - geometry.overhead_height(half_central_angle - angles, geometry.EARTH_RADIUS)


# TODO add radius correction based on the latitude, see: http://en.wikipedia.org/wiki/Earth_radius#Geocentric_radius
# TODO currently only 'sampling', to be 'exact' a full path should be performed on the actual dataset
# TODO rasterize a polyline:
# see: http://gis.stackexchange.com/questions/97306/rasterizing-polyline-data-with-qgis-gdal-custom-line-width
def profile(data_source, wgs84_lat1, wgs84_long1, wgs84_lat2, wgs84_long2, height1=0, height2=0, above_ground1=True,
            above_ground2=True, definition=512):
    """
    Generates a profile with the given parameters and elevation data source.

    :param data_source: the data_source to read elevation data from
    :param wgs84_lat1: the latitude of the starting point
    :param wgs84_long1: the longitude of the starting point
    :param wgs84_lat2: the latitude of the ending point
    :param wgs84_long2: the longitude of the ending point
    :param height1: the sight height for the starting point, defaults to 0
    :param height2: the sight height for the ending point, defaults to 0
    :param above_ground1: is sight height fir the starting point above the ground (True) or above the sea (False),
                          defaults to True
    :param above_ground2: is sight height fir the ending point above the ground (True) or above the sea (False),
                          defaults to True
    :param definition: the number of points to sample including the starting point and the ending point
    :return: the profile data composed of numpy arrays for latitudes, longitudes, sights, elevations, distances and
             overheads (correction of the rounded earth profile)
    """
    profile_data = {}
    profile_data['latitudes'] = latitudes = np.linspace(wgs84_lat1, wgs84_lat2, definition)
    profile_data['longitudes'] = longitudes = np.linspace(wgs84_long1, wgs84_long2, definition)
    profile_data['elevations'] = geods.read_ds_value_from_wgs84(data_source, latitudes, longitudes)
    start_sight = float(height1)
    if above_ground1:
        start_sight += float(profile_data['elevations'][0])
    end_sight = float(height2)
    if above_ground2:
        end_sight += float(profile_data['elevations'][-1])
    profile_data['sights'] = np.linspace(start_sight, end_sight, definition)
    profile_data['distances'] = geometry.distance_between_wgs84_coordinates(wgs84_lat1, wgs84_long1, latitudes,
                                                                            longitudes)
    profile_data['overheads'] = compute_curved_earth_correction(wgs84_lat1, wgs84_long1, wgs84_lat2, wgs84_long2,
                                                                latitudes, longitudes)
    return profile_data
