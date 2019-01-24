# math3d_triangle_mesh.py

from math3d_side import Side
from math3d_vector import Vector
from math3d_triangle import Triangle

class TriangleMesh(object):
    # Most algorithms will assume the mesh approximately forms a proper manifold.
    # Note that all triangles must be wound consistently, and we use this to determine the front and back of the mesh.

    def __init__(self):
        self.vertex_list = []
        self.triangle_list = []

    def clone(self):
        mesh = TriangleMesh()
        mesh.vertex_list = [vertex.clone() for vertex in self.vertex_list]
        mesh.triangle_list = [triangle for triangle in self.triangle_list]
        return mesh

    def surface_fit(self, surface_function):
        # Here we fit a mesh to a surface defined as the zero set of the given scalar-field function.
        # This is not a trivial task.  In some cases, for example, the curvature of the surface can
        # become extreme.  In others, the surface may extend through space without bound.
        pass

    def tri_strip(self):
        pass

    def side(self, point, eps=1e-7):
        # This is a very non-trivial problem.  For one, there may be no clear answer
        # to the question, such as in the case of a Mobius strip or Klein bottle.
        # Secondly, the mesh may form a concave shape.
        pass

    def yield_triangles(self):
        for i, triangle in enumerate(self.triangle_list):
            point_a = self.vertex_list[triangle[0]]
            point_b = self.vertex_list[triangle[1]]
            point_c = self.vertex_list[triangle[2]]
            yield i, Triangle(point_a, point_b, point_c)

    def find_vertex(self, given_vertex, create_if_not_found=False, eps=1e-7):
        for i, vertex in enumerate(self.vertex_list):
            if (given_vertex - vertex).length() < eps:
                return i
        if create_if_not_found:
            self.vertex_list.append(given_vertex.clone())
            return len(self.vertex_list) - 1

    def find_triangle(self, given_triangle):
        pass

    def are_adjacent(self, i, j):
        triangle_a = self.triangle_list[i]
        triangle_b = self.triangle_list[j]
        return len(set(triangle_a).intersection(set(triangle_b))) == 2

    def insert(self, other):
        if isinstance(other, Triangle):
            pass
        elif isinstance(other, list):
            for item in other:
                self.insert(item)

    def cut_against(self, other):
        # Our result here is the smallest possible set of meshes whose union is
        # this mesh and where no member of that set intersects the given mesh.
        mesh = self.clone()
        i = 0
        while i < len(mesh.triangle_list):
            triangle = mesh.triangle_list[i]
            for j, cutting_triangle in other.yield_triangles():
                split_list = triangle.cut_against(cutting_triangle)
                if len(split_list) > 1:
                    del mesh.triangle_list[i]
                    mesh.insert(split_list)
                    # TODO: Mark boundary triangles here?
                    break
            else:
                i += 1
        # TODO: Now how do we proceed?  We need to do a BFS that doesn't proceed across the cut boundary.

class TriangleMeshWalker(object):
    # This class facilitates the ability to do a breadth-first traversal
    # of a given triangle mesh, starting with a given triangle of that mesh.

    def __init__(self):
        pass

    def reset(self, mesh, i):
        self.mesh = mesh
        self.queue = [i]
        self.visited = set()

    def __next__(self):
        if len(self.queue) == 0:
            raise StopIteration()
        i = self.queue.pop(0)
        self.visited.add(i)
        for j in range(len(self.mesh.triangle_list)):
            if self.mesh.are_adjacent(i, j):
                if j not in self.visited and j not in self.queue:
                    self.queue.append(j)
        return i