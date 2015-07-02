#!/usr/bin/env python

"""
    Simple script that computes the distance in meters between two points referenced by their WGS 84
    latitude and longitude.
"""

import geometry
import sys

# 'GPS' coordinates of the first point
first_lat = float(sys.argv[1])  # ex: 43.561725
first_long = float(sys.argv[2])  # ex: 1.444796

# 'GPS' coordinates of the second point
second_lat = float(sys.argv[3])  # ex: 43.671348
second_long = float(sys.argv[4])  # ex: 1.225619

distance = geometry.distance_between_wgs84_coordinates(first_lat, first_long, second_lat, second_long)

print 'distance is: %fm' % distance
