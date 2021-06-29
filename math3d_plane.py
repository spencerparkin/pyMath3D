# math3d_plane.py

from math3d_side import Side
from math3d_vector import Vector

class Plane(object):
    def __init__(self, center, normal):
        self.center = center.clone()
        self.unit_normal = normal.clone()
        self.normalize()

    def normalize(self):
        self.unit_normal = self.unit_normal.normalized()
        self.center = self.center.projected(self.unit_normal)

    def clone(self):
        return Plane(self.center, self.unit_normal)

    def to_dict(self):
        data = {
            'center': self.center.to_dict(),
            'unit_normal': self.unit_normal.to_dict()
        }
        return data

    def from_dict(self, data):
        self.center = Vector().from_dict(data.get('center', {}))
        self.unit_normal = Vector().from_dict(data.get('unit_normal', {}))
        return self

    def is_plane(self, plane, eps=1e-7):
        self.normalize()
        plane.normalize()
        if not self.center.is_vector(plane.center, eps):
            return False
        if not self.unit_normal.is_vector(plane.unit_normal, eps):
            return False
        return True

    def contains_point(self, point, eps=1e-7):
        return Side.NEITHER == self.side(point, eps)

    def side(self, point, eps=1e-7):
        distance = self.point_distance(point)
        if distance >= eps:
            return Side.FRONT
        elif distance <= -eps:
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