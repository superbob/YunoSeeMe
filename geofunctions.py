#!/usr/bin/env python
# -*- coding: utf-8 -*-

# get the elevation value from a 'GPS' (WGS 84/ESPG:4326) coordinate
# using the specified DEM GeoTIFF file
# from coordinates in 'GPS' format, it has to be first transformed to the
# ds projection referential and then to the ds pixel offsets

# greatly inspired from
# http://gis.stackexchange.com/questions/6669/converting-projected-geotiff-to-wgs84-with-gdal-and-python
# and http://gis.stackexchange.com/questions/29632/raster-how-to-get-elevation-at-lat-long-using-python

import logging
import math
from osgeo import osr

logger = logging.getLogger('geofunctions.py')

def transform_from_wgs84(projection_ref, wgs84_lat, wgs84_long):
    # get the coordinate system of the projection ref
    ref_cs = osr.SpatialReference()
    ref_cs.ImportFromWkt(projection_ref)

    # get the coordinate system of WGS 84/ESPG:4326/'GPS'
    wgs84_cs = osr.SpatialReference()
    wgs84_cs.ImportFromEPSG(4326)

    # create a transform object to convert between coordinate systems
    transform = osr.CoordinateTransformation(wgs84_cs, ref_cs)

    # do the transformation/projection from WGS 84 to the projection ref
    ref_point = transform.TransformPoint(wgs84_long, wgs84_lat)
    ref_x = ref_point[0]
    ref_y = ref_point[1]

    return ref_x, ref_y

def compute_offset(transform, ds_x, ds_y):
    # tranform[2] and tranform[4] are assumed to be 0 (simpler)
    # TODO should they be checked ?
    # http://www.gdal.org/classGDALDataset.html#af9593cc241e7d140f5f3c4798a43a668
    origin_x = transform[0]
    origin_y = transform[3]
    pixel_width = transform[1]
    pixel_height = transform[5]

    # do the inverse geo transform, flooring to the int
    # TODO better approximation than flooring to the int ?
    offset_x = int((ds_x - origin_x) / pixel_width)
    offset_y = int((ds_y - origin_y) / pixel_height)

    return offset_x, offset_y

def read_ds_data(ds, ds_x, ds_y):
    # get georeference info
    transform = ds.GetGeoTransform()

    if transform is None:
        raise Exception("Can only handle 'Affine GeoTransforms'")

    offset_x, offset_y = compute_offset(transform, ds_x, ds_y)

    logger.debug("offset x: " + str(offset_x) + ", offset y: " + str(offset_y))

    band = ds.GetRasterBand(1)  # 1-based index, data shall be in the first band
    nodata = band.GetNoDataValue()
    logger.debug("for this band, no data is: " + str(nodata))
    data = band.ReadAsArray(offset_x, offset_y, 1, 1)  # read a 1x1 array containing the requested value
    value = data[0, 0]
    if value != nodata:
        return value
    else:
        return None

def read_ds_value_from_wgs84(ds, wgs84_lat, wgs84_long):
    projected_x, projected_y = transform_from_wgs84(ds.GetProjectionRef(), wgs84_lat, wgs84_long)

    logger.debug("projected x: " + str(projected_x) + ", projected y: " + str(projected_y))

    return read_ds_data(ds, projected_x, projected_y)

def half_great_circle_angle(rad_lat1, rad_long1, rad_lat2, rad_long2):
    return math.asin(math.sqrt(
        math.sin((rad_lat2 - rad_lat1) / 2) ** 2
        + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin((rad_long2 - rad_long1) / 2) ** 2))

def quadratic_mean_radius(a, b):
    return math.sqrt((a ** 2 + b ** 2) / 2)

def deg_to_rad(deg):
    return deg * math.pi / 180

# Values from https://en.wikipedia.org/wiki/Earth_radius#Global_average_radii
equatorial_radius = 6378137.0
polar_radius = 6356752.3
earth_quadratic_mean_radius = quadratic_mean_radius(equatorial_radius, polar_radius)

def distance_between_wgs84_coordinates(first_wgs84_lat, first_wgs84_long, second_wgs84_lat, second_wgs84_long):
    half_angle = half_great_circle_angle(deg_to_rad(first_wgs84_lat), deg_to_rad(first_wgs84_long),
                                         deg_to_rad(second_wgs84_lat), deg_to_rad(second_wgs84_long))
    return 2 * earth_quadratic_mean_radius * half_angle
