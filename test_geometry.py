import geometry

def test_half_central_angle():
    expected = 0.00092629
    actual = geometry.half_central_angle(0.76075893, 0.02301392, 0.76106595, 0.02553666)
    assert abs(expected - actual) < 0.0000001

def test_quadratic_mean():
    expected = 6367453.627
    actual = geometry.quadratic_mean(geometry.equatorial_radius, geometry.polar_radius)
    assert abs(expected - actual) < 0.1

def test_distance_between_wgs84_coordinates():
    expected = 11796.338490
    actual = geometry.distance_between_wgs84_coordinates(43.588276, 1.318601, 43.605867, 1.463143)
    assert abs(expected - actual) < 0.001
