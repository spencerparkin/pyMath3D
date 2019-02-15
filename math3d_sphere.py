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
    
    def make_mesh(self, subdivision_level=1):
        from math3d_triangle_mesh import TriangleMesh, Polyhedron
        from math3d_triangle import Triangle
        tri_mesh = TriangleMesh.make_polyhedron(Polyhedron.ICOSAHEDRON)
        triangle_list = tri_mesh.to_triangle_list()
        for triangle in triangle_list:
            for i in range(3):
                triangle[i] = triangle[i].normalized() * self.radius
        for i in range(subdivision_level):
            new_triangle_list = []
            for triangle in triangle_list:
                for j in range(3):
                    new_triangle_list.append(Triangle(triangle[j], (triangle[j] + triangle[j + 1]).normalized() * self.radius, (triangle[j] + triangle[j + 2]).normalized() * self.radius))
                new_triangle = Triangle()
                for j in range(3):
                    new_triangle[j] = (triangle[j] + triangle[j + 1]).normalized() * self.radius
                new_triangle_list.append(new_triangle)
            triangle_list = new_triangle_list
        tri_mesh.from_triangle_list(triangle_list)
        for i, vertex in enumerate(tri_mesh.vertex_list):
            tri_mesh.vertex_list[i] = vertex + self.center
        return tri_mesh