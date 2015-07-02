import geometry

def test_half_central_angle():
    expected = 0.0016830423969495
    actual = geometry.half_central_angle(0.76029552909832, 0.0252164472196439, 0.76220881138424, 0.0213910869250003)
    assert abs(expected - actual) < 0.0000001

def test_quadratic_mean():
    expected = 6367453.627
    actual = geometry.quadratic_mean(geometry.equatorial_radius, geometry.polar_radius)
    assert abs(expected - actual) < 0.1

def test_distance_between_wgs84_coordinates():
    expected = 21433.388831
    actual = geometry.distance_between_wgs84_coordinates(43.561725, 1.444796, 43.671348, 1.225619)
    assert abs(expected - actual) < 0.001

def test_overhead_height():
    expected = 2.731679321737121
    actual = geometry.overhead_height(0.00092629, geometry.earth_radius)
    assert abs(expected - actual) < 0.001
