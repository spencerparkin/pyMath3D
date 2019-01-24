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

    def surface_fit(self, surface_function):
        # Here we fit a mesh to a surface defined as the zero set of the given scalar-field function.
        # This is not a trivial task.  In some cases, for example, the curvature of the surface can
        # become extreme.  In others, the surface may extend through space without bound.
        pass

    def side(self, point, eps=1e-7):
        # This is a very non-trivial problem.  For one, there may be no clear answer
        # to the question, such as in the case of a Mobius strip or Klein bottle.
        # Secondly, the mesh may form a concave shape.
        pass

    def yield_triangles(self):
        for triangle in self.triangle_list:
            point_a = self.vertex_list[triangle[0]]
            point_b = self.vertex_list[triangle[1]]
            point_c = self.vertex_list[triangle[2]]
            yield Triangle(point_a, point_b, point_c)

    def cut_against(self, other):
        # Our result here is the smallest possible set of meshes whose union is this mesh and
        # where no member of that set intersects the given mesh.
        pass # TODO: Make use of intersect method.

    def intersect(self, other):
        # Though the intersection of a mesh with itself is itself, we do not
        # handle this or similar cases.  We're only interested in the case where
        # the intersection is a line-segment mesh.
        from math3d_graph import Graph
        graph = Graph()
        for triangle_a in self.yield_triangles():
            for triangle_b in other.yield_triangles():
                line_segment = triangle_a.intersect_with(triangle_b)
                if line_segment is not None:
                    graph.insert(line_segment)
        return graph

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
            if self._are_adjacent(i, j):
                if j not in self.visited and j not in self.queue:
                    self.queue.append(j)
        return i

    def _are_adjacent(self, i, j):
        triangle_a = self.mesh.triangle_list[i]
        triangle_b = self.mesh.triangle_list[j]
        return len(set(triangle_a).intersection(set(triangle_b))) == 2