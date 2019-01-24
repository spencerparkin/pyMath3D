# math3d_graph.py

from math3d_line_segment import LineSegment
from math3d_triangle import Triangle

class Graph(object):
    def __init__(self):
        self.vertex_list = []
        self.edge_list = []

    def clone(self):
        pass

    def insert(self, other):
        if isinstance(other, LineSegment):
            pass
        elif isinstance(other, Triangle):
            pass
        elif isinstance(other, Graph):
            pass