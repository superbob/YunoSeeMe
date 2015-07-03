#!/usr/bin/env python

"""
    Script that run a web server doing the same as `profile.py` but in a RESTful webservice fashion.
"""

import logging
import os
import sys
import cherrypy
import geods
from osgeo import gdal
from gdalconst import GA_ReadOnly
import ConfigParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    ds_filename = config.get('dem', 'location')

    # data source file name
    if len(sys.argv) >= 2:
        ds_filename = sys.argv[1]  # ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'

    LOGGER.debug("using the following DEM: %s", ds_filename)

    resolution = 512

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(ds_filename, GA_ReadOnly)

    # pylint: disable=no-self-use
    class Profile(object):
        """Profile service"""
        @cherrypy.expose
        def index(self):
            """
                Index mapping that redirects to /profile/json.

                :return: nothing, raises an exception to redirect
            """
            raise cherrypy.HTTPRedirect("/profile/json", 301)

        @cherrypy.expose
        @cherrypy.tools.json_out()
        def json(self, first_lat, first_long, second_lat, second_long):
            """
                JSON mapping that outputs the elevations.

                :param first_lat: latitude of the first point
                :param first_long: longitude of the first point
                :param second_lat: latitude of the second point
                :param second_long: longitude of the second point
                :return: the list of elevations between the two points
            """
            elevations = []
            for i in range(resolution+1):
                first_lat_float = float(first_lat)
                first_long_float = float(first_long)
                second_lat_float = float(second_lat)
                second_long_float = float(second_long)
                i_lat = first_lat_float + ((second_lat_float - first_lat_float) * i) / resolution
                i_long = first_long_float + ((second_long_float - first_long_float) * i) / resolution
                value = geods.read_ds_value_from_wgs84(data_source, i_lat, i_long)
                elevations.append(value.astype(float))
            return elevations

        # TODO to be done
        @cherrypy.expose
        def png(self):
            """
                PNG mapping that outputs a png image of the profile
                :return:
            """
            return "png output"
    # pylint: enable=no-self-use

    cherrypy.quickstart(Profile(), '/profile')

if __name__ == '__main__':
    main()
