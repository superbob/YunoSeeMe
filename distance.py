#!/usr/bin/env python

"""
Simple program that computes the distance in meters between two points referenced by their WGS 84 ("GPS")
latitude and longitude.
"""

import argparse

import geometry


def main():
    """Main entrypoint"""

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('first_lat', type=float, help="first point latitude, ex: 43.561725")
    parser.add_argument('first_long', type=float, help="first point longitude, ex: 1.444796")
    parser.add_argument('second_lat', type=float, help="second point latitude, ex: 43.671348")
    parser.add_argument('second_long', type=float, help="second point longitude, ex: 1.225619")
    args = parser.parse_args()

    distance = geometry.distance_between_wgs84_coordinates(args.first_lat, args.first_long,
                                                           args.second_lat, args.second_long)

    print "distance is: %fm" % distance


if __name__ == '__main__':
    main()
