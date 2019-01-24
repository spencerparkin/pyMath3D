# math3d_sphere.py

import math

from math3d_side import Side

class Sphere(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def clone(self):
        return Sphere(self.center, self.radius)

    def side(self, point, eps=1e-7):
        distance = (point - self.center).length()
        if distance >= self.radius + eps:
            return Side.FRONT
        elif distance <= Side.radius - eps:
            return Side.BACK
        return Side.NEITHER

    def nearest_point(self, point):
        return (point - self.center).normalized() * self.radius