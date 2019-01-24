# math3d_line_segment.py

from math3d_line import Line

class LineSegment(object):
    def __init__(self, point_a, point_b):
        self.point_a = point_a.clone()
        self.point_b = point_b.clone()

    def clone(self):
        return LineSegment(self.point_a, self.point_b)

    def length(self):
        return (self.point_a - self.point_b).length()

    def lerp(self, alpha):
        return self.point_a * (1.0 - alpha) + self.point_b * alpha

    def inverse_lerp(self, point):
        pass

    def calc_line(self):
        unit_normal = (self.point_b - self.point_a).normalized()
        return Line(self.point_a, unit_normal)

    def contains_point(self, point, eps=1e-7):
        if not self.calc_line().contains_point(point, eps):
            return False
        alpha = self.inverse_lerp(point)
        return -eps < alpha < 1.0 + eps