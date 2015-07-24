#!/usr/bin/env python

"""
Program that run a web server providing elevation profile and profile graph in a RESTful webservice fashion.
See profiler.py and profile_output.py for generation details.
"""

import argparse
import ConfigParser
import logging
import os

import cherrypy
from osgeo import gdal
from gdalconst import GA_ReadOnly

import profiler
from profile_format import JSON, PNG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))


class Profile(object):
    """Profile service"""

    def __init__(self, data_source):
        self.data_source = data_source

    def serve_profile(self, lat1, long1, lat2, long2, content_type='application/json', profile_format=JSON,
                      og1=None, os1=None, og2=None, os2=None):
        """
        Generate and format a profile for the given parameters.

        :param lat1: latitude of the first point
        :param long1: longitude of the first point
        :param lat2: latitude of the second point
        :param long2: longitude of the second point
        :param content_type: response content-type to send, defaults to 'application/json'
        :param profile_format: profile format to use, defaults to profile_format.JSON
        :param og1: line of sight offset from the ground level of the first point
        :param os1: line of sight offset from the sea level of the first point
        :param og2: line of sight offset from the ground level of the second point
        :param os2: line of sight offset from the sea level of the second point
        :return: the formatted elevation profile between the two points
        """
        if og1 is not None and os1 is not None:
            raise cherrypy.HTTPError(400, "Incompatible parameters 'og1' and 'os1'")

        if og2 is not None and os2 is not None:
            raise cherrypy.HTTPError(400, "Incompatible parameters 'og2' and 'os2'")

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

        elevations = profiler.profile(self.data_source, float(lat1), float(long1), float(lat2), float(long2), **kwargs)

        cherrypy.response.headers['Content-Type'] = content_type
        return profile_format.get_data(elevations)

    @cherrypy.expose
    def index(self):  # pylint: disable=no-self-use
        """
        Index mapping that redirects to /profile/json.

        :return: nothing, raises an exception to redirect
        """
        raise cherrypy.HTTPRedirect("/profile/json", 301)

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
        return self.serve_profile(lat1, long1, lat2, long2, og1=og1, os1=os1, og2=og2, os2=os2)

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
        return self.serve_profile(lat1, long1, lat2, long2, content_type='image/png', profile_format=PNG,
                                  og1=og1, os1=os1, og2=og2, os2=os2)


def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    config_dem_location = config.get('dem', 'location')

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--dem', help="DEM file location, ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'")
    args = parser.parse_args()

    LOGGER.debug("using the following DEM: %s", args.dem)

    # register all of the drivers
    gdal.AllRegister()
    # open the image
    dem_location = args.dem or config_dem_location
    data_source = gdal.Open(dem_location, GA_ReadOnly)

    cherrypy.quickstart(Profile(data_source), '/profile')


if __name__ == '__main__':
    main()
