import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from PIL import Image

from sklearn.cluster import KMeans
from skimage import morphology

class ImageProcessor:

    @staticmethod
    def process_images(images):
        processed_images = grayscale(images)

        # masked_lung = []

        # i = 0
        # for img in images:
        #     i += 1
        #     masked_lung.append(make_lungmask(img))

        # processed_images = np.array(masked_lung)

        return processed_images

def grayscale(imgs):
    # Convert pixel_array (img) to -> gray image (img_2d_scaled)
    ## Step 1. Convert to float to avoid overflow or underflow losses.
    imgs_2d = imgs.astype(float)

    ## Step 2. Rescaling grey scale between 0-255
    imgs_2d_scaled = (np.maximum(imgs_2d,0) / imgs_2d.max()) * 255.0

    ## Step 3. Convert to uint
    imgs_2d_scaled = np.uint8(imgs_2d_scaled)

    return imgs_2d_scaled

def show_numpy_image(image, MODE = 'pil'):
    import pprint
    pprint.pprint(image)
    if MODE == 'pil':
        # image = Image.fromarray(np.uint8(image, mode='L')
        image = Image.fromarray((image * 255).astype('uint8'), mode='L')
        image.show()
    else:
        plt.imshow(image, cmap='gray')
        plt.show()


def find_intersection(images, x, y):
    depth = len(images[:,0,0])
    for z in range(depth):
        if images[z, x, y] < 150 and images[z, x, y] > 35 and images[z, x, y] != 1:
            return images[z, x, y]
    return 255

def do_raycast(images):
    depth = len(images[:,0,0])
    width = len(images[0,:,0])
    height = len(images[0,0,:])
    new_image = np.zeros(shape=(width,height))
    print(new_image.shape)
    show_numpy_image(images[200])

    for x in range(width):
        for y in range(height):
            new_image[x][y] = find_intersection(images, x, y)

    print('Finish render')

    show_numpy_image(new_image)

def make_lungmask(img, display=False):
    row_size= img.shape[0]
    col_size = img.shape[1]
    
    mean = np.mean(img)
    std = np.std(img)
    img = img-mean
    img = img/std
    # Find the average pixel value near the lungs
    # to renormalize washed out images
    middle = img[int(col_size/5):int(col_size/5*4),int(row_size/5):int(row_size/5*4)] 
    mean = np.mean(middle)  
    max = np.max(img)
    min = np.min(img)
    # To improve threshold finding, I'm moving the 
    # underflow and overflow on the pixel spectrum
    img[img==max]=mean
    img[img==min]=mean
    #
    # Using Kmeans to separate foreground (soft tissue / bone) and background (lung/air)
    #
    kmeans = KMeans(n_clusters=2).fit(np.reshape(middle,[np.prod(middle.shape),1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    threshold = np.mean(centers)
    thresh_img = np.where(img<threshold,1.0,0.0)  # threshold the image

    # First erode away the finer elements, then dilate to include some of the pixels surrounding the lung.  
    # We don't want to accidentally clip the lung.

    eroded = morphology.erosion(thresh_img,np.ones([3,3]))
    dilation = morphology.dilation(eroded,np.ones([8,8]))

    labels = measure.label(dilation) # Different labels are displayed in different colors
    label_vals = np.unique(labels)
    regions = measure.regionprops(labels)
    good_labels = []
    for prop in regions:
        B = prop.bbox
        if B[2]-B[0]<row_size/10*9 and B[3]-B[1]<col_size/10*9 and B[0]>row_size/5 and B[2]<col_size/5*4:
            good_labels.append(prop.label)
    mask = np.ndarray([row_size,col_size],dtype=np.int8)
    mask[:] = 0

    #
    #  After just the lungs are left, we do another large dilation
    #  in order to fill in and out the lung mask 
    #
    for N in good_labels:
        mask = mask + np.where(labels==N,1,0)
    mask = morphology.dilation(mask,np.ones([10,10])) # one last dilation

    if (display):
        fig, ax = plt.subplots(3, 2, figsize=[12, 12])
        ax[0, 0].set_title("Original")
        ax[0, 0].imshow(img, cmap='gray')
        ax[0, 0].axis('off')
        ax[0, 1].set_title("Threshold")
        ax[0, 1].imshow(thresh_img, cmap='gray')
        ax[0, 1].axis('off')
        ax[1, 0].set_title("After Erosion and Dilation")
        ax[1, 0].imshow(dilation, cmap='gray')
        ax[1, 0].axis('off')
        ax[1, 1].set_title("Color Labels")
        ax[1, 1].imshow(labels)
        ax[1, 1].axis('off')
        ax[2, 0].set_title("Final Mask")
        ax[2, 0].imshow(mask, cmap='gray')
        ax[2, 0].axis('off')
        ax[2, 1].set_title("Apply Mask on Original")
        ax[2, 1].imshow(mask*img, cmap='gray')
        ax[2, 1].axis('off')
        
        plt.show()
    return mask*img

def sample_stack(stack, rows=6, cols=6, start_with=10, show_every=3):
    fig,ax = plt.subplots(rows,cols,figsize=[12,12])
    for i in range(rows*cols):
        ind = start_with + i*show_every
        ax[int(i/rows),int(i % rows)].set_title('slice %d' % ind)
        ax[int(i/rows),int(i % rows)].imshow(stack[ind],cmap='gray')
        ax[int(i/rows),int(i % rows)].axis('off')
    plt.show()