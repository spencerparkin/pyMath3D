# math3d_point_cloud.py

from math3d_side import Side
from math3d_triangle import Triangle

class PointCloud(object):
    def __init__(self):
        self.point_list = []

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
    
    def find_convex_hull(self):
        from math3d_triangle_mesh import TriangleMesh
        
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
    
    def fit_plane(self):
        pass # TODO: Use least-squares method.  This will require solving a system of linear equations.