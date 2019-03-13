# math3d_matrix.py

import copy

from math3d_vector import Vector

class Matrix3x3(object):
    def __init__(self, other=None):
        if other is None:
            self.make_identity()
        elif isinstance(other, Matrix3x3):
            self.elements = copy.deepcopy(other.elements)
            
    def clone(self):
        return Matrix3x3(self)
    
    def make_identity(self):
        self.elements = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
    
    def get_row(self, i):
        return Vector(self.elements[i][0], self.elements[i][1], self.elements[i][2])
    
    def set_row(self, i, vector):
        self.elements[i][0] = vector.x
        self.elements[i][1] = vector.y
        self.elements[i][2] = vector.z
    
    def get_col(self, j):
        return Vector(self.elements[0][j], self.elements[1][j], self.elements[2][j])
    
    def set_col(self, j, vector):
        self.elements[0][j] = vector.x
        self.elements[1][j] = vector.y
        self.elements[2][j] = vector.z
    
    def calc_inverse(self):
        adjoint = self.calc_adjoint()
        det = self.calc_determinant()
        try:
            inverse = adjoint / det
            return inverse
        except ZeroDivisionError:
            return None
    
    def calc_determinant(self):
        det = 0.0
        for i in range(3):
            det += self.elements[0][i] * self.calc_cofactor(0, i)
        return det
    
    def calc_adjoint(self):
        return self.calc_cofactor_matrix().make_transpose()
        
    def calc_cofactor_matrix(self):
        cofactor_matrix = Matrix3x3()
        for i in range(3):
            for j in range(3):
                cofactor_matrix.elements[i][j] = self.calc_cofactor(i, j)
        return cofactor_matrix
    
    def calc_cofactor(self, i, j):
        element_list = []
        for row in range(3):
            for col in range(3):
                if row != i and col != j:
                    element_list.append(self.elements[row][col])
        det = element_list[0] * element_list[3] - element_list[1] * element_list[2]
        if (i + j) % 2 == 1:
            det *= -1.0
        return det

    def make_transpose(self):
        tranpose = Matrix3x3()
        for i in range(3):
            for j in range(3):
                tranpose.elements[i][j] = self.elements[j][i]
        return tranpose
    
    def __truediv__(self, other):
        if isinstance(other, float):
            result = Matrix3x3()
            for i in range(3):
                for j in range(3):
                    result.elements[i][j] = self.elements[i][j] / other
        if isinstance(other, Matrix3x3):
            inverse = other.calc_inverse()
            result = self * inverse
        return result
    
    def __mul__(self, other):
        result = None
        if isinstance(other, float):
            result = Matrix3x3()
            for i in range(3):
                for j in range(3):
                    result.elements[i][j] = self.elements[i][j] * other
        elif isinstance(other, Matrix3x3):
            result = Matrix3x3()
            for i in range(3):
                for j in range(3):
                    result.elements[i][j] = self.get_row(i).dot(other.get_col(j))
        elif isinstance(other, Vector):
            result = Vector()
            result.x = self.get_row(0).dot(other)
            result.y = self.get_row(1).dot(other)
            result.z = self.get_row(2).dot(other)
        return result

    def __rmul__(self, other):
        result = None
        if isinstance(other, Vector):
            result = Vector()
            result.x = other.dot(self.get_col(0))
            result.y = other.dot(self.get_col(1))
            result.z = other.dot(self.get_col(2))
        elif isinstance(other, float):
            result = self * other
        return result
    
    def __add__(self, other):
        result = None
        if isinstance(other, Matrix3x3):
            result = Matrix3x3()
            for i in range(3):
                for j in range(3):
                    result.elements[i][j] = self.elements[i][j] + other.elements[i][j]
        return result
    
    def __sub__(self, other):
        result = None
        if isinstance(other, Matrix3x3):
            result = Matrix3x3()
            for i in range(3):
                for j in range(3):
                    result.elements[i][j] = self.elements[i][j] - other.elements[i][j]
        return result
    
    def calc_bestfit_orientation(self):
        pass # TODO: Use singular-value decomposition to find the orthogonal matrix that best fits this matrix.
    
    def calc_singular_value_decomposition(self):
        pass
    
    def calc_eigen_value_decomposition(self):
        pass
    
    def calc_graham_schmidt_decomposition(self):
        pass

    def __str__(self):
        matrix_str = ''
        for i in range(3):
            row = self.get_row(i)
            matrix_str += '[%f %f %f]\n' % (row.x, row.y, row.z)
        return matrix_str

if __name__ == '__main__':
    matrix = Matrix3x3()
    matrix.elements[0][0] = 3.0
    matrix.elements[0][1] = 0.0
    matrix.elements[0][2] = 2.0
    matrix.elements[1][0] = 2.0
    matrix.elements[1][1] = 0.0
    matrix.elements[1][2] = -2.0
    matrix.elements[2][0] = 0.0
    matrix.elements[2][1] = 1.0
    matrix.elements[2][2] = 1.0
    print(matrix)
    inv_matrix = matrix.calc_inverse()
    print(inv_matrix)
    product = matrix * inv_matrix
    print(product)