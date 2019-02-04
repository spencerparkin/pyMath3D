# math3d_vector.py

import math

class Vector(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Vector(self.x, self.y, self.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector(x, y, z)

    def length(self):
        return math.sqrt(self.dot(self))

    def normalized(self):
        try:
            scale = 1.0 / self.length()
            return self * scale
        except ZeroDivisionError:
            return None

    def projected(self, unit_normal):
        return unit_normal * self.dot(unit_normal)

    def rejected(self, unit_normal):
        return self - self.projected(unit_normal)

    def angle_between(self, other):
        return math.acos(self.normalized().dot(other.normalized()))

    def rotated(self, unit_axis, angle):
        projection = self.projection(unit_axis)
        rejection = self.rejected(unit_axis)
        x_axis = rejection.normalized()
        y_axis = unit_axis.cross(x_axis)
        radius = rejection.length()
        rejection = x_axis * radius * math.cos(angle) + y_axis * radius * math.sin(angle)
        return projection + rejection
    
    def __hash__(self):
        return hash(str(self))
    
    def __str__(self):
        return '(%f,%f,%f)' % (self.x, self.y, self.z)
    
    def sign_permute(self):
        vector_set = set()
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    vector = self.clone()
                    if i % 2 == 0:
                        vector.x *= -1.0
                    if j % 2 == 0:
                        vector.y *= -1.0
                    if k % 2 == 0:
                        vector.z *= -1.0
                    vector_set.add(vector)
        for vector in vector_set:
            yield vector