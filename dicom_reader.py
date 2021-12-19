import os
import pydicom as dicom
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure, SubplotParams
from skimage import measure
from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt5.QtGui import QImage

from image_processing import ImageProcessor

# create output directory

class DICOMReader:
    def __init__(self):
        self.version = 0

    def set_absolute_path(self, path):
        self.absolute_path = path

    def set_version(self, version):
        self.version = version
        self.change_clipboard_path()

    def change_clipboard_path(self):
        self.clipboard_path = self.absolute_path

        self.clipboard_path += "/OUTPUT/" + str(self.version)

        try:
            os.makedirs(self.clipboard_path)
        except:
            pass

    def save_npy(self, file, filename):
        np.save("{}/{}_{}.npy".format(self.clipboard_path, filename, self.version), file)

    def read_npy(self, filename):
        file_used = "{}/{}_{}.npy".format(self.clipboard_path, filename, self.version)
        return np.load(file_used)#.astype(np.float64)

    def import_dicom(self, file_path, read=False, save=False):
        if read:
            self.images = self.read_npy("images")
            print('Warning: READING MODE cannot exact dicom header informations')
        else:
            self.load_dicom(file_path)
            if save:
                self.save_npy(self.images, "images")

        self.processed_images = ImageProcessor.process_images(self.images)
        self.limited_processed_images = self.processed_images
        if not read:
            self.save_hist()
        self.xy = self.processed_images
        self.xz = self.xy.transpose(2, 1, 0)
        self.yz = self.xy.transpose(1, 2, 0)

    def load_dicom(self, file_path):
        file_path = '\\'.join(file_path.split('/')[0:-1])
        slices = [dicom.read_file(file_path + '/' + s, force=True) for s in os.listdir(file_path)]
        self.dicom_header = slices[0]
        self.images = np.stack([s.pixel_array for s in slices])

    def get_images(self):
        return self.images

    def get_processed_images(self):
        return self.processed_images

    def get_vertices(self):
        return self.vertices

    def get_indices(self):
        return self.indices
    
    def setLimit(self, lowerLimit, upperLimit):
        self.limited_processed_images =  self.processed_images[lowerLimit:upperLimit]
    
    def do_marching_cubes(self, threshold, read=False, save=False):
        if read:
            self.vertices = self.read_npy('vertices')
            self.indices = self.read_npy('indices')
        else:
            print('making cake')
            self.vertices, self.indices, norm, val = measure.marching_cubes(self.limited_processed_images, threshold, allow_degenerate=True)

        if save:
            self.save_npy(self.vertices, "vertices")
            self.save_npy(self.indices, "indices")

    @staticmethod
    def get_plot_image(image):
        fig = Figure(figsize=(12, 12))
        canvas = FigureCanvas(fig)
        ax = fig.subplots()
        ax.imshow(image, cmap='gray')
        ax.set_axis_off()

        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return im

    def get_image_at(self, index, PLANE = 'TRANSVERSE'):
        mode = 'PIL'
        if mode == 'PIL':
            if PLANE == 'TRANSVERSE':
                image = self.xy[index]
                # return Image.fromarray((self.xy[index] * 255).astype('uint8'), mode='L')
            elif PLANE == 'SAGITTAL':    #xz
                image = self.xz[index]
                # return Image.fromarray((self.xz[index] * 255).astype('uint8'), mode='L')
            elif PLANE == 'FRONTAL':    #yz
                image = self.yz[index]
                # return Image.fromarray((self.yz[index] * 255).astype('uint8'), mode='L')
            image = Image.fromarray(np.uint8(image))
            image = ImageQt(image)
            return image
        else:
            if PLANE == 'TRANSVERSE':
                return self.get_plot_image(self.xy[index])
            elif PLANE == 'SAGITTAL':    #xz
                return self.get_plot_image(self.xz[index])
            elif PLANE == 'FRONTAL':    #yz
                return self.get_plot_image(self.yz[index])

    def get_dicom_header(self):
        return self.dicom_header

    def get_dicom_height(self): #rows num
        return self.images.shape[2]

    def get_dicom_width(self): #column num
        return self.images.shape[1]

    def get_dicom_num(self):
        return self.images.shape[0]

    def save_hist(self):
        plt.hist(self.processed_images.flatten(), bins=50, color='c')
        plt.xlabel("Histogram")
        plt.ylabel("Frequency")
        file_used = "{}/{}_{}".format(self.clipboard_path, "histogram", self.version)
        plt.savefig(file_used)

    def get_hist(self):
        file_used = "{}/{}_{}.png".format(self.clipboard_path, "histogram", self.version)
        image = Image.open(file_used)
        image = ImageQt(image)
        return image


