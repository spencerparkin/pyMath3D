# math3d_triangle_mesh.py

import math

from math3d_side import Side
from math3d_triangle import Triangle
from math3d_vector import Vector

class Polyhedron:
    TETRAHEDRON = 0
    HEXAHEDRON = 1
    ICOSAHEDRON = 2
    DODECAHEDRON = 3
    ICOSIDODECAHEDRON = 4

class TriangleMesh(object):
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.vertex_list = []
        self.triangle_list = []
    
    def clone(self):
        new_mesh = TriangleMesh()
        new_mesh.vertex_list = [vertex.clone() for vertex in self.vertex_list]
        new_mesh.triangle_list = [triangle for triangle in self.triangle_list]
        return new_mesh
    
    def yield_triangles(self):
        for triangle in self.triangle_list:
            point_a = self.vertex_list[triangle[0]]
            point_b = self.vertex_list[triangle[1]]
            point_c = self.vertex_list[triangle[2]]
            yield Triangle(point_a, point_b, point_c)
    
    def to_triangle_list(self):
        return [triangle for triangle in self.yield_triangles()]
    
    def from_triangle_list(self, triangle_list):
        self.clear()
        for triangle in triangle_list:
            self.add_triangle(triangle)
        return self
    
    def add_triangle(self, triangle):
        new_triangle = (
            self.find_or_add_vertex(triangle.point_a),
            self.find_or_add_vertex(triangle.point_b),
            self.find_or_add_vertex(triangle.point_c)
        )
        self.triangle_list.append(new_triangle)
    
    def find_or_add_vertex(self, new_point, eps=1e-7):
        for i, point in enumerate(self.vertex_list):
            if (point - new_point).length() < eps:
                return i
        self.vertex_list.append(new_point)
        return len(self.vertex_list) - 1
    
    def side(self, point, eps=1e-7):
        # Assuming this mesh to be a convex hull, tell us which side the given point is on.
        for triangle in self.yield_triangles():
            plane = triangle.calc_plane()
            side = plane.side(point, eps)
            if side == Side.FRONT or side == Side.NEITHER:
                return Side.FRONT
        return Side.BACK
    
    def split_against_mesh(self, tri_mesh):
        # The given mesh should be a convex shape.  If not, the result is left undefined.
        back_mesh_list = []
        front_mesh_list = []
        triangle_list = self.to_triangle_list()
        while len(triangle_list) > 0:
            triangle = triangle_list.pop(0)
            for cutting_triangle in tri_mesh.yield_triangles():
                cutting_plane = cutting_triangle.calc_plane()
                back_list, front_list = triangle.split_against_plane(cutting_plane)
                if len(front_list) == 0:
                    back_mesh_list += back_list
                elif len(back_list) == 0:
                    front_mesh_list += front_list
                else:
                    triangle_list += back_list + front_list
        front_tri_mesh = TriangleMesh().from_triangle_list(front_mesh_list)
        back_tri_mesh = TriangleMesh().from_triangle_list(back_mesh_list)
        return back_tri_mesh, front_tri_mesh
    
    def calc_center(self):
        center = Vector(0.0, 0.0, 0.0)
        for point in self.vertex_list:
            center += point
        center = center / float(len(self.vertex_list))
        return center
    
    def make_polyhedron(self, polyhedron):
        from math3d_point_cloud import PointCloud
        point_cloud = PointCloud()
        
        phi = (1.0 + 5.0 ** 0.5) / 2.0
        
        if polyhedron == Polyhedron.TETRAHEDRON:
            point_cloud.point_list = [point for point in Vector(1.0, 0.0, -1.0 / math.sqrt(2.0)).sign_permute(True, False, False)]
            point_cloud.point_list += [point for point in Vector(0.0, 1.0, 1.0 / math.sqrt(2.0)).sign_permute(False, True, False)]
        elif polyhedron == Polyhedron.HEXAHEDRON:
            point_cloud.point_list = [point for point in Vector(1.0, 1.0, 1.0).sign_permute()]
        elif polyhedron == Polyhedron.ICOSAHEDRON:
            point_cloud.point_list = [point for point in Vector(0.0, 1.0, phi).sign_permute(False, True, True)]
            point_cloud.point_list += [point for point in Vector(phi, 0.0, 1.0).sign_permute(True, False, True)]
            point_cloud.point_list += [point for point in Vector(1.0, phi, 0.0).sign_permute(True, True, False)]
        elif polyhedron == Polyhedron.DODECAHEDRON:
            point_cloud.point_list = [point for point in Vector(1.0, 1.0, 1.0).sign_permute()]
            point_cloud.point_list += [point for point in Vector(0.0, phi, 1.0 / phi).sign_permute(False, True, True)]
            point_cloud.point_list += [point for point in Vector(1.0 / phi, 0.0, phi).sign_permute(True, False, True)]
            point_cloud.point_list += [point for point in Vector(phi, 1.0 / phi, 0.0).sign_permute(True, True, False)]
        elif polyhedron == Polyhedron.ICOSIDODECAHEDRON:
            point_cloud.point_list = [point for point in Vector(0.0, 0.0, phi).sign_permute(False, False, True)]
            point_cloud.point_list += [point for point in Vector(0.5, phi / 2.0, phi * phi / 2.0).sign_permute()]
        
        triangle_list = point_cloud.find_convex_hull()
        return self.from_triangle_list(triangle_list)
    
    def render(self):
        from OpenGL.GL import GL_TRIANGLES, glBegin, glEnd, glVertex3f, glNormal3f
        
        glBegin(GL_TRIANGLES)
        try:
            for triangle in self.yield_triangles():
                plane = triangle.calc_plane()
                glNormal3f(plane.unit_normal.x, plane.unit_normal.y, plane.unit_normal.z)
                glVertex3f(triangle.point_a.x, triangle.point_a.y, triangle.point_a.z)
                glVertex3f(triangle.point_b.x, triangle.point_b.y, triangle.point_b.z)
                glVertex3f(triangle.point_c.x, triangle.point_c.y, triangle.point_c.z)
        except Exception as ex:
            error = str(ex)
            error = None
        finally:
            glEnd()