"""
    Tests for the geods module
"""

import numpy as np
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

    assert abs(expected_x - actual[0]) <= EPSILON
    assert abs(expected_y - actual[1]) <= EPSILON


def test_transform_from_wgs84_np():
    expected_x = np.array([3596322.69380009, 3604604.56529048, 3612866.96142577, 3621109.83240858, 3629333.12848138,
                           3637536.79992675, 3645720.79706777, 3653885.0702683, 3662029.56993335, 3670154.24650938])
    expected_y = np.array([2264369.22046415, 2273312.7959045, 2282267.55204012, 2291233.45945101, 2300210.48857829,
                           2309198.6097241, 2318197.79305154, 2327208.0085846, 2336229.22620805, 2345261.41566741])
    actual = geods.transform_from_wgs84(EPSG3035_WKT, np.linspace(43.1, 43.9, 10), np.linspace(1.1, 1.9, 10))

    for exp_x, exp_y, act_x, act_y in zip(expected_x, expected_y, actual[0], actual[1]):
        assert abs(exp_x - act_x) <= EPSILON
        assert abs(exp_y - act_y) <= EPSILON


TRANSFORM = (3000000.0, 25.0, 0, 3000000.0, 0, -25.0)


def test_compute_offset():
    expected_x = 25196
    expected_y = 27339
    actual = geods.compute_offset(TRANSFORM, 3629916.385801, 2316502.956137)

    assert actual[0] == expected_x
    assert actual[1] == expected_y


def test_compute_offset_np():
    expected_x = np.array([24000, 24311, 24622, 24933, 25244, 25555, 25866, 26177, 26488, 26800])
    expected_y = np.array([29600, 29244, 28888, 28533, 28177, 27822, 27466, 27111, 26755, 26400])
    actual = geods.compute_offset(TRANSFORM, np.linspace(3600000., 3670000., 10), np.linspace(2260000., 2340000., 10))

    for exp_x, exp_y, act_x, act_y in zip(expected_x, expected_y, actual[0], actual[1]):
        assert act_x == exp_x
        assert act_y == exp_y


def test_read_ds_data():
    expected = 151.0
    gdal.AllRegister()
    data_source = gdal.Open(DS_FILENAME, GA_ReadOnly)
    actual = geods.read_ds_data(data_source, 529, 477)

    assert abs(expected - actual) <= EPSILON


def test_read_ds_data_np():
    expected = np.array([195, 182, 176, 177, 175, 160, 136, 130, 109, 113])
    gdal.AllRegister()
    data_source = gdal.Open(DS_FILENAME, GA_ReadOnly)
    actual = geods.read_ds_data(data_source, np.linspace(300, 400, 10, dtype=int),
                                np.linspace(400, 300, 10, dtype=int))

    for exp, act in zip(expected, actual):
        assert abs(exp - act) <= EPSILON


def test_read_ds_value_from_wgs84():
    expected = 151.0
    gdal.AllRegister()
    data_source = gdal.Open(DS_FILENAME, GA_ReadOnly)
    actual = geods.read_ds_value_from_wgs84(data_source, 43.602091, 1.441183)

    assert abs(expected - actual) <= EPSILON
