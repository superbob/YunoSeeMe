#!/usr/bin/env python

"""
Program that output a profile in JSON raw data or plot in PNG, there are style options for the plot.
This one uses the "profile-curved-earth.png from the generate_curved_earth_plot function"
"""

import argparse
import ConfigParser
import logging
import os
import sys

from osgeo import gdal
from gdalconst import GA_ReadOnly

import profiler
import profile_format

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(os.path.basename(__file__))


def parse_args():
    """
    Parses the command line arguments.
    :return: the arguments Namespace object
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('lat1', type=float, help="first point latitude, ex: 43.561725")
    parser.add_argument('long1', type=float, help="first point longitude, ex: 1.444796")
    parser.add_argument('lat2', type=float, help="second point latitude, ex: 43.671348")
    parser.add_argument('long2', type=float, help="second point longitude, ex: 1.225619")
    parser.add_argument('-d', '--dem', help="DEM file location, ex: '/path/to/file/EUD_CP-DEMS_3500025000-AA.tif'")
    offset1_group = parser.add_mutually_exclusive_group()
    offset1_group.add_argument('-og1', '--offset-ground1', type=float, metavar='OFF1',
                               help="first point line of sight offset from the ground level, ex: 6")
    offset1_group.add_argument('-os1', '--offset-sea1', type=float, metavar='OFF1',
                               help="first point line of sight offset from the sea level, ex: 180")
    offset2_group = parser.add_mutually_exclusive_group()
    offset2_group.add_argument('-og2', '--offset-ground2', type=float, metavar='OFF2',
                               help="second point line of sight offset from the ground level, ex: 10")
    offset2_group.add_argument('-os2', '--offset-sea2', type=float, metavar='OFF2',
                               help="second point line of sight offset from the sea level, ex: 200")
    parser.add_argument('-of', '--output-format', choices=['json', 'png'], default='json', help="output format")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-f', '--filename', help="file name")
    output_group.add_argument('-s', '--stdout', action='store_true', help="redirect output to standard output")
    parser.add_argument('-st', '--style', choices=['corrected_elevation', 'curved_sight', 'detailed'],
                        default='corrected_elevation', help="plot style for png output format")
    return parser.parse_args()


def main():
    """Main entrypoint"""
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    config_dem_location = config.get('dem', 'location')

    args = parse_args()

    kwargs = {}
    if args.offset_sea1 is not None:
        kwargs['height1'] = args.offset_sea1
        kwargs['above_ground1'] = False
    elif args.offset_ground1 is not None:
        kwargs['height1'] = args.offset_ground1
        kwargs['above_ground1'] = True

    if args.offset_sea2 is not None:
        kwargs['height2'] = args.offset_sea2
        kwargs['above_ground2'] = False
    elif args.offset_ground1 is not None:
        kwargs['height2'] = args.offset_ground2
        kwargs['above_ground2'] = True

    LOGGER.debug("using the following DEM: %s", args.dem)
    LOGGER.debug("requesting profile for the following 'GPS' coordinates")
    LOGGER.debug("first wgs84 lat: %f, long: %f", args.lat1, args.long1)
    LOGGER.debug("second wgs84 lat: %f, long: %f", args.lat2, args.long2)

    # register all of the drivers
    gdal.AllRegister()
    # open the DEM
    dem_location = args.dem or config_dem_location
    data_source = gdal.Open(dem_location, GA_ReadOnly)

    profile_data = profiler.profile(data_source, args.lat1, args.long1, args.lat2, args.long2, **kwargs)

    if args.output_format == 'png':
        if args.style == 'detailed':
            output_format = profile_format.PNG_detailed
        elif args.style == 'curved_sight':
            output_format = profile_format.PNG_curved_sight
        else:
            output_format = profile_format.PNG

        default_filename = "profile.png"
    else:
        output_format = profile_format.JSON
        default_filename = "profile.json"

    if args.stdout:
        output_format.write_to_fd(profile_data, sys.stdout)
    else:
        filename = args.filename or default_filename
        output_format.write_to_filename(profile_data, filename)

if __name__ == '__main__':
    main()
