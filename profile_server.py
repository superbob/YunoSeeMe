#!/usr/bin/env python

"""
Program that run a web server providing elevation profile and profile graph in a RESTful webservice fashion.
See profile.py and profile_graph.py for generation details.
"""

import argparse
import ConfigParser
from io import BytesIO
import logging
import os

import cherrypy
from osgeo import gdal
from gdalconst import GA_ReadOnly

import profile
import profile_graph

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))

class Profile(object):
    """Profile service"""
    def __init__(self, data_source):
        self.data_source = data_source

# pylint: disable=no-self-use
    @cherrypy.expose
    def index(self):
        """
        Index mapping that redirects to /profile/json.

        :return: nothing, raises an exception to redirect
        """
        raise cherrypy.HTTPRedirect("/profile/json", 301)
# pylint: enable=no-self-use

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def json(self, lat1, long1, lat2, long2):
        # TODO, fix json formatting issue
        """
        JSON mapping that outputs the elevations.

        :param lat1: latitude of the first point
        :param long1: longitude of the first point
        :param lat2: latitude of the second point
        :param long2: longitude of the second point
        :return: the list of elevations between the two points
        """
        return str(profile.profile(self.data_source, float(lat1), float(long1), float(lat2),
                                   float(long2)))

    @cherrypy.expose
    def png(self, lat1, long1, lat2, long2):
        # TODO, add image size to http headers
        """
        PNG mapping that outputs a png image of the profile

        :param lat1: latitude of the first point
        :param long1: longitude of the first point
        :param lat2: latitude of the second point
        :param long2: longitude of the second point
        :return: the picture of the requested profile
        """
        buf = BytesIO()
        profile_graph.generate_figure(
            profile.profile(self.data_source, float(lat1), float(long1), float(lat2),
                            float(long2)),
            buf)
        buf.seek(0)
        cherrypy.response.headers['Content-Type'] = 'image/png'
        return buf

def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    config_dem_location = config.get('dem', 'location')

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--dem', help="DEM file location, ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'",
                        default=config_dem_location)
    args = parser.parse_args()

    LOGGER.debug("using the following DEM: %s", args.dem)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    data_source = gdal.Open(args.dem, GA_ReadOnly)

    cherrypy.quickstart(Profile(data_source), '/profile')

if __name__ == '__main__':
    main()
