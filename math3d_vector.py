# math3d_vector.py

import math

class Vector(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Vector(self.x, self.y, self.z)

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z
        }
    
    def from_dict(self, data):
        self.x = data.get('x', 0.0)
        self.y = data.get('y', 0.0)
        self.z = data.get('z', 0.0)
        return self

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, float):
            return Vector(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, float):
            return Vector(self.x / other, self.y / other, self.z / other)
        elif isinstance(other, Vector):
            return Vector(self.x / other.x, self.y / other.y, self.z / other.z)

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
        projection = self.projected(unit_axis)
        rejection = self.rejected(unit_axis)
        x_axis = rejection.normalized()
        if x_axis is None:
            return self.clone()
        y_axis = unit_axis.cross(x_axis)
        radius = rejection.length()
        rejection = x_axis * radius * math.cos(angle) + y_axis * radius * math.sin(angle)
        return projection + rejection
    
    def perpendicular_vector(self, eps=1e-7):
        if math.fabs(self.x) > eps or math.fabs(self.y) > eps:
            return Vector(self.y, -self.x, 0.0)
        elif math.fabs(self.x) > eps or math.fabs(self.z) > eps:
            return Vector(self.z, 0.0, -self.x)
        elif math.fabs(self.y) > eps or math.fabs(self.z) > eps:
            return Vector(0.0, self.z, -self.y)
    
    def __hash__(self):
        return hash(str(self))
    
    def __str__(self):
        return '(%f, %f, %f)' % (self.x, self.y, self.z)
    
    def __eq__(self, other):
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        if self.z != other.z:
            return False
        return True
    
    def sign_permute(self, flip_x=True, flip_y=True, flip_z=True):
        x_list = [1.0, -1.0] if flip_x else [1.0]
        y_list = [1.0, -1.0] if flip_y else [1.0]
        z_list = [1.0, -1.0] if flip_z else [1.0]
        for x_scale in x_list:
            for y_scale in y_list:
                for z_scale in z_list:
                    yield Vector(x_scale, y_scale, z_scale) * self