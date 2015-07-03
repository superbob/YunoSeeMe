"""
    Collection of geometrical functions.
"""

import math

def half_central_angle(rad_lat1, rad_long1, rad_lat2, rad_long2):
    """
        Return the half of the central angle between the points specified by the given latitudes and longitudes.

        It is based on the Haversine formula (https://en.wikipedia.org/wiki/Haversine_formula).

        :param rad_lat1: the latitude of the first point in radians
        :param rad_long1: the longitude of the first point in radians
        :param rad_lat2: the latitude of the second point in radians
        :param rad_long2: the longitude of the second point in radians
        :return: the half of the great circle angle between the two points
    """
    return math.asin(math.sqrt(
        math.sin((rad_lat2 - rad_lat1) / 2) ** 2
        + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin((rad_long2 - rad_long1) / 2) ** 2))

def quadratic_mean(a, b):  # pylint: disable=invalid-name
    """
        Compute a quadratic mean of to values.

        :param a: first value
        :param b: second value
        :return: quadratic mean
    """
    return math.sqrt((a ** 2 + b ** 2) / 2)

# Values from https://en.wikipedia.org/wiki/Earth_radius#Global_average_radii
EQUATORIAL_RADIUS = 6378137.0
POLAR_RADIUS = 6356752.3
EARTH_RADIUS = quadratic_mean(EQUATORIAL_RADIUS, POLAR_RADIUS)

def distance_between_wgs84_coordinates(wgs84_lat1, wgs84_long1, wgs84_lat2, wgs84_long2):
    """
        Compute the great circle distance between the to specified points.

        :param wgs84_lat1: the latitude of the first point
        :param wgs84_long1: the longitude of the first point
        :param wgs84_lat2: the latitude of the second point
        :param wgs84_long2: the longitude of the second point
        :return: the distance
    """
    half_angle = half_central_angle(math.radians(wgs84_lat1), math.radians(wgs84_long1),
                                    math.radians(wgs84_lat2), math.radians(wgs84_long2))
    return 2 * EARTH_RADIUS * half_angle

def overhead_height(angle, radius):
    """
        Computes the overhead height induced by the earth curvature of the specified angle.

        The formula is detailed in the ``overhead_comparison.py`` file in the ``overhead_height_c`` function.

        :param angle: the angle to determine overhead height
        :param radius: the radius of the sphere
        :return: the overhead height
    """
    return 2 * radius * math.sin(angle / 2) ** 2
