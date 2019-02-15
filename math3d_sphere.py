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
        from math3d_triangle_mesh import TriangleMesh
        from math3d_triangle import Triangle
        def calc_sphere_vertex(i, j):
            latitude_angle = float(i) / float(latitudes) * math.pi
            longitude_angle = float(j) / float(longitudes) * 2.0 * math.pi
            y = self.radius * math.cos(latitude_angle)
            r = self.radius * math.sin(latitude_angle)
            x = r * math.cos(longitude_angle)
            z = r * math.sin(longitude_angle)
            return Vector(x, y, z) + self.center
        tri_mesh = TriangleMesh()
        for i in range(1, latitudes - 1):
            for j in range(0, longitudes):
                tri_mesh.add_triangle(Triangle(calc_sphere_vertex(i, j), calc_sphere_vertex(i + 1, j + 1), calc_sphere_vertex(i + 1, j)))
                tri_mesh.add_triangle(Triangle(calc_sphere_vertex(i, j), calc_sphere_vertex(i, j + 1), calc_sphere_vertex(i + 1, j + 1)))
        for j in range(0, longitudes):
            tri_mesh.add_triangle(Triangle(self.center + Vector(0.0, self.radius, 0.0), calc_sphere_vertex(1, j + 1), calc_sphere_vertex(1, j)))
            tri_mesh.add_triangle(Triangle(self.center + Vector(0.0, -self.radius, 0.0), calc_sphere_vertex(latitudes - 1, j), calc_sphere_vertex(latitudes - 1, j + 1)))
        return tri_mesh