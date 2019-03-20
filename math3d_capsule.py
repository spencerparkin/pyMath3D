# math3d_capsule.py

import math

from math3d_line_segment import LineSegment

class Capsule(object):
    def __init__(self, point_a, point_b, radius):
        self.line_segment = LineSegment(point_a, point_b)
        self.radius = radius

    def clone(self):
        return Capsule(self.line_segment.point_a, self.line_segment.point_b, self.radius)

    def length(self):
        return self.line_segment.length()

    def volume(self):
        return math.pi * self.radius * self.radius * ((4.0 / 3.0) * self.radius + self.length())

    def calc_line(self):
        return self.line_segment.calc_line()

    def contains_point(self, point, eps=1e-7):
        return True if self.line_segment.point_distance(point) < self.radius + eps else False
    
    def make_mesh(self, subdivision_level=1):
        pass # TODO: Use convex hull generator algorithm after computing points.