#!/usr/bin/env python

"""
Program that run a web server providing elevation profile and profile graph in a RESTful webservice fashion.
See profile.py and profile_graph.py for generation details.
"""

import argparse
import ConfigParser
from io import BytesIO
import json
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
    def json(self, lat1, long1, lat2, long2, og1=None, os1=None, og2=None, os2=None):
        """
        JSON mapping that outputs the elevations.

        :param lat1: latitude of the first point
        :param long1: longitude of the first point
        :param lat2: latitude of the second point
        :param long2: longitude of the second point
        :param og1: line of sight offset from the ground level of the first point
        :param os1: line of sight offset from the sea level of the first point
        :param og2: line of sight offset from the ground level of the second point
        :param os2: line of sight offset from the sea level of the second point
        :return: the list of elevations between the two points
        """
        if og1 is not None and os1 is not None:
            raise cherrypy.HTTPError(400, "Incompatible parameters 'og1' and 'os1")

        if og2 is not None and os2 is not None:
            raise cherrypy.HTTPError(400, "Incompatible parameters 'og2' and 'os2")

        kwargs = {}
        if os1 is not None:
            kwargs['height1'] = os1
            kwargs['above_ground1'] = False
        elif og1 is not None:
            kwargs['height1'] = og1
            kwargs['above_ground1'] = True

        if os2 is not None:
            kwargs['height2'] = os2
            kwargs['above_ground2'] = False
        elif og2 is not None:
            kwargs['height2'] = og2
            kwargs['above_ground2'] = True

        elevations = profile.profile(self.data_source, float(lat1), float(long1), float(lat2), float(long2), **kwargs)

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(elevations, cls=profile.NumpyEncoder)

    @cherrypy.expose
    def png(self, lat1, long1, lat2, long2, og1=None, os1=None, og2=None, os2=None):
        """
        PNG mapping that outputs a png image of the profile

        :param lat1: latitude of the first point
        :param long1: longitude of the first point
        :param lat2: latitude of the second point
        :param long2: longitude of the second point
        :param og1: line of sight offset from the ground level of the first point
        :param os1: line of sight offset from the sea level of the first point
        :param og2: line of sight offset from the ground level of the second point
        :param os2: line of sight offset from the sea level of the second point
        :return: the picture of the requested profile
        """
        if og1 is not None and os1 is not None:
            raise cherrypy.HTTPError(400, "Incompatible parameters 'og1' and 'os1")

        if og2 is not None and os2 is not None:
            raise cherrypy.HTTPError(400, "Incompatible parameters 'og2' and 'os2")

        kwargs = {}
        if os1 is not None:
            kwargs['height1'] = os1
            kwargs['above_ground1'] = False
        elif og1 is not None:
            kwargs['height1'] = og1
            kwargs['above_ground1'] = True

        if os2 is not None:
            kwargs['height2'] = os2
            kwargs['above_ground2'] = False
        elif og2 is not None:
            kwargs['height2'] = og2
            kwargs['above_ground2'] = True

        buf = BytesIO()
        profile_graph.generate_figure(
            profile.profile(self.data_source, float(lat1), float(long1), float(lat2),
                            float(long2), **kwargs),
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
