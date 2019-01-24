# math3d_line.py

class Line(object):
    def __init__(self, center, unit_normal):
        self.center = center.clone()
        self.unit_normal = unit_normal.clone()

    def clone(self):
        return Line(self.center, self.unit_normal)

    def contains_point(self, point, eps=1e-7):
        return (point - self.center).rejected(self.unit_normal).length() < eps