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
from osgeo import osr

logger = logging.getLogger('geods.py')

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

    # do the transformation/projection from WGS 84 to the projection ref
    ref_point = transform.TransformPoint(wgs84_long, wgs84_lat)

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
    # TODO tranform[2] and tranform[4] should be checked as equal to 0 (unless raise an error)
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
    """
        Read the ds value at the specified projected coordinates.

        :param ds: the dataset to read the value in
        :param ds_x: the projected x-coordinate
        :param ds_y: the projected y-coordinate
        :return: the value or None if the specified coordinate is a "no data"
    """
    # get georeference info
    transform = ds.GetGeoTransform()

    if transform is None:
        raise Exception("Can only handle 'Affine GeoTransforms'")

    offset_x, offset_y = compute_offset(transform, ds_x, ds_y)

    logger.debug("offset x: %d, offset y: %d", offset_x, offset_y)

    band = ds.GetRasterBand(1)  # 1-based index, data shall be in the first band
    no_data_value = band.GetNoDataValue()
    logger.debug("for this band, no data is: %s", no_data_value)
    data = band.ReadAsArray(offset_x, offset_y, 1, 1)  # read a 1x1 array containing the requested value
    value = data[0, 0]
    if value != no_data_value:
        return value
    else:
        return None

def read_ds_value_from_wgs84(ds, wgs84_lat, wgs84_long):
    """
        Read the ds value at the specified WGS 84 (GPS) coordinates.

        :param ds: the dataset to read the value in
        :param wgs84_lat: the WGS 84 latitude
        :param wgs84_long: the WGS 84 longitude
        :return: the value or None if the specified coordinate is a "no data"
    """
    projected_x, projected_y = transform_from_wgs84(ds.GetProjectionRef(), wgs84_lat, wgs84_long)

    logger.debug("projected x: %f, projected y: %f", projected_x, projected_y)

    return read_ds_data(ds, projected_x, projected_y)
