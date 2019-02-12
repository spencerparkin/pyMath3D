# math3d_triangle.py

import math

from math3d_side import Side
from math3d_plane import Plane
from math3d_line_segment import LineSegment

class Triangle(object):
    def __init__(self, point_a, point_b, point_c):
        self.point_a = point_a.clone()
        self.point_b = point_b.clone()
        self.point_c = point_c.clone()

    def clone(self):
        return Triangle(self.point_a, self.point_b, self.point_c)

    def calc_plane(self):
        unit_normal = (self.point_b - self.point_a).cross(self.point_c - self.point_a).normalized()
        return Plane(self.point_a, unit_normal)

    def calc_center(self):
        return (self.point_a + self.point_b + self.point_c) / 3.0

    def contains_point(self, point, eps=1e-7):
        if not self.calc_plane().contains_point(point, eps):
            return False
        area_a = Triangle(point, self.point_a, self.point_b).area()
        area_b = Triangle(point, self.point_b, self.point_c).area()
        area_c = Triangle(point, self.point_c, self.point_a).area()
        return math.fabs((area_a + area_b + area_c) - self.area()) < eps

    def contains_edge_point(self, point, eps=1e-7):
        return any([line_segment.contains_point(point, eps) for line_segment in self.yield_line_segments()])

    def contains_interior_point(self, point, eps=1e-7):
        return self.contains_point(point, eps) and not self.contains_edge_point(point, eps)

    def yield_line_segments(self):
        yield LineSegment(self.point_a, self.point_b)
        yield LineSegment(self.point_b, self.point_c)
        yield LineSegment(self.point_c, self.point_a)

    def side(self, point, eps=1e-7):
        return self.calc_plane().side(point, eps)

    def area(self):
        return (self.point_b - self.point_a).cross(self.point_c - self.point_a).length() / 2.0

    def __getitem__(self, i):
        return [self.point_a, self.point_b, self.point_c][i % 3]

    def __setitem__(self, i, point):
        setattr(self, ['point_a', 'point_b', 'point_c'][i % 3], point)

    def split_against_plane(self, plane, eps=1e-7):
        back_list = []
        front_list = []
        
        triangle_list = [self.clone()]
        while len(triangle_list) > 0:
        
            triangle = triangle_list.pop(0)
        
            side_list = [plane.side(triangle[i], eps) for i in range(3)]
            if all([side == Side.NEITHER for side in side_list]):
                pass
            elif all([side == Side.BACK or side == Side.NEITHER for side in side_list]):
                back_list.append(triangle)
            elif all([side == Side.FRONT or side == Side.NEITHER for side in side_list]):
                front_list.append(triangle)
            else:
                for i in range(3):
                    if (side_list[i] == Side.BACK and side_list[(i + 1) % 3] == Side.FRONT or
                            side_list[i] == Side.FRONT and side_list[(i + 1) % 3] == Side.BACK):
                        # This might not be the best tessellation, but it will work.
                        line_segment = LineSegment(triangle[i], triangle[i + 1])
                        alpha = plane.intersect_line_segment(line_segment)
                        point = line_segment.lerp(alpha)
                        triangle_list.append(Triangle(triangle[i], point, triangle[i + 2]))
                        triangle_list.append(Triangle(point, triangle[i + 1], triangle[i + 2]))
                        break
        
        return back_list, front_list

    def intersect_with(self, other, eps=1e-7):
        if isinstance(other, Triangle):
            from math3d_point_cloud import PointCloud
            point_cloud = PointCloud()
            for line_segment in self.yield_line_segments():
                point = other.intersect_with(line_segment)
                if point is not None:
                    point_cloud.add_point(point)
            for line_segment in other.yield_line_segments():
                point = self.intersect_with(line_segment)
                if point is not None:
                    point_cloud.add_point(point)
            point_list = point_cloud.point_list
            if len(point_list) == 2:
                line_segment = LineSegment(point_list[0], point_list[1])
                if line_segment.length() >= eps:
                    return line_segment
        elif isinstance(other, LineSegment):
            plane = self.calc_plane()
            alpha = plane.intersect_line_segment(other)
            if alpha is not None and 0.0 <= alpha <= 1.0:
                point = other.lerp(alpha)
                if self.contains_point(point, eps):
                    return point