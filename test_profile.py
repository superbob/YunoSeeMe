"""
    Tests for the profile module
"""

import gdal
from gdalconst import GA_ReadOnly
import ConfigParser

import profiler

CONFIG = ConfigParser.ConfigParser()
CONFIG.read('pytest.ini')
DS_FILENAME = CONFIG.get('dem', 'location')
EPSILON = 0.001


def test_profile():
    expected_distances = [0., 9166.70306504, 18329.92411276, 27489.65733578, 36645.89692202, 45798.63705469,
                          54947.87191227, 64093.59566856, 73235.80249261, 82374.48654874]
    expected_elevations = [280., 326., 228., 184., 241., 158., 224., 209., 190., 184.]
    expected_latitudes = [43.2, 43.2666, 43.3333, 43.4, 43.4666, 43.5333, 43.6, 43.6666, 43.7333, 43.8]
    expected_longitudes = [1.2, 1.2666, 1.3333, 1.4, 1.4666, 1.5333, 1.6, 1.6666, 1.7333, 1.8]
    expected_overheads = [0., 52.6953, 92.1818, 118.4743, 131.5879, 131.5375, 118.3384, 92.0056, 52.5544, 0.]
    expected_sights = [280., 269.3333, 258.6667, 248.0, 237.3333, 226.6667, 216.0, 205.3333, 194.6667, 184.]

    gdal.AllRegister()
    data_source = gdal.Open(DS_FILENAME, GA_ReadOnly)
    actual = profiler.profile(data_source, 43.2, 1.2, 43.8, 1.8, definition=10)

    for exp_d, act_d in zip(expected_distances, actual['distances']):
        assert abs(exp_d - act_d) <= EPSILON

    for exp_d, act_d in zip(expected_elevations, actual['elevations']):
        assert abs(exp_d - act_d) <= EPSILON

    for exp_d, act_d in zip(expected_latitudes, actual['latitudes']):
        assert abs(exp_d - act_d) <= EPSILON

    for exp_d, act_d in zip(expected_longitudes, actual['longitudes']):
        assert abs(exp_d - act_d) <= EPSILON

    for exp_d, act_d in zip(expected_overheads, actual['overheads']):
        assert abs(exp_d - act_d) <= EPSILON

    for exp_d, act_d in zip(expected_sights, actual['sights']):
        assert abs(exp_d - act_d) <= EPSILON
