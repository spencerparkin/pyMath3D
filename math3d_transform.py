# math3d_transform.py

from math3d_vector import Vector

class Transform(object):
    # Generally, a transform is just a function.
    
    def __init__(self):
        pass
    
    def __call__(self, input):
        output = input
        return output

class LinearTransform(Transform):
    def __init__(self, x_axis=None, y_axis=None, z_axis=None):
        super().__init__()
        self.x_axis = x_axis.clone() if x_axis is not None else Vector(1.0, 0.0, 0.0)
        self.y_axis = y_axis.clone() if y_axis is not None else Vector(0.0, 1.0, 0.0)
        self.z_axis = z_axis.clone() if z_axis is not None else Vector(0.0, 0.0, 1.0)
    
    def clone(self):
        return LinearTransform(self.x_axis, self.y_axis, self.z_axis)
    
    def __call__(self, input):
        from math3d_triangle_mesh import TriangleMesh
        
        if isinstance(input, Vector):
            output = self.x_axis * input.x + self.y_axis * input.y + self.z_axis * input.z
        elif isinstance(input, list):
            output = [self.__call__(input_item) for input_item in input]
        elif isinstance(input, LinearTransform):
            output = LinearTransform(x_axis=self(input.x_axis), y_axis=self(input.y_axis), z_axis=self(input.z_axis))
        elif isinstance(input, TriangleMesh):
            output = input.clone()
            output.vertex_list = self(input.vertex_list)
        return output
    
    def make_identity(self):
        self.x_axis = Vector(1.0, 0.0, 0.0)
        self.y_axis = Vector(0.0, 1.0, 0.0)
        self.z_axis = Vector(0.0, 0.0, 1.0)
    
    def make_rotation(self, unit_axis, angle):
        self.x_axis = Vector(1.0, 0.0, 0.0).rotated(unit_axis, angle)
        self.y_axis = Vector(0.0, 1.0, 0.0).rotated(unit_axis, angle)
        self.z_axis = Vector(0.0, 0.0, 1.0).rotated(unit_axis, angle)
    
    def make_inverse(self):
        det = self.determinant()
        inverse = LinearTransform()
        try:
            inverse.x_axis.x = (self.y_axis.y * self.z_axis.z - self.z_axis.y * self.y_axis.z) / det
            inverse.y_axis.y = (self.z_axis.y * self.x_axis.z) / det
            # TODO: Finish this later.
            return inverse
        except ZeroDivisionError:
            return None
    
    def determinant(self):
        return self.x_axis.cross(self.y_axis).dot(self.z_axis)
    
class AffineTransform(Transform):
    def __init__(self, x_axis=None, y_axis=None, z_axis=None, translation=None):
        super().__init__()
        self.linear_transform = LinearTransform(x_axis, y_axis, z_axis)
        self.translation = translation.clone() if translation is not None else Vector(0.0, 0.0, 0.0)
    
    def clone(self):
        return AffineTransform(self.linear_transform.x_axis, self.linear_transform.y_axis, self.linear_transform.z_axis, self.translation)
    
    def __call__(self, input):
        from math3d_triangle_mesh import TriangleMesh
        
        if isinstance(input, Vector):
            output = self.linear_transform(input) + self.translation
        elif isinstance(input, list):
            output = [self.__call__(input_item) for input_item in input]
        elif isinstance(input, AffineTransform):
            output = AffineTransform()
            output.linear_transform = self.linear_transform(input.linear_transform)
            output.translation = self.linear_transform(input.translation) + self.translation
        elif isinstance(input, TriangleMesh):
            output = input.clone()
            output.vertex_list = self(input.vertex_list)
        return output
    
    def make_rigid_body_motion(self, unit_axis, angle, translation):
        self.linear_transform.make_rotation(unit_axis, angle)
        self.translation = translation.clone()
    
    def make_translation(self, translation):
        self.linear_transform.make_identity()
        self.translation = translation.clone()
    
    def make_inverse(self):
        pass