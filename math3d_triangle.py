# math3d_triangle.py

import math

from math3d_plane import Plane
from math3d_line_segment import LineSegment

class Triangle(object):
    def __init__(self, point_a, point_b, point_c):
        self.point_a = point_a.clone()
        self.point_b = point_b.clone()
        self.point_c = point_c.clone()

    def calc_plane(self):
        unit_normal = (self.point_b - self.point_a).cross(self.point_c - self.point_a).normalized()
        return Plane(self.point_a, unit_normal)

    def contains_point(self, point, eps=1e-7):
        if not self.calc_plane().contains_point(point, eps):
            return False
        area_a = Triangle(point, self.point_a, self.point_b).area()
        area_b = Triangle(point, self.poitn_b, self.point_c).area()
        area_c = Triangle(point. self.point_c, self.point_a).area()
        return math.abs((area_a + area_b + area_c) - self.area()) < eps

    def yield_line_segments(self):
        yield LineSegment(self.point_a, self.point_b)
        yield LineSegment(self.point_b, self.point_c)
        yield LineSegment(self.point_c, self.point_a)

    def side(self, point, eps=1e-7):
        return self.calc_plane().side(point, eps)

    def area(self):
        return (self.point_b - self.point_a).cross(self.point_c - self.point_a).length() / 2.0

    def intersect_with(self, other):
        if isinstance(other, Triangle):
            # Though the intersection of a triangle with itself is itself, we are not
            # interested in this or similar cases.  We are only interested in the case
            # where the intersection is a non-generate line-segment.
            pass