# math3d_triangle_mesh.py

import math

from math3d_side import Side
from math3d_triangle import Triangle
from math3d_vector import Vector
from math3d_line_segment import LineSegment

class Polyhedron:
    TETRAHEDRON = 0
    HEXAHEDRON = 1
    ICOSAHEDRON = 2
    DODECAHEDRON = 3
    ICOSIDODECAHEDRON = 4
    TRUNCATED_TETRAHEDRON = 5
    TRUNCATED_OCTAHEDRON = 6

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

    def add_triangle_list(self, triangle_list):
        for triangle in triangle_list:
            self.add_triangle(triangle)

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
        return self
    
    def add_quad(self, v0, v1, v2, v3):
        # Vertices need to be wound CCW.
        self.add_triangle(Triangle(v0, v1, v2))
        self.add_triangle(Triangle(v0, v2, v3))
        return self
    
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

    def find_adjacent_triangles(self, triangle):
        adjacent_triangles_list = []
        for offset, existing_triangle in enumerate(self.triangle_list):
            if existing_triangle == triangle:
                continue
            for i in range(3):
                edge_a = (triangle[i], triangle[(i + 1) % 3])
                for j in range(3):
                    edge_b = (existing_triangle[j], existing_triangle[(j - 1) % 3])
                    if edge_a == edge_b:
                        adjacent_triangles_list.append((existing_triangle, (j - 2) % 3, offset))
        return adjacent_triangles_list

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
    
    def find_vertex(self, given_point, eps=1e-7):
        # TODO: If a BSP tree was available, using that would speed this up considerably.
        #       Instead of a linear search, here we would have a logarithmic one.
        for i, point in enumerate(self.vertex_list):
            if (point - given_point).length() < eps:
                return i
    
    def find_or_add_vertex(self, new_point, eps=1e-7):
        i = self.find_vertex(new_point, eps=eps)
        if i is not None:
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

    def split_into_connected_parts(self):
        # The correctness of this algorithm depends on the mesh being normalized.
        triangle_mesh_list = []
        visited_triangle_set = set()

        while True:

            # Can we find a triangle we have yet to visit?
            queue = []
            for i in range(len(self.triangle_list)):
                if i not in visited_triangle_set:
                    queue = [i]
                    break

            # If no such triangle exists, we're done.
            if len(queue) == 0:
                break

            # Otherwise, perform a DFS starting at the found triangle.
            triangle_mesh = TriangleMesh()
            triangle_mesh_list.append(triangle_mesh)
            while len(queue) > 0:
                i = queue.pop()
                visited_triangle_set.add(i)
                triangle_mesh.add_triangle(self.make_triangle(i))
                adjacent_triangle_list = self.find_adjacent_triangles(self.triangle_list[i])
                for adjacent_triangle in adjacent_triangle_list:
                    i = adjacent_triangle[2]
                    if i not in queue and i not in visited_triangle_set:
                        queue.append(i)

        return triangle_mesh_list

    def split_against_mesh(self, tri_mesh):
        # The given mesh must be a convex shape.  If not, the result is left undefined.
        # The caller might want to reduce/normalize the returned meshes for efficiency purposes.
        # NOTE: Long after writing this routine, I ran across the following article...
        #       https://www.researchgate.net/publication/220721659_Set_operation_on_polyhedra_using_binary_space_partitioning_trees
        #       This paper suggests that here in this routine we could overcome the limitation of
        #       requiring a convex cut-shape by being passed-in instead the BSP-tree representation
        #       of the cut-shape.  This helps us solve the classification problem for non-convex shapes,
        #       which is part of the underlying problem being solved for the algorithm naively implemented here.
        #       There's surely more to it than just that, but anyhow, it's worth noting if I ever return to this code.
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
                    try:
                        plane = triangle.calc_plane()
                    except Exception as ex:
                        error = str(ex)
                        error = None
                    else:
                        normal += plane.unit_normal
            normal = normal.normalized()
            if normal is None:
                normal = Vector(1.0, 0.0, 0.0)
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

    def render(self, random_colors=False):
        from OpenGL.GL import GL_TRIANGLES, glBegin, glEnd, glVertex3f, glNormal3f, glColor3f
        
        glBegin(GL_TRIANGLES)
        try:
            for triangle in self.yield_triangles():
                plane = triangle.calc_plane()
                glNormal3f(plane.unit_normal.x, plane.unit_normal.y, plane.unit_normal.z)
                if random_colors:
                    color = Vector().random()
                    glColor3f(color.x, color.y, color.z)
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

        # The correctness of our algorithm here depends on the mesh being normalized.
        self.normalize()

        line_loop_list = []

        def expand_line_loop():
            for i in range(len(line_loop)):
                for triangle in triangle_queue:
                    for j in range(3):
                        if all([line_loop[(i + k) % len(line_loop)] == triangle[(j + 2 - k) % 3] for k in range(3)]):
                            del line_loop[(i + 1) % len(line_loop)]
                            triangle_queue.remove(triangle)
                            return True
            
            for i in range(len(line_loop)):
                for triangle in triangle_queue:
                    for j in range(3):
                        if all([line_loop[(i + k) % len(line_loop)] == triangle[(j + 1 - k) % 3] for k in range(2)]):
                            line_loop.insert(i + 1, triangle[(j + 2) % 3])
                            triangle_queue.remove(triangle)
                            return True
        
        triangle_queue = [triangle for triangle in self.triangle_list]
        while len(triangle_queue) > 0:
            triangle = triangle_queue.pop()
            line_loop = [triangle[0], triangle[1], triangle[2]]
            while expand_line_loop():
                pass
            line_loop_list.append(line_loop)
        
        # Each island of the mesh now has a line-loop, but each island may
        # also have zero or more holes in it.  So the last step is to possibly
        # break up each line-loop we have so far generated.
        line_loop_queue = line_loop_list
        line_loop_list = []
        while len(line_loop_queue) > 0:
            line_loop = line_loop_queue.pop()
            overlap = False
            count_map = {}
            for i in line_loop:
                if i in count_map:
                    count_map[i] += 1
                    overlap = True
                else:
                    count_map[i] = 1
            if not overlap:
                if len(line_loop) > 2:
                    line_loop_list.append(line_loop)
            else:
                for i in range(len(line_loop)):
                    if count_map[line_loop[i]] > 1 and count_map[line_loop[(i + 1) % len(line_loop)]] == 1:
                        break
                else:
                    continue
                j = (i + 1) % len(line_loop)
                while not (count_map[line_loop[j]] > 1 and count_map[line_loop[(j - 1) % len(line_loop)]] == 1):
                    j = (j + 1) % len(line_loop)
                if line_loop[i] == line_loop[j]:
                    line_loop_a = []
                    line_loop_b = []
                    k = i
                    while k != j:
                        line_loop_a.append(line_loop[k])
                        k = (k + 1) % len(line_loop)
                    while k != i:
                        line_loop_b.append(line_loop[k])
                        k = (k + 1) % len(line_loop)
                    line_loop_queue.append(line_loop_a)
                    line_loop_queue.append(line_loop_b)
            
        return line_loop_list

    def remove_degenerate_triangles(self, eps=1e-7):
        count = 0
        while True:
            for triple in self.triangle_list:
                triangle = self.make_triangle(triple)
                area = triangle.area()
                if area < eps:
                    self.triangle_list.remove(triple)
                    count += 1
                    break
            else:
                break
        return count
    
    def normalize(self, eps=1e-7):
        # The goal here is to find a mesh representing the exact same set of points in space,
        # but having the property that no vertex of the mesh is contained on an edge of a triangle
        # in the mesh and not on an end-point of that edge.
        
        # Note that reduction is not necessary for the correctness of this algorithm, but 1) sometimes
        # it is enough to normalize the mesh, and 2) it may significantly reduce the size of the mesh.
        self.reduce(eps=eps)

        min_area = {'area': 1e-7}

        def split_triangle(min_area):
            for triple in self.triangle_list:
                triangle = self.make_triangle(triple)
                for i in range(3):
                    edge = LineSegment(point_a=triangle[i], point_b=triangle[i + 1])
                    for j, vertex in enumerate(self.vertex_list):
                        if (vertex - edge.point_a).length() < eps:
                            continue
                        if (vertex - edge.point_b).length() < eps:
                            continue
                        if not edge.contains_point(vertex, eps=eps):
                            continue
                        self.triangle_list.remove(triple)
                        self.triangle_list.append((j, triple[(i + 2) % 3], triple[i]))
                        self.triangle_list.append((j, triple[(i + 1) % 3], triple[(i + 2) % 3]))
                        min_area['area'] = min(self.make_triangle(self.triangle_list[-2]).area(), min_area['area'])
                        min_area['area'] = min(self.make_triangle(self.triangle_list[-1]).area(), min_area['area'])
                        return True

        while self.remove_degenerate_triangles(eps=min_area['area']) > 0 or split_triangle(min_area):
            pass
    
    def reduce(self, eps=1e-7):
        def merge_triangles():
            for triangle_a in self.triangle_list:
                for triangle_b in self.triangle_list:
                    if triangle_a is triangle_b:
                        continue
                    for i in range(3):
                        for j in range(3):
                            if triangle_a[(i + 1) % 3] == triangle_b[(j + 2) % 3] and triangle_a[(i + 2) % 3] == triangle_b[(j + 1) % 3]:
                                vector_a = self.vertex_list[triangle_a[i]] - self.vertex_list[triangle_a[(i + 2) % 3]]
                                vector_b = self.vertex_list[triangle_b[j]] - self.vertex_list[triangle_b[(j + 1) % 3]]
                                if math.fabs(vector_a.angle_between(vector_b) - math.pi) < eps:
                                    self.triangle_list.remove(triangle_a)
                                    self.triangle_list.remove(triangle_b)
                                    self.triangle_list.append((triangle_a[i], triangle_a[(i + 1) % 3], triangle_b[j]))
                                    return True
                                vector_a = self.vertex_list[triangle_a[i]] - self.vertex_list[triangle_a[(i + 1) % 3]]
                                vector_b = self.vertex_list[triangle_b[j]] - self.vertex_list[triangle_b[(j + 2) % 3]]
                                if math.fabs(vector_a.angle_between(vector_b) - math.pi) < eps:
                                    self.triangle_list.remove(triangle_a)
                                    self.triangle_list.remove(triangle_b)
                                    self.triangle_list.append((triangle_b[j], triangle_b[(j + 1) % 3], triangle_a[i]))
                                    return True
        
        while self.remove_degenerate_triangles() > 0 or merge_triangles():
            pass
        
        self.remove_unused_vertices()
    
    def remove_unused_vertices(self):
        triangle_list = self.to_triangle_list()
        self.from_triangle_list(triangle_list)