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
    
    def to_dict(self):
        data = {
            'x_axis': self.x_axis.to_dict(),
            'y_axis': self.y_axis.to_dict(),
            'z_axis': self.z_axis.to_dict()
        }
        return data
    
    def from_dict(self, data):
        self.x_axis = Vector().from_dict(data.get('x_axis'))
        self.y_axis = Vector().from_dict(data.get('y_axis'))
        self.z_axis = Vector().from_dict(data.get('z_axis'))
        return self
    
    def __call__(self, input):
        from math3d_triangle_mesh import TriangleMesh
        from math3d_point_cloud import PointCloud
        
        if isinstance(input, Vector):
            output = self.x_axis * input.x + self.y_axis * input.y + self.z_axis * input.z
        elif isinstance(input, list):
            output = [self.__call__(input_item) for input_item in input]
        elif isinstance(input, LinearTransform):
            output = LinearTransform(x_axis=self(input.x_axis), y_axis=self(input.y_axis), z_axis=self(input.z_axis))
        elif isinstance(input, TriangleMesh):
            output = input.clone()
            output.vertex_list = self(input.vertex_list)
        elif isinstance(input, PointCloud):
            output = PointCloud(self(input.point_list))
        return output
    
    def make_identity(self):
        self.x_axis = Vector(1.0, 0.0, 0.0)
        self.y_axis = Vector(0.0, 1.0, 0.0)
        self.z_axis = Vector(0.0, 0.0, 1.0)
        return self
    
    def make_rotation(self, unit_axis, angle):
        self.x_axis = Vector(1.0, 0.0, 0.0).rotated(unit_axis, angle)
        self.y_axis = Vector(0.0, 1.0, 0.0).rotated(unit_axis, angle)
        self.z_axis = Vector(0.0, 0.0, 1.0).rotated(unit_axis, angle)
        return self
    
    def make_uniform_scale(self, scale):
        self.x_axis = Vector(scale, 0.0, 0.0)
        self.y_axis = Vector(0.0, scale, 0.0)
        self.z_axis = Vector(0.0, 0.0, scale)
        return self

    def make_non_uniform_scale(self, x_scale, y_scale, z_scale):
        self.x_axis = Vector(x_scale, 0.0, 0.0)
        self.y_axis = Vector(0.0, y_scale, 0.0)
        self.z_axis = Vector(0.0, 0.0, z_scale)
        return self
    
    def calc_inverse(self):
        from math3d_matrix import Matrix3x3
        matrix = Matrix3x3()
        matrix.set_row(0, self.x_axis)
        matrix.set_row(1, self.y_axis)
        matrix.set_row(2, self.z_axis)
        inv_matrix = matrix.calc_inverse()
        inverse = LinearTransform()
        inverse.x_axis = inv_matrix.get_row(0)
        inverse.y_axis = inv_matrix.get_row(1)
        inverse.z_axis = inv_matrix.get_row(2)
        return inverse
    
    def determinant(self):
        return self.x_axis.cross(self.y_axis).dot(self.z_axis)
    
class AffineTransform(Transform):
    def __init__(self, x_axis=None, y_axis=None, z_axis=None, translation=None):
        super().__init__()
        self.linear_transform = LinearTransform(x_axis, y_axis, z_axis)
        self.translation = translation.clone() if translation is not None else Vector(0.0, 0.0, 0.0)
    
    def clone(self):
        return AffineTransform(self.linear_transform.x_axis, self.linear_transform.y_axis, self.linear_transform.z_axis, self.translation)
    
    def to_dict(self):
        data = {
            'linear_transform': self.linear_transform.to_dict(),
            'translation': self.translation.to_dict()
        }
        return data
    
    def from_dict(self, data):
        self.linear_transform = LinearTransform().from_dict(data.get('linear_transform'))
        self.translation = Vector().from_dict(data.get('translation'))
        return self
    
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
    
    def make_rigid_body_motion(self, unit_axis, angle, translation=None):
        self.linear_transform.make_rotation(unit_axis, angle)
        self.translation = translation.clone() if translation is not None else Vector(0.0, 0.0, 0.0)
        return self
    
    def make_translation(self, translation):
        self.linear_transform.make_identity()
        self.translation = translation.clone()
        return self

    def make_rotation(self, axis, angle, center=None):
        if center is None:
            center = Vector(0.0, 0.0, 0.0)
        self.linear_transform.make_rotation(axis, angle)
        self.translation = self.linear_transform(-center) + center
        return self

    def calc_inverse(self):
        inverse = AffineTransform()
        inverse.linear_transform = self.linear_transform.make_inverse()
        inverse.translation = inverse.linear_transform(-self.translation)
        return inverse