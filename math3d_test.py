# math3d_test.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from math3d_triangle_mesh import TriangleMesh, Polyhedron

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tri_mesh = TriangleMesh().make_polyhedron(Polyhedron.TETRAHEDRON)

    def initializeGL(self):
        glShadeModel(GL_FLAT)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        aspect_ratio = float(width) / float(height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, aspect_ratio, 0.1, 1000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, -10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
        glColor3f(1.0, 0.0, 0.0)
        self.tri_mesh.render()

        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            self.update()

def ExceptionHook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = ExceptionHook

    app = QtGui.QGuiApplication(sys.argv)

    win = Window()
    win.resize(640, 480)
    win.show()

    sys.exit(app.exec_())