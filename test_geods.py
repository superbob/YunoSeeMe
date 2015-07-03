"""
    Tests for the geods module
"""

import gdal
from gdalconst import GA_ReadOnly
import ConfigParser

import geods

CONFIG = ConfigParser.ConfigParser()
CONFIG.read('pytest.ini')
DS_FILENAME = CONFIG.get('dem', 'location')
EPSILON = 0.001

EPSG3035_WKT = """PROJCS["ETRS89 / ETRS-LAEA",
    GEOGCS["ETRS89",
        DATUM["European_Terrestrial_Reference_System_1989",
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            AUTHORITY["EPSG","6258"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4258"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Lambert_Azimuthal_Equal_Area"],
    PARAMETER["latitude_of_center",52],
    PARAMETER["longitude_of_center",10],
    PARAMETER["false_easting",4321000],
    PARAMETER["false_northing",3210000],
    AUTHORITY["EPSG","3035"],
    AXIS["X",EAST],
    AXIS["Y",NORTH]]"""

def test_transform_from_wgs84():
    expected_x = 3629916.385801
    expected_y = 2316502.956137
    actual = geods.transform_from_wgs84(EPSG3035_WKT, 43.602091, 1.441183)
    assert abs(expected_x - actual[0]) < EPSILON
    assert abs(expected_y - actual[1]) < EPSILON

TRANSFORM = (3000000.0, 25.0, 0, 3000000.0, 0, -25.0)

def test_compute_offset():
    expected_x = 25196
    expected_y = 27339
    actual = geods.compute_offset(TRANSFORM, 3629916.385801, 2316502.956137)
    assert actual[0] == expected_x
    assert actual[1] == expected_y

def test_read_ds_data():
    expected = 151.0
    gdal.AllRegister()
    data_source = gdal.Open(DS_FILENAME, GA_ReadOnly)
    actual = geods.read_ds_data(data_source, 529, 477)
    assert abs(expected - actual) < EPSILON

def test_read_ds_value_from_wgs84():
    expected = 151.0
    gdal.AllRegister()
    data_source = gdal.Open(DS_FILENAME, GA_ReadOnly)
    actual = geods.read_ds_value_from_wgs84(data_source, 43.602091, 1.441183)
    assert abs(expected - actual) < EPSILON
