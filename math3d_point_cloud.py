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
    
    def find_convex_hull(self, method='silhouette', eps=1e-7):
        from math3d_triangle_mesh import TriangleMesh
        
        if len(self.point_list) < 4:
            raise Exception('The point-cloud must consist of at least 4 non-co-planar points.')
        
        if method == 'silhouette':
            
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
        
        elif method == 'gift_wrap':

            tri_mesh = TriangleMesh()

            # Find a point on the surface of the hull.
            j = 0
            for i in range(1, len(self.point_list)):
                if self.point_list[i].x > self.point_list[j].x:
                    j = i
            
            # Find an edge on the surface of the hull.
            point_a = self.point_list[j]
            for point_b in self.point_list:
                vector_a = point_b - point_a
                vector_b = Vector(1.0, 0.0, 0.0).cross(vector_a)
                normal = vector_a.cross(vector_b).normalized()
                plane = Plane(point_a, normal)
                back_list, front_list, neither_list = self.planar_sort(plane)
                if len(front_list) == 0:
                    break
            else:
                raise Exception('Failed to find edge on surface of convex hull.')
            
            while True:
                
                # Find a non-generate triangle involving the edge on the surface of the hull.
                while True:
                    point_c = random.choice(self.point_list)
                    triangle = Triangle(point_a, point_b, point_c)
                    if triangle.area() > eps:
                        break
                
                # Float the plane to the surface.
                while True:
                    plane = triangle.calc_plane()
                    largest_distance = 0.0
                    i = 0
                    point_list = [point for point in self.point_list]
                    while i < len(point_list):
                        distance = plane.point_distance(point_list[i])
                        if distance >= eps:
                            if distance > largest_distance:
                                largest_distance = distance
                                triangle[2] = point_list[i]
                            i += 1
                        else:
                            del point_list[i]
                    if largest_distance == 0.0:
                        break
                
                # Now find the convex hull of the points in the plane.
                #...then add triangles to mesh...
                
                # Now find a new edge of the surface of the hull that needs a triangle with it to be floated up.
                naked_edge = tri_mesh.find_naked_edge()
                if naked_edge is None:
                    break # We're done when no more naked edges can be found.
                
                # Note the reversal of order here.  This ensures we don't find the same triangle from whence the naked edge came.
                point_a = tri_mesh.vertex_list[naked_edge[1]]
                point_b = tri_mesh.vertex_list[naked_edge[0]]
        
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
        pass # TODO: Use least-squares method.  This will require solving a system of linear equations.