# math3d_point_cloud.py

import random

from math3d_side import Side
from math3d_triangle import Triangle
from math3d_vector import Vector
from math3d_plane import Plane

class PointCloud(object):
    def __init__(self, point_list=None):
        self.point_list = point_list if point_list is not None else []

    def clone(self):
        return PointCloud([point for point in self.point_list])

    def to_dict(self):
        data = {
            'point_list': [point.to_dict() for point in self.point_list]
        }
        return data
    
    def from_dict(self, data):
        self.point_list = [Vector().from_dict(point) for point in data.get('point_list', [])]
        return self

    def calc_center(self):
        center = Vector(0.0, 0.0, 0.0)
        for point in self.point_list:
            center = center + point
        center = center * (1.0 / float(len(self.point_list)))
        return center

    def add_point(self, new_point, eps=1e-7):
        for point in self.point_list:
            if (point - new_point).length() < eps:
                break
        else:
            self.point_list.append(new_point)

    def _find_initial_tetrahedron_for_convex_hull(self):
        for i in range(len(self.point_list)):
            point_a = self.point_list[i]
            for j in range(i + 1, len(self.point_list)):
                point_b = self.point_list[j]
                for k in range(j + 1, len(self.point_list)):
                    point_c = self.point_list[k]
                    for l in range(k + 1, len(self.point_list)):
                        point_d = self.point_list[l]
                        vec_a = point_a - point_d
                        vec_b = point_b - point_d
                        vec_c = point_c - point_d
                        volume = vec_a.cross(vec_b).dot(vec_c)
                        if volume > 0.0:
                            return [
                                Triangle(point_d, point_b, point_a),
                                Triangle(point_d, point_c, point_b),
                                Triangle(point_d, point_a, point_c),
                                Triangle(point_a, point_b, point_c)
                            ]
    
    def find_convex_hull(self, eps=1e-7):
        from math3d_triangle_mesh import TriangleMesh
        
        if len(self.point_list) < 4:
            raise Exception('The point-cloud must consist of at least 4 non-co-planar points.')
        
        triangle_list = self._find_initial_tetrahedron_for_convex_hull()
        tri_mesh = TriangleMesh().from_triangle_list(triangle_list)
        
        # Proceed by expanding the current convex hull until all points have been incorporated.
        point_list = [point for point in self.point_list]
        while True:
            
            # Remove any points that lie on or within the current convex hull.
            i = 0
            while i < len(point_list):
                point = point_list[i]
                if tri_mesh.side(point) == Side.BACK:
                    del point_list[i]
                else:
                    i += 1
            
            # We're done when all points have been incorporated into the hull.
            if len(point_list) == 0:
                break
            
            # Arbitrarily choose the first point in the list.  We know it is outside the hull.
            new_point = point_list[0]
            tri_mesh.vertex_list.append(new_point)
            i = len(tri_mesh.vertex_list) - 1
            
            # Build upon any triangles that face toward our new point.
            triangle_list = [triangle for triangle in tri_mesh.triangle_list]
            for triple in triangle_list:
                triangle = tri_mesh.make_triangle(triple)
                plane = triangle.calc_plane()
                side = plane.side(new_point)
                if side == Side.FRONT:
                    tri_mesh.toggle_triangle(triple, check_forward=True, check_reverse=False)
                    tri_mesh.toggle_triangle((i, triple[0], triple[1]), check_forward=False, check_reverse=True)
                    tri_mesh.toggle_triangle((i, triple[1], triple[2]), check_forward=False, check_reverse=True)
                    tri_mesh.toggle_triangle((i, triple[2], triple[0]), check_forward=False, check_reverse=True)
        
        # Finally, return the convex hull.
        return tri_mesh
    
    def planar_sort(self, plane, eps=1e-7):
        back_list = []
        front_list = []
        neither_list = []
        for i, point in enumerate(self.point_list):
            side = plane.side(point, eps)
            if side == Side.BACK:
                back_list.append(i)
            elif side == Side.FRONT:
                front_list.append(i)
            elif side == Side.NEITHER:
                neither_list.append(i)
        return back_list, front_list, neither_list
    
    def fit_plane(self):
        # f(x,y,z) = ax + by + cz + d is the plane equation.
        # For m points {p_i}, we want to find coefficients a, b, c, d so
        # that all equations f(p_i)=0 are satisfied or as near satisfied
        # as they can be in the sense that |f(p_i)| are all minimized.
        # The least squares method has us define F(a,b,c,d) = Sum_i f^2(p_i),
        # and then we simply solve for a, b, c, d by setting each of
        # dF/da, dF/db, dF/dc, dF/dd to zero, which gives us a homogeneous
        # system of linear equations.  We find a non-trivial solution by
        # looking for an eigenvector with the smallest associated value.
        import numpy
        
        matrix = [[0.0 for i in range(4)] for j in range(4)]
        
        sum_xx = sum([point.x * point.x for point in self.point_list])
        sum_yy = sum([point.y * point.y for point in self.point_list])
        sum_zz = sum([point.z * point.z for point in self.point_list])
        
        sum_xy = sum([point.x * point.y for point in self.point_list])
        sum_xz = sum([point.x * point.z for point in self.point_list])
        sum_yz = sum([point.y * point.z for point in self.point_list])
        
        sum_x = sum([point.x for point in self.point_list])
        sum_y = sum([point.y for point in self.point_list])
        sum_z = sum([point.z for point in self.point_list])

        matrix[0][0] = sum_xx
        matrix[0][1] = sum_xy
        matrix[0][2] = sum_xz
        matrix[0][3] = sum_x
        matrix[1][0] = sum_xy
        matrix[1][1] = sum_yy
        matrix[1][2] = sum_yz
        matrix[1][3] = sum_y
        matrix[2][0] = sum_xz
        matrix[2][1] = sum_yz
        matrix[2][2] = sum_zz
        matrix[2][3] = sum_z
        matrix[3][0] = sum_x
        matrix[3][1] = sum_y
        matrix[3][2] = sum_z
        matrix[3][3] = float(len(self.point_list))

        matrix = numpy.array(matrix)
        
        w, v = numpy.linalg.eig(matrix)
        
        j = -1
        smallest_value = None
        for i in range(4):
            value = w[i]
            if smallest_value is None or abs(value) < abs(smallest_value):
                smallest_value = value
                j = i
        
        unit_normal = Vector(v[0][j], v[1][j], v[2][j]).normalized()
        center = -v[3][j] * unit_normal
        
        plane = Plane(center, unit_normal)
        return plane

    def render(self):
        from OpenGL.GL import GL_POINTS, glBegin, glEnd, glVertex3f

        glBegin(GL_POINTS)
        try:
            for point in self.point_list:
                glVertex3f(point.x, point.y, point.z)
        except Exception as ex:
            error = str(ex)
            error = None
        finally:
            glEnd()