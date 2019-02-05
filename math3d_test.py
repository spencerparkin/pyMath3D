# math3d_test.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from math3d_triangle_mesh import TriangleMesh, Polyhedron
from math3d_triangle import Triangle
from math3d_vector import Vector

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tri_mesh = TriangleMesh().make_polyhedron(Polyhedron.ICOSIDODECAHEDRON)
        
        self.orient = Vector(0.0, 0.0, 0.0)
        self.dragging_mouse = False
        self.drag_pos = None
        self.zoom = 5.0

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glShadeModel(GL_SMOOTH)
                     
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.7, 0.7, 0.7, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        aspect_ratio = float(width) / float(height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(80.0, aspect_ratio, 0.1, 1000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
        glPushMatrix()
        glRotatef(self.orient.x, 1.0, 0.0, 0.0)
        glRotatef(self.orient.y, 0.0, 1.0, 0.0)
        glRotatef(self.orient.z, 0.0, 0.0, 1.0)

        glEnable(GL_LIGHTING)
        
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.0, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, [50.0])
        
        self.tri_mesh.render()
        
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 1.0, 0.0)
        
        self.tri_mesh.render_normals()
        
        glPopMatrix()

        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            self.dragging_mouse = True
            self.drag_pos = event.localPos()
    
    def mouseMoveEvent(self, event):
        if self.dragging_mouse:
            pos = event.localPos()
            delta = pos - self.drag_pos
            self.drag_pos = pos
            sensativity_factor = 2.0
            self.orient.x += sensativity_factor * float(delta.y())
            self.orient.y += sensativity_factor * -float(delta.x())
            self.update()
        
    def mouseReleaseEvent(self, event):
        if self.dragging_mouse:
            self.dragging_mouse = False
            self.drag_pos = None
    
    def wheelEvent(self, event):
        delta = event.angleDelta()
        delta = float(delta.y()) / 120.0
        zoom_factor = 0.5
        self.zoom += delta * zoom_factor
        self.update()

def exceptionHook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = exceptionHook

    app = QtGui.QGuiApplication(sys.argv)

    win = Window()
    win.resize(640, 480)
    win.show()

    sys.exit(app.exec_())