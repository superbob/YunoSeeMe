#!/usr/bin/env python

import logging
import sys
from osgeo import gdal
from gdalconst import GA_ReadOnly

import geofunctions

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger('profile.py')

# TODO enforce input arguments

# ds file name
ds_filename = sys.argv[3]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

# 'GPS' coordinates to get pixel values for
input_lat = float(sys.argv[1])  # ex: 43.588276
input_long = float(sys.argv[2])  # ex: 1.318601

logger.debug("requesting elevation for the following 'GPS' coordinates")
logger.debug("wgs84 lat: " + str(input_lat) + ", long: " + str(input_long))

# register all of the drivers
gdal.AllRegister()
# open the image
ds = gdal.Open(ds_filename, GA_ReadOnly)

# get the value
value = geofunctions.read_ds_value_from_wgs84(ds, input_lat, input_long)

print "elevation for coordinates " + str(input_lat) + ", " + str(input_long) + " is " + str(value)
