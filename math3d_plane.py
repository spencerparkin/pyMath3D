# math3d_plane.py

from math3d_side import Side

class Plane(object):
    def __init__(self, center, unit_normal):
        self.center = center.projected(unit_normal)
        self.unit_normal = unit_normal.clone()

    def clone(self):
        return Plane(self.center, self.unit_normal)

    def contains_point(self, point, eps=1e-7):
        return Side.NEITHER == self.side(point, eps)

    def side(self, point, eps=1e-7):
        distance = self.point_distance(point)
        if distance >= eps:
            return Side.FRONT
        elif distance <= eps:
            return Side.BACK
        return Side.NEITHER

    def nearest_point(self, point):
        return point - (point - self.center).projected(self.unit_normal)
    
    def point_distance(self, point):
        return (point - self.center).dot(self.unit_normal)
    
    def intersect_line_segment(self, line_segment):
        numer = (self.center - line_segment.point_a).dot(self.unit_normal)
        denom = (line_segment.point_b - line_segment.point_a).dot(self.unit_normal)
        try:
            alpha = numer / denom
        except ZeroDivisionError:
            return None
        return alpha