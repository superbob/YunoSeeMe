#!/usr/bin/env python

"""
    This program is used to test different formulas to determine the overhead height induced by the earth curvature
    of a point.
    Sine is known to be more precise than cosine when angle is close to zero
    so the formulas should be more precises when using less cosine and more sine.

    In conclusion, after running it, we see that the result is identical (relative difference is always 0)
"""

import math


def quadratic_mean(a, b):  # pylint: disable=invalid-name
    """
        Compute a quadratic mean of to values.

        :param a: first value
        :param b: second value
        :return: quadratic mean
    """
    return math.sqrt((a ** 2 + b ** 2) / 2)


# Values from https://en.wikipedia.org/wiki/Earth_radius#Global_average_radii
EQUATORIAL_RADIUS = 6378137.0
POLAR_RADIUS = 6356752.3
EARTH_RADIUS = float(quadratic_mean(EQUATORIAL_RADIUS, POLAR_RADIUS))


def overhead_height_a(angle, radius):
    """
        Computes the overhead height of the specified angle.

        This formula is the simplest and most intuitive one and uses only one cosine.

        :param angle: the angle to determine overhead height
        :param radius: the radius of the sphere
        :return: the overhead height
    """
    return radius * (1 - math.cos(angle))


def overhead_height_b(angle, radius):
    """
        Computes the overhead height of the specified angle.

        This formula is based on the previous one, replacing the cosine with a sine and the Pythagorean equation.

        :param angle: the angle to determine overhead height
        :param radius: the radius of the sphere
        :return: the overhead height
    """
    cos = math.sqrt(1 - math.sin(angle) ** 2)
    return radius * (1 - cos)


def overhead_height_c(angle, radius):
    """
        Computes the overhead height of the specified angle.

        This formula is based on an geometrical analytic approach,
        it uses a squared sine to determine the overhead height (no cosine, no square root).

        The picture doc/formula_c.svg shows on a circle, where the angles are, alpha being equal to the ``angle`` param,
        r the ``radius`` and h the result.

        Using the following equations::

            gamma = pi / 2 - alpha / 2
            beta = pi / 2 - alpha
            delta = gamma - beta
            l = 2 * sin(alpha / 2) * r
            h = l * sin(delta)

        We can demonstrate that::

            delta = alpha / 2

        And then:

            h = 2 * r * sin(alpha / 2) ** 2

        :param angle: the angle to determine overhead height
        :param radius: the radius of the sphere
        :return: the overhead height
    """
    return 2 * radius * math.sin(angle / 2) ** 2


def main():
    """Main entrypoint"""

    checked_angle = 0.00092629
    result_a = overhead_height_a(checked_angle, EARTH_RADIUS)
    result_b = overhead_height_b(checked_angle, EARTH_RADIUS)
    result_c = overhead_height_c(checked_angle, EARTH_RADIUS)

    print 'spherical correction for %f is a: %f, b: %f, c: %f' % (checked_angle, result_a, result_b, result_c)
    print 'relative difference (a//b) is %f%%' % ((result_a - result_b) / ((result_a + result_b) * 2) * 100)
    print 'relative difference (a//c) is %f%%' % ((result_a - result_c) / ((result_a + result_c) * 2) * 100)
    print 'relative difference (b//c) is %f%%' % ((result_b - result_c) / ((result_b + result_c) * 2) * 100)


if __name__ == '__main__':
    main()
