#!/usr/bin/env python

import logging
import os
import sys
import cherrypy
import geods
from osgeo import gdal
from gdalconst import GA_ReadOnly
import ConfigParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(os.path.basename(__file__))

config = ConfigParser.ConfigParser()
config.read('config.ini')
ds_filename = config.get('dem', 'location')

# ds file name
if len(sys.argv) >= 2:
    ds_filename = sys.argv[1]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

logger.debug("using the following DEM: %s", ds_filename)

resolution = 512

# register all of the drivers
gdal.AllRegister()
# open the image
ds = gdal.Open(ds_filename, GA_ReadOnly)

class Profile(object):
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/profile/json", 301)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def json(self, first_lat, first_long, second_lat, second_long):
        elevations = []
        for i in range(resolution+1):
            first_lat_float = float(first_lat)
            first_long_float = float(first_long)
            second_lat_float = float(second_lat)
            second_long_float = float(second_long)
            i_lat = first_lat_float + ((second_lat_float - first_lat_float) * i) / resolution
            i_long = first_long_float + ((second_long_float - first_long_float) * i) / resolution
            value = geods.read_ds_value_from_wgs84(ds, i_lat, i_long)
            elevations.append(value.astype(float))
        return elevations

    @cherrypy.expose
    def png(self):
        return "png output"

cherrypy.quickstart(Profile(), '/profile')
