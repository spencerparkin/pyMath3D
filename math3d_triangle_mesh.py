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
    TRUNCATED_TETRAHEDRON = 5
    TRUNCATED_TETRAHEDRON = 6

class TriangleMesh(object):
    def __init__(self, mesh=None):
        if mesh is None:
            self.clear()
        else:
            mesh = mesh.clone()
            self.vertex_list = mesh.vertex_list
            self.triangle_list = mesh.triangle_list
    
    def clear(self):
        self.vertex_list = []
        self.triangle_list = []
    
    def clone(self):
        new_mesh = TriangleMesh()
        new_mesh.vertex_list = [vertex.clone() for vertex in self.vertex_list]
        new_mesh.triangle_list = [triangle for triangle in self.triangle_list]
        return new_mesh
    
    def __add__(self, other):
        mesh = TriangleMesh()
        for triangle in self.yield_triangles():
            mesh.add_triangle(triangle)
        for triangle in other.yield_triangles():
            mesh.add_triangle(triangle)
        return mesh
    
    def valid_offset(self, i):
        return True if 0 <= i < len(self.vertex_list) else False

    def is_convex(self):
        pass # TODO: Determine whether the mesh forms a convex or concave shape.

    def yield_triangles(self):
        for triangle in self.triangle_list:
            yield self.make_triangle(triangle)
    
    def to_dict(self):
        data = {
            'vertex_list': [vertex.to_dict() for vertex in self.vertex_list],
            'triangle_list': [triple for triple in self.triangle_list]
        }
        return data
    
    def from_dict(self, data):
        self.vertex_list = [Vector().from_dict(vertex) for vertex in data.get('vertex_list', [])]
        self.triangle_list = [(triple[0], triple[1], triple[2]) for triple in data.get('triangle_list', [])]
        return self
    
    def to_triangle_list(self):
        return [triangle for triangle in self.yield_triangles()]
    
    def from_triangle_list(self, triangle_list):
        self.clear()
        for triangle in triangle_list:
            self.add_triangle(triangle)
        return self
    
    def add_triangle(self, triangle):
        if isinstance(triangle, tuple):
            assert(all([self.valid_offset(triangle[i]) for i in range(3)]))
            self.triangle_list.append(triangle)
        elif isinstance(triangle, Triangle):
            new_triangle = (
                self.find_or_add_vertex(triangle.point_a),
                self.find_or_add_vertex(triangle.point_b),
                self.find_or_add_vertex(triangle.point_c)
            )
            self.triangle_list.append(new_triangle)
    
    def find_triangle(self, triangle, check_forward=True, check_reverse=False):
        triple_list = []
        if check_forward:
            triple_list.append(triangle)
        if check_reverse:
            triple_list.append((triangle[2], triangle[1], triangle[0]))
        for i, existing_triangle in enumerate(self.triangle_list):
            for triple in triple_list:
                if existing_triangle == triple:
                    return i
                if existing_triangle == (triple[1], triple[2], triple[0]):
                    return i
                if existing_triangle == (triple[2], triple[0], triple[1]):
                    return i
    
    def toggle_triangle(self, triangle, check_forward=True, check_reverse=False):
        i = self.find_triangle(triangle, check_forward=check_forward, check_reverse=check_reverse)
        if i is not None:
            del self.triangle_list[i]
        else:
            self.add_triangle(triangle)
    
    def make_triangle(self, triangle):
        if isinstance(triangle, tuple) or isinstance(triangle, list):
            point_a = self.vertex_list[triangle[0]]
            point_b = self.vertex_list[triangle[1]]
            point_c = self.vertex_list[triangle[2]]
            return Triangle(point_a, point_b, point_c)
        elif isinstance(triangle, int):
            return self.make_triangle(self.triangle_list[triangle])
    
    def find_or_add_vertex(self, new_point, eps=1e-7):
        for i, point in enumerate(self.vertex_list):
            if (point - new_point).length() < eps:
                return i
        self.vertex_list.append(new_point)
        return len(self.vertex_list) - 1
    
    def side(self, other, eps=1e-7):
        if isinstance(other, Vector):
            # Assuming this mesh to be a convex hull, tell us which side the given point is on.
            for triangle in self.yield_triangles():
                plane = triangle.calc_plane()
                side = plane.side(other, eps)
                if side == Side.FRONT:
                    return Side.FRONT
            # It could also be on the mesh, but let's just do this for now.
            return Side.BACK
    
    def split_against_mesh(self, tri_mesh):
        # The given mesh must be a convex shape.  If not, the result is left undefined.
        back_mesh_list = []
        front_mesh_list = []

        triangle_list = self.to_triangle_list()

        while len(triangle_list) > 0:
            triangle = triangle_list.pop(0)

            side_list = [tri_mesh.side(triangle[i]) for i in range(3)]
            if all([side == Side.BACK for side in side_list]):
                back_mesh_list.append(triangle)
            else:
                for cutting_triangle in tri_mesh.yield_triangles():
                    result = triangle.intersect_with(cutting_triangle)
                    if result is not None:
                        cutting_plane = cutting_triangle.calc_plane()
                        back_list, front_list = triangle.split_against_plane(cutting_plane)
                        if len(back_list) > 0 and len(front_list) > 0:
                            triangle_list += back_list + front_list
                            break
                else:
                    front_mesh_list.append(triangle)

        front_tri_mesh = TriangleMesh().from_triangle_list(front_mesh_list)
        back_tri_mesh = TriangleMesh().from_triangle_list(back_mesh_list)
        return back_tri_mesh, front_tri_mesh
    
    def calc_center(self):
        from math3d_point_cloud import PointCloud
        return PointCloud(point_list=self.vertex_list).calc_center()
    
    def calc_triangle_center(self):
        from math3d_point_cloud import PointCloud
        point_cloud = PointCloud()
        for triangle in self.yield_triangles():
            point_cloud.add_point(triangle.calc_center())
        return point_cloud.calc_center()
    
    def calc_vertex_normals(self):
        normal_list = []
        for i, vertex in enumerate(self.vertex_list):
            normal = Vector(0.0, 0.0, 0.0)
            for triple in self.triangle_list:
                if any([triple[j] == i for j in range(3)]):
                    triangle = self.make_triangle(triple)
                    plane = triangle.calc_plane()
                    normal += plane.unit_normal
            normal = normal.normalized()
            normal_list.append(normal)
        return normal_list
    
    @staticmethod
    def make_polyhedron(polyhedron):
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
            point_cloud.point_list = [point for point in Vector(phi, 0.0, 0.0).sign_permute(True, False, False)]
            point_cloud.point_list += [point for point in Vector(0.0, phi, 0.0).sign_permute(False, True, False)]
            point_cloud.point_list += [point for point in Vector(0.0, 0.0, phi).sign_permute(False, False, True)]
            point_cloud.point_list += [point for point in Vector(0.5, phi / 2.0, phi * phi / 2.0).sign_permute()]
            point_cloud.point_list += [point for point in Vector(phi * phi / 2.0, 0.5, phi / 2.0).sign_permute()]
            point_cloud.point_list += [point for point in Vector(phi / 2.0, phi * phi / 2.0, 0.5).sign_permute()]
        elif polyhedron == Polyhedron.TRUNCATED_TETRAHEDRON:
            point_cloud.point_list = [Vector(3.0, 1.0, 1.0), Vector(-3.0, -1.0, 1.0), Vector(-3.0, 1.0, -1.0), Vector(3.0, -1.0, -1.0)]
            point_cloud.point_list += [Vector(1.0, 3.0, 1.0), Vector(-1.0, -3.0, 1.0), Vector(-1.0, 3.0, -1.0), Vector(1.0, -3.0, -1.0)]
            point_cloud.point_list += [Vector(1.0, 1.0, 3.0), Vector(-1.0, -1.0, 3.0), Vector(-1.0, 1.0, -3.0), Vector(1.0, -1.0, -3.0)]
        elif polyhedron == Polyhedron.TRUNCATED_OCTAHEDRON:
            point_cloud.point_list += [point for point in Vector(0.0, 1.0, 2.0).sign_permute()]

        return point_cloud.find_convex_hull()
    
    @staticmethod
    def make_disk(center, unit_normal, radius, sides):
        from math3d_transform import AffineTransform
        transform = AffineTransform(translation=center, z_axis=unit_normal)
        transform.linear_transform.x_axis = unit_normal.perpendicular_vector().normalized()
        transform.linear_transform.y_axis = unit_normal.cross(transform.linear_transform.x_axis)
        
        vertex_list = []
        for i in range(sides):
            angle = float(i) / float(sides) * 2.0 * math.pi
            vertex = Vector(radius * math.cos(angle), radius * math.sin(angle), 0.0)
            vertex = transform(vertex)
            vertex_list.append(vertex)

        mesh = TriangleMesh()
        for i in range(sides):
            triangle = Triangle(vertex_list[i], vertex_list[(i + 1) % sides], center)
            mesh.add_triangle(triangle)
        
        return mesh

    def area(self):
        total = 0.0
        for triangle in self.yield_triangles():
            total += triangle.area()
        return total

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
    
    def render_normals(self, length=1.0):
        from OpenGL.GL import GL_LINES, glBegin, glEnd, glVertex3f
        
        glBegin(GL_LINES)
        try:
            for triangle in self.yield_triangles():
                plane = triangle.calc_plane()
                center = triangle.calc_center()
                tip = center + plane.unit_normal * length
                glVertex3f(center.x, center.y, center.z)
                glVertex3f(tip.x, tip.y, tip.z)
        finally:
            glEnd()
    
    def find_boundary_loops(self):
        # If the mesh is not a typical manifold, the results of this function are undefined.
        # The topology of the manifold shouldn't matter.
        
        # Generate a map of all bare edges.
        edge_map = {}
        for triple in self.triangle_list:
            for i in range(3):
                edge = (i, (i + 1) % 3)
                edge = (triple[edge[0]], triple[edge[1]])
                edge_key = '%d|%d' % edge if edge[0] <= edge[1] else '%d|%d' % (edge[1], edge[0])
                if edge_key not in edge_map:
                    edge_map[edge_key] = edge
                else:
                    del edge_map[edge_key]
        
        # Generate a map we can use to follow the edges sequentially.
        # This should work due to consistent winding of the triangles in the mesh.
        vertex_map = {}
        for edge_key in edge_map:
            edge = edge_map[edge_key]
            vertex_map[edge[0]] = edge[1]
            
        # Now go read-off all the loops.
        loop_list = []
        while len(vertex_map) > 0:
            vertex_list = []
            vertex = list(vertex_map.keys())[0]
            while len(vertex_list) == 0 or vertex_list[0] != vertex:
                vertex_list.append(vertex)
                try:
                    new_vertex = vertex_map[vertex]
                except KeyError:
                    break
                del vertex_map[vertex]
                vertex = new_vertex
            loop_list.append(vertex_list)
        
        # Finally, return the list of loops.
        return loop_list
    
    def reduce_vertices(self, eps=0.05):
        while True:
            i, j = self.find_point_pair_within_distance(eps)
            if i is None or j is None:
                break
            
            point_a = self.vertex_list[i]
            point_b = self.vertex_list[j]
            mid_point = (point_a + point_b) / 2.0
            self.vertex_list.append(mid_point)
            
            for k, triple in enumerate(self.triangle_list):
                self.triangle_list[k] = [triple[0], triple[1], triple[2]]
            
            for triple in self.triangle_list:
                for k in range(3):
                    if triple[k] == i or triple[k] == j:
                        triple[k] = len(self.vertex_list) - 1
            
            k = 0
            while k < len(self.triangle_list):
                triple = self.triangle_list[k]
                triple_set = {q for q in triple}
                if len(triple_set) < 3:
                    del self.triangle_list[k]
                else:
                    k += 1
            
            triangle_list = self.to_triangle_list()
            self.from_triangle_list(triangle_list)
        
    def find_point_pair_within_distance(self, distance):
        for i in range(len(self.vertex_list)):
            point_a = self.vertex_list[i]
            for j in range(i + 1, len(self.vertex_list)):
                point_b = self.vertex_list[j]
                if (point_a - point_b).length() <= distance:
                    return i, j
        return None, None