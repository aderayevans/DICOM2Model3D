from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph.opengl as gl 

from stl import mesh
import numpy as np

from os import environ
from pathlib import Path

environ["QT_DEVICE_PIXEL_RATIO"] = "0"
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
environ["QT_SCREEN_SCALE_FACTORS"] = "1"
environ["QT_SCALE_FACTOR"] = "1"

class STLViewer:
    def __init__(self, distance = 40, size=(200, 200, None), spacing=(50, 50, None)):
        self.layout = QVBoxLayout()
        
        self.viewer = gl.GLViewWidget()
        self.layout.addWidget(self.viewer, 1)
        self.viewer.setCameraPosition(distance = distance)
        
        g = gl.GLGridItem()
        x_size, y_size, z_size = size
        x_spacing, y_spacing, z_spacing = spacing
        
        g.setSize(x_size, y_size, z_size)
        g.setSpacing(x_spacing, y_spacing, z_spacing)
        self.viewer.addItem(g)

        self.currentMesh = None
        self.lastDir = None
        self.droppedFilename = None
        
        btn = QPushButton(text="Load STL")
        btn.clicked.connect(self.showDialog)
        btn.setFont(QFont("Ricty Diminished", 14))
        self.layout.addWidget(btn)
            
    def showDialog(self):
        directory = Path("")
        if self.lastDir:
            directory = self.lastDir
        fname = QFileDialog.getOpenFileName(None, "Open file", str(directory), "STL (*.stl)")
        if fname[0]:
            self.show(fname[0])
            self.lastDir = Path(fname[0]).parent

    def show(self, filename=None, vertices=None, indices=None, edgeColor = (0, 1, 0), MODE = 'stl'):
        print('Show time')
        if self.currentMesh:
            self.viewer.removeItem(self.currentMesh)

        if MODE == 'stl':
            points, faces = self.loadSTL(filename)
        else:
            points = vertices
            faces = indices

        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=True, drawEdges=True, edgeColor=edgeColor + (1,))
        self.viewer.addItem(mesh)
        
        self.currentMesh = mesh
        
    def loadSTL(self, filename):
        m = mesh.Mesh.from_file(filename)
        shape = m.points.shape
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces

    def getLayout(self):
        return self.layout