# math3d_point_cloud.py

from math3d_side import Side
from math3d_triangle import Triangle

class PointCloud(object):
    def __init__(self):
        self.point_list = []
    
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
        triangle_list = self._find_initial_tetrahedron_for_convex_hull()
        
        # Proceed by expanding the current convex hull until all points have been incorporated.
        point_list = [point for point in self.point_list]
        while True:
            
            # Remove any points that lie on or within the current convex hull.
            i = 0
            while i < len(point_list):
                point = point_list[i]
                for triangle in triangle_list:
                    plane = triangle.calc_plane()
                    side = plane.side(point)
                    if side == Side.FRONT:
                        i += 1
                        break
                else:
                    del point_list[i]
            
            # We're done when all points have been incorporated into the hull.
            if len(point_list) == 0:
                break
            
            # Arbitrarily choose the first point in the list.  We know it is outside the hull.
            new_point = point_list[0]
            
            # Remove any triangles from our current hull that face the chosen point.
            i = 0
            while i < len(triangle_list):
                triangle = triangle_list[i]
                plane = triangle.calc_plane()
                side = plane.side(new_point)
                if side == Side.FRONT:
                    del triangle_list[i]
                else:
                    i += 1
            
            # Add triangles involving the new point whose plane does not split the current hull.
            # Note that this works, but it is very slow.
            new_triangle_list = []
            for triangle in triangle_list:
                for line_segment in triangle.yield_line_segments():
                    new_triangle = Triangle(new_point, line_segment.point_b, line_segment.point_a)
                    plane = new_triangle.calc_plane()
                    for i in range(len(triangle_list)):
                        k = 0
                        while k < 3:
                            point = triangle_list[i][k]
                            side = plane.side(point)
                            if side == Side.FRONT:
                                break
                            k += 1
                        if k < 3:
                            break
                    else:
                        new_triangle_list.append(new_triangle)
            triangle_list += new_triangle_list
        
        # Finally, return the convex hull as a list of triangles.
        return triangle_list
    
    def fit_plane(self):
        pass