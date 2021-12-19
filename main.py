import sys
import os
import pathlib
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *  


from dicom_reader import DICOMReader
from stl_viewer import STLViewer

CUR_DIR = str(pathlib.Path(__file__).parent.resolve())


class Controllers(QtWidgets.QMainWindow):
    def __init__(self):
        super(Controllers, self).__init__()
        uic.loadUi(CUR_DIR + '/form.ui', self)
        self.show()
        
        self.setWindowIcon(QIcon(CUR_DIR + '/ico/icon3.png'))

        self.dicom_reader = DICOMReader()

        self.setUp()
        self.detectSignals()

    def setUp(self):
        fileLink = "D:/Workplace/GameMaking/DICOM_images/650458-/56519872.dcm"
        self.lne_import.setText(fileLink)
        self.tabWidget.setCurrentIndex(0)
        self.lne_red.setText('0.75')
        self.lne_green.setText('0.75')
        self.lne_blue.setText('0.75')
        self.lne_theshold.setText('150')

        self.hsd_red.setMinimum(0)
        self.hsd_red.setMaximum(100)
        self.hsd_red.setValue(75)
        self.hsd_green.setMinimum(0)
        self.hsd_green.setMaximum(100)
        self.hsd_green.setValue(75)
        self.hsd_blue.setMinimum(0)
        self.hsd_blue.setMaximum(100)
        self.hsd_blue.setValue(75)

        self.dicom_reader.set_absolute_path(CUR_DIR)
        self.dicom_reader.set_version(0)

        red_image = QImage(self.lbl_red.width(), self.lbl_red.height(), QImage.Format_RGB32)
        red_image.fill(QColor(255, 0, 0))
        self.display_image(red_image, self.lbl_red)

        green_image = QImage(self.lbl_green.width(), self.lbl_green.height(), QImage.Format_RGB32)
        green_image.fill(QColor(0, 255, 0))
        self.display_image(green_image, self.lbl_green)
        
        blue_image = QImage(self.lbl_blue.width(), self.lbl_blue.height(), QImage.Format_RGB32)
        blue_image.fill(QColor(0, 0, 255))
        self.display_image(blue_image, self.lbl_blue)
        
        color_image = QImage(self.lbl_color.width(), self.lbl_color.height(), QImage.Format_RGB32)
        color_image.fill(QColor(
                            int(float(self.lne_red.text()) * 255),  
                            int(float(self.lne_green.text()) * 255), 
                            int(float(self.lne_blue.text()) * 255)
            ))
        self.display_image(color_image, self.lbl_color)

        self.setAcceptDrops(True)
        self.stl_viewer = STLViewer(distance=1000, size=(2000, 2000, None), spacing=(50, 50, None))
        self.stl_display.setLayout(self.stl_viewer.getLayout())

    def dragEnterEvent(self, e):
        print("enter")
        mimeData = e.mimeData()
        mimeList = mimeData.formats()
        filename = None
        
        if "text/uri-list" in mimeList:
            filename = mimeData.data("text/uri-list")
            filename = str(filename, encoding="utf-8")
            filename = filename.replace("file:///", "").replace("\r\n", "").replace("%20", " ")
            filename = Path(filename)
            
        if filename.exists() and filename.suffix == ".stl":
            e.accept()
            self.droppedFilename = filename
        else:
            e.ignore()
            self.droppedFilename = None
        
    def dropEvent(self, e):
        if self.droppedFilename:
            self.stl_viewer.show(filename=self.droppedFilename)
    
    def detectSignals(self):
        self.btn_import.clicked.connect(self.btn_import_was_clicked)
        self.btn_buildModel.clicked.connect(self.btn_buildModel_was_clicked)
        self.btn_display.clicked.connect(self.btn_display_was_clicked)
        self.hsd_red.valueChanged.connect(self.hsd_red_value_was_changed)
        self.hsd_green.valueChanged.connect(self.hsd_green_value_was_changed)
        self.hsd_blue.valueChanged.connect(self.hsd_blue_value_was_changed)
        self.btn_get_images.clicked.connect(self.btn_get_images_was_clicked)
        self.hsd_1.valueChanged.connect(self.hsd_1_value_was_changed)
        self.hsd_2.valueChanged.connect(self.hsd_2_value_was_changed)
        self.hsd_3.valueChanged.connect(self.hsd_3_value_was_changed)
        self.spb_version.valueChanged.connect(self.spb_version_was_changed)

    def display_image(self, image=None, label=None, scale=True):
        qPixmap = QPixmap.fromImage(image)

        if scale:
            qPixmap = qPixmap.scaled(label.width(), label.height(), aspectRatioMode = Qt.IgnoreAspectRatio)

        label.setPixmap(qPixmap)

    def hsd_1_value_was_changed(self):
        self.lne_1.setText(str(self.hsd_1.value()))
        image = self.dicom_reader.get_image_at(self.hsd_1.value(), PLANE = 'TRANSVERSE')
        self.display_image(image, self.lbl_1, scale=True)

    def hsd_2_value_was_changed(self):
        self.lne_2.setText(str(self.hsd_2.value()))
        image = self.dicom_reader.get_image_at(self.hsd_2.value(), PLANE = 'SAGITTAL')
        self.display_image(image, self.lbl_2, scale=True)

    def hsd_3_value_was_changed(self):
        self.lne_3.setText(str(self.hsd_3.value()))
        image = self.dicom_reader.get_image_at(self.hsd_3.value(), PLANE = 'FRONTAL')
        self.display_image(image, self.lbl_3, scale=True)

    def hsd_red_value_was_changed(self):
        self.lne_red.setText(str(self.hsd_red.value()/100))
        
        color_image = QImage(self.lbl_color.width(), self.lbl_color.height(), QImage.Format_RGB32)
        color_image.fill(QColor(
                            int(float(self.lne_red.text()) * 255),  
                            int(float(self.lne_green.text()) * 255), 
                            int(float(self.lne_blue.text()) * 255)
            ))
        self.display_image(color_image, self.lbl_color, 'QT')

    def hsd_green_value_was_changed(self):
        self.lne_green.setText(str(self.hsd_green.value()/100))
        
        color_image = QImage(self.lbl_color.width(), self.lbl_color.height(), QImage.Format_RGB32)
        color_image.fill(QColor(
                            int(float(self.lne_red.text()) * 255),  
                            int(float(self.lne_green.text()) * 255), 
                            int(float(self.lne_blue.text()) * 255)
            ))
        self.display_image(color_image, self.lbl_color, 'QT')

    def hsd_blue_value_was_changed(self):
        self.lne_blue.setText(str(self.hsd_blue.value()/100))
        
        color_image = QImage(self.lbl_color.width(), self.lbl_color.height(), QImage.Format_RGB32)
        color_image.fill(QColor(
                            int(float(self.lne_red.text()) * 255),  
                            int(float(self.lne_green.text()) * 255), 
                            int(float(self.lne_blue.text()) * 255)
            ))
        self.display_image(color_image, self.lbl_color, 'QT')

    def btn_get_images_was_clicked(self):
        self.dicom_reader.import_dicom(self.lne_import.text(), read=self.ckb_readImages.isChecked(), save=self.ckb_save.isChecked())

        if self.ckb_save.isChecked():
            file_path = "{}/{}_{}.npy".format(CUR_DIR, "images", self.spb_version.value())
            if self.ckb_readImages.isChecked():
                file_path = 'reading' + file_path
            self.plt_images_path.setPlainText(file_path)

        #self.display_image(self.dicom_reader.get_image_at(0), self.lbl_sampleImg)
        self.display_image(self.dicom_reader.get_image_at(0), self.lbl_sampleImg, scale=True)
        self.display_image(self.dicom_reader.get_image_at(0, PLANE = 'TRANSVERSE'), self.lbl_1, scale=True)
        self.display_image(self.dicom_reader.get_image_at(0, PLANE = 'SAGITTAL'), self.lbl_2, scale=True)
        self.display_image(self.dicom_reader.get_image_at(0, PLANE = 'FRONTAL'), self.lbl_3, scale=True)

        self.hsd_1.setMinimum(0)
        self.hsd_1.setMaximum(self.dicom_reader.get_dicom_num() - 1)
        self.hsd_2.setMinimum(0)
        self.hsd_2.setMaximum(self.dicom_reader.get_dicom_width() - 1)
        self.hsd_3.setMinimum(0)
        self.hsd_3.setMaximum(self.dicom_reader.get_dicom_height() - 1)

        self.lne_firstSlice.setText(str('0'))
        self.lne_lastSlice.setText( str(    self.dicom_reader.get_dicom_num() - 1 )    )

        self.display_image(self.dicom_reader.get_hist(), self.lbl_histogram, scale=True)

    def btn_import_was_clicked(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(None, "Open File",
                                                    os.getcwd(),
                                                    "All files (*.*)");
        self.lne_import.setText(fileName[0])

    def spb_version_was_changed(self):
        self.dicom_reader.set_version(self.spb_version.value())

    def get_color(self):
        self.color_val = []
        red_color_val = float(self.lne_red.text())
        green_color_val = float(self.lne_green.text())
        blue_color_val = float(self.lne_blue.text())
        self.color_val.extend((red_color_val, green_color_val, blue_color_val))
        return self.color_val

    def btn_buildModel_was_clicked(self):
        if not self.ckb_readVertex.isChecked():
            self.dicom_reader.setLimit(int(self.lne_firstSlice.text()), int(self.lne_lastSlice.text()))
        self.dicom_reader.do_marching_cubes(int(self.lne_theshold.text()), read=self.ckb_readVertex.isChecked(), save=self.ckb_save.isChecked())

        if self.ckb_save.isChecked():
            file_path = "{}/{}_{}.npy".format(CUR_DIR, "indices", self.spb_version.value())
            self.plt_indices_path.setPlainText(file_path)

            file_path = "{}/{}_{}.npy".format(CUR_DIR, "vertices", self.spb_version.value())
            self.plt_vertices_path.setPlainText(file_path)

        self.indices = self.dicom_reader.get_indices()
        self.vertices = self.dicom_reader.get_vertices()


    def btn_display_was_clicked(self):
        self.stl_viewer.show(vertices = self.vertices, indices = self.indices\
            , edgeColor = ( float(self.lne_red.text()), 
                            float(self.lne_green.text()), 
                            float(self.lne_blue.text())
                        )
            , MODE = 'vertex')


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Controllers()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()