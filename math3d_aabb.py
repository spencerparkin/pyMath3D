# math3d_aabb.py

from math3d_vector import Vector
from math3d_point_cloud import PointCloud
from math3d_triangle import Triangle
from math3d_triangle_mesh import TriangleMesh
from math3d_side import Side

class AxisAlignedBoundingBox(object):
    # Results of any algorithm here are left undefined if the min and max
    # points do not form a valid AABB (i.e., min <= max.)

    def __init__(self, min_point=Vector(0.0, 0.0), max_point=Vector(0.0, 0.0)):
        self.min_point = min_point.clone()
        self.max_point = max_point.clone()

    def extent(self):
        return self.max_point - self.min_point

    def make_point(self, point):
        self.min_point = point.clone()
        self.max_point = point.clone()

    def expand_by(self, other):
        if isinstance(other, Vector):
            self.min_point.x = other.x if other.x < self.min_point.x else self.min_point.x
            self.min_point.y = other.y if other.y < self.min_point.y else self.min_point.y
            self.min_point.z = other.z if other.z < self.min_point.z else self.min_point.z
            self.max_point.x = other.x if other.x > self.max_point.x else self.max_point.x
            self.max_point.y = other.y if other.y > self.max_point.y else self.max_point.y
            self.max_point.z = other.z if other.z > self.max_point.z else self.max_point.z
        elif isinstance(other, AxisAlignedBoundingBox):
            self.expand_by(other.min_point)
            self.expand_by(other.max_point)
        elif isinstance(other, PointCloud):
            for point in other.point_list:
                self.expand_by(point)
        elif isinstance(other, Triangle):
            self.expand_by(other.point_a)
            self.expand_by(other.point_b)
            self.expand_by(other.point_c)
        elif isinstance(other, TriangleMesh):
            for triangle in other.yield_triangles():
                self.expand_by(triangle)
        elif type(other) is list:
            for thing in other:
                self.expand_by(thing)

    def contains_point(self, point, eps=1e-7):
        side = self.point_side(point, eps=eps)
        return side != Side.FRONT

    def point_side(self, point, eps=1e-7):
        if self.min_point.x + eps < point.x < self.max_point.x - eps and \
            self.min_point.y + eps < point.y < self.max_point.x - eps and \
            self.min_point.z + eps < point.z < self.max_point.x - eps:
            return Side.BACK

        if point.x < self.min_point.x - eps or point.x > self.max_point.x + eps or \
            point.y < self.min_point.y - eps or point.y > self.max_point.y + eps or \
            point.z < self.min_point.z - eps or point.z > self.max_point.z + eps:
            return Side.FRONT

        return Side.NEITHER