"""
Collection of functions related to geographical datasets.
Especially:

 * converting coordinates between coordinate systems
 * getting the value at a specific point of a dataset
"""

# greatly inspired from
# http://gis.stackexchange.com/questions/6669/converting-projected-geotiff-to-wgs84-with-gdal-and-python
# and http://gis.stackexchange.com/questions/29632/raster-how-to-get-elevation-at-lat-long-using-python

import logging
import os

import numpy as np
from osgeo import osr

LOGGER = logging.getLogger(os.path.basename(__file__))


def transform_from_wgs84(projection_ref, wgs84_lat, wgs84_long):
    """
    Transforms WGS 84 (GPS) coordinates to the specified coordinate system (WKT).

    Be careful as latitude and longitude are swapped in a Cartesian coordinate system (lat is y, and long is x).

    :param projection_ref: the specified coordinate system supplied in Well Known Text (WKT) format
    :param wgs84_lat: the WGS 84 latitude
    :param wgs84_long: the WGS 84 longitude
    :return: the couple of transformed coordinates (x, y)
    """
    # get the coordinate system of the projection ref
    ref_cs = osr.SpatialReference()
    ref_cs.ImportFromWkt(projection_ref)

    # get the coordinate system of WGS 84/ESPG:4326/'GPS'
    wgs84_cs = osr.SpatialReference()
    wgs84_cs.ImportFromEPSG(4326)

    # create a transform object to convert between coordinate systems
    transform = osr.CoordinateTransformation(wgs84_cs, ref_cs)

    vectorized_transform = np.vectorize(transform.TransformPoint)
    # do the transformation/projection from WGS 84 to the projection ref
    ref_point = vectorized_transform(wgs84_long, wgs84_lat)

    return ref_point[0], ref_point[1]


def compute_offset(transform, ds_x, ds_y):
    """
    Compute the image offset based on the projected coordinates and the transformation.

    The transformation performed is the invert transformation that is described on the transform object.

    The resulting offsets are floored to int.

    Results are valid as long as the transformation is linear (tranform[2] and tranform[4] are 0).

    :param transform: the transformation obtained from Dataset::GetGeoTransform.
    :param ds_x: the projected x-coordinate
    :param ds_y: the projected y-coordinate
    :return: the couple of offsets (x, y)
    """
    # TODO is this exception really useful?
    if transform is None:
        raise Exception("Can only handle 'Affine GeoTransforms'")

    # TODO tranform[2] and tranform[4] should be checked as equal to 0 (unless raise an error)
    # http://www.gdal.org/classGDALDataset.html#af9593cc241e7d140f5f3c4798a43a668
    origin_x = transform[0]
    origin_y = transform[3]
    pixel_width = transform[1]
    pixel_height = transform[5]

    # do the inverse geo transform, flooring to the int
    # TODO better approximation than flooring to the int ?
    offset_x = np.floor_divide(ds_x - origin_x, pixel_width).astype(int)
    offset_y = np.floor_divide(ds_y - origin_y, pixel_height).astype(int)

    return offset_x, offset_y


def read_band_data(band, no_data, offset_x, offset_y):
    """
    Read a single value from a band, replacing "NoData" with None
    :param band: the band to read data from
    :param no_data: the no data value for this band
    :param offset_x: the x offset to read data
    :param offset_y: the y offset to read data
    :return: the value
    """
    value = band.ReadAsArray(offset_x, offset_y, 1, 1)[0, 0]

    if value is not no_data:
        return value
    else:
        return None


vectorized_read_band_data = np.vectorize(read_band_data, excluded=('band', 'no_data'))


def read_ds_data(data_source, offset_x, offset_y):
    """
    Read data from the given data source.
    :param data_source:  the data source to read data from
    :param offset_x: the x offset to read data
    :param offset_y: the y offset to read data
    :return: the value
    """
    band = data_source.GetRasterBand(1)  # 1-based index, data shall be in the first band
    no_data_value = band.GetNoDataValue()
    LOGGER.debug("for this band, no data is: %s", no_data_value)

    if np.isscalar(offset_x) and np.isscalar(offset_y):
        data = read_band_data(band, no_data_value, offset_x, offset_y)
    else:
        data = vectorized_read_band_data(band, no_data_value, offset_x, offset_y)

    return data


def read_ds_value_from_wgs84(data_source, wgs84_lat, wgs84_long):
    """
    Read the ds value at the specified WGS 84 (GPS) coordinates.

    :param data_source: the dataset to read the value in
    :param wgs84_lat: the WGS 84 latitude
    :param wgs84_long: the WGS 84 longitude
    :return: the value or None if the specified coordinate is a "no data"
    """
    projected_x, projected_y = transform_from_wgs84(data_source.GetProjectionRef(), wgs84_lat, wgs84_long)
    LOGGER.debug("projected x: %f, projected y: %f", projected_x, projected_y)

    offset_x, offset_y = compute_offset(data_source.GetGeoTransform(), projected_x, projected_y)
    LOGGER.debug("offset x: %d, offset y: %d", offset_x, offset_y)

    return read_ds_data(data_source, offset_x, offset_y)
