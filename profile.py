#!/usr/bin/env python

import logging
import sys
from osgeo import gdal
from gdalconst import GA_ReadOnly

import geods

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger('profile.py')

# TODO enforce input arguments
# For curved earth profile, calculate radius :
# http://en.wikipedia.org/wiki/Earth_radius#Geocentric_radius
# and then compute line of sight as if it was on a fixed radius sphere
# quadratic mean radius
# http://en.wikipedia.org/wiki/Earth_radius#Rectifying_radius
# maybe need to use some haversine magic to compute angles
# TODO currently only 'sampling', to be 'exact' a full path should be performed on the actual dataset

# ds file name
ds_filename = sys.argv[5]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

# 'GPS' coordinates of the first point
first_lat = float(sys.argv[1])  # ex: 43.588276
first_long = float(sys.argv[2])  # ex: 1.318601

# 'GPS' coordinates of the second point
second_lat = float(sys.argv[3])  # ex: 43.605867
second_long = float(sys.argv[4])  # ex: 1.463143

definition = 512

logger.debug("requesting profile for the following 'GPS' coordinates")
logger.debug("first wgs84 lat: " + str(first_lat) + ", long: " + str(first_long))
logger.debug("second wgs84 lat: " + str(second_lat) + ", long: " + str(second_long))

# register all of the drivers
gdal.AllRegister()
# open the image
ds = gdal.Open(ds_filename, GA_ReadOnly)

elevations = []
for i in range(definition+1):
    i_lat = first_lat + ((second_lat - first_lat) * i) / definition
    i_long = first_long + ((second_long - first_long) * i) / definition
    value = geods.read_ds_value_from_wgs84(ds, i_lat, i_long)
    elevations.append(value)

print "elevation profile between coordinates " + str(first_lat) + ", " + str(first_long) + " and " + str(second_lat)\
      + ", " + str(second_long) + " is"
print str(elevations)
