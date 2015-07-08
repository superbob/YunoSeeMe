#!/usr/bin/env python

"""
    Script that run a web server doing the same as `profile.py` but in a RESTful webservice fashion.
"""

import logging
import os
import sys
import cherrypy
from osgeo import gdal
from gdalconst import GA_ReadOnly
import ConfigParser
from io import BytesIO

import profile
import profile_graph

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
            # TODO, fix json formatting issue
            """
                JSON mapping that outputs the elevations.

                :param first_lat: latitude of the first point
                :param first_long: longitude of the first point
                :param second_lat: latitude of the second point
                :param second_long: longitude of the second point
                :return: the list of elevations between the two points
            """
            return str(profile.profile(data_source, float(first_lat), float(first_long), float(second_lat),
                                       float(second_long)))

        @cherrypy.expose
        def png(self, first_lat, first_long, second_lat, second_long):
            # TODO, add image size to http headers
            """
                PNG mapping that outputs a png image of the profile

                :param first_lat: latitude of the first point
                :param first_long: longitude of the first point
                :param second_lat: latitude of the second point
                :param second_long: longitude of the second point
                :return: the picture of the requested profile
            """
            buf = BytesIO()
            profile_graph.generate_figure(
                profile.profile(data_source, float(first_lat), float(first_long), float(second_lat),
                                float(second_long)),
                buf)
            buf.seek(0)
            cherrypy.response.headers['Content-Type'] = 'image/png'
            return buf
    # pylint: enable=no-self-use

    cherrypy.quickstart(Profile(), '/profile')

if __name__ == '__main__':
    main()
