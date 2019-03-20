# math3d_cylinder.py

import math

from math3d_line_segment import LineSegment
from math3d_vector import Vector

class Cylinder(object):
    def __init__(self, point_a, point_b, radius):
        self.line_segment = LineSegment(point_a, point_b)
        self.radius = radius
    
    def clone(self):
        return Cylinder(self.line_segment.point_a, self.line_segment.point_b, self.radius)
    
    def length(self):
        return self.line_segment.length()
    
    def calc_line(self):
        return self.line_segment.calc_line()
    
    def contains_point(self, point, eps=1e-7):
        spine = self.line_segment.point_b - self.line_segment.point_a
        unit_normal = spine.normalized()
        vector = point - self.line_segment.point_a
        length = vector.dot(unit_normal)
        if length <= -eps or length >= spine.length() + eps:
            return False
        hypotenuse = vector.length()
        distance = math.sqrt(hypotenuse * hypotenuse - length * length)
        return True if distance < self.radius + eps else False
    
    def make_mesh(self, subdivision_level=1):
        from math3d_point_cloud import PointCloud
        from math3d_transform import AffineTransform
        spine = self.line_segment.point_b - self.line_segment.point_a
        spine_length = spine.length()
        transform = AffineTransform().make_frame(spine, self.line_segment.point_a)
        count = 4 * (subdivision_level + 1)
        point_cloud = PointCloud()
        for i in range(count):
            angle = 2.0 * math.pi * float(i) / float(count)
            vertex = Vector(self.radius * math.cos(angle), self.radius * math.sin(angle), 0.0)
            point_cloud.point_list.append(transform(vertex))
            point_cloud.point_list.append(transform(vertex + Vector(0.0, 0.0, spine_length)))
        return point_cloud.find_convex_hull()