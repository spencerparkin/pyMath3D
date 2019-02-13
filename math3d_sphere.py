# math3d_sphere.py

import math

from math3d_side import Side
from math3d_vector import Vector

class Sphere(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def clone(self):
        return Sphere(self.center, self.radius)

    def side(self, point, eps=1e-7):
        distance = (point - self.center).length()
        if distance >= self.radius + eps:
            return Side.FRONT
        elif distance <= Side.radius - eps:
            return Side.BACK
        return Side.NEITHER

    def nearest_point(self, point):
        return (point - self.center).normalized() * self.radius
    
    def make_mesh(self, latitudes, longitudes):
        # TODO: This works, but it is slow.  We should just build the mesh directly here.
        from math3d_point_cloud import PointCloud
        point_cloud = PointCloud()
        point_cloud.point_list.append(Vector(0.0, self.radius, 0.0))
        point_cloud.point_list.append(Vector(0.0, -self.radius, 0.0))
        for i in range(1, latitudes):
            latitude_angle = float(i) / float(latitudes) * math.pi
            for j in range(0, longitudes):
                longitude_angle = float(j) / float(longitudes) * 2.0 * math.pi
                y = self.radius * math.cos(latitude_angle)
                r = self.radius * math.sin(latitude_angle)
                x = r * math.cos(longitude_angle)
                z = r * math.sin(longitude_angle)
                point_cloud.point_list.append(Vector(x, y, z))
        tri_mesh = point_cloud.find_convex_hull()
        return tri_mesh