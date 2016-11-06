from skimage.data import imread
from skimage.filter import threshold_otsu
import matplotlib.pyplot as plt
import numpy as np
import glob

# weed_datapath = "/Users/jonegilsson/Data/Drone/shared_annotation_folder/weed_patches_10m_64px"
# weed_images = glob.glob(weed_datapath + "/*.png")
# crop_datapath = "/Users/jonegilsson/Data/Drone/shared_annotation_folder/wheat_patches_10m_64px"
# crop_images = glob.glob(crop_datapath + "/*.png")
def excess_green(image):
    R = image[:,:,0]
    G = image[:,:,1]
    B = image[:,:,2]
    return 2*G - R - B

def plot(img, img2):
    plt.subplot(2,2,1)
    plt.title("Weed")
    plt.axis('off')
    plt.imshow(excess_green(img))
    plt.subplot(2,2,2)
    plt.title("Crop")
    plt.axis('off')
    plt.imshow(excess_green(img2))
    plt.subplot(2,2,3)
    plt.axis('off')

    plt.imshow(img)
    plt.subplot(2,2,4)
    plt.axis('off')
    plt.imshow(img2)

if __name__ == "__main__":
    weed_median_excess_green = [np.median(excess_green(imread(im))) for im in weed_images]
    crop_median_excess_green = [np.median(excess_green(imread(im))) for im in crop_images]
    plt.hist([weed_median_excess_green, crop_median_excess_green], 20, color=['green', 'yellow'], label=['Weed', 'Crop'])
    plt.legend()
    weed_mean_excess_green = [np.mean(excess_green(imread(im))) for im in weed_images]
    crop_mean_excess_green = [np.mean(excess_green(imread(im))) for im in crop_images]
    plt.hist([weed_mean_excess_green, crop_mean_excess_green], 20, color=['green', 'yellow'], label=['Weed', 'Crop'])
    plt.legend()
    threshold = (max(crop_median_excess_green) + min(weed_median_excess_green)) / 2
    thresholdplt.hist([weed_median_excess_green, crop_median_excess_green], 20, color=['green', 'yellow'], label=['Weed', 'Crop'])
    plt.axvline(threshold, color='red', label='Threshold')
    plt.legend()

    weed_median_excess_green = [np.median(excess_green(imread(im))) for im in weed_images]
    crop_training = [np.median(excess_green(imread(im))) for im in crop_images]

    correctly_classified_weed = 0
    for i,weed_validation in enumerate(weed_median_excess_green):
        weed_training = weed_median_excess_green[0:i] + weed_median_excess_green[i+1:]
        threshold = (max(crop_training) + min(weed_training)) / 2.0
        if weed_validation > threshold:
            correctly_classified_weed += 1
        else:
            print "Wrongly classified image: %s (%d)" % (weed_images[i], i)
            
    print "Weed classification ratio: " + str(correctly_classified_weed / float(len(weed_mean_excess_green)))

    weed_training = [np.median(excess_green(imread(im))) for im in weed_images]
    crop_median_excess_green = [np.median(excess_green(imread(im))) for im in crop_images]

    correctly_classified_crop = 0
    for i,crop_validation in enumerate(crop_median_excess_green):
        crop_training = crop_median_excess_green[0:i] + crop_median_excess_green[i+1:]
        threshold = (max(crop_training) + min(weed_training)) / 2.0
        if crop_validation <= threshold:
            correctly_classified_crop += 1
        else:
            print "Wrongly classified image: %s (%d)" % (crop_images[i], i)
            
    print "Crop classification ratio: " + str(correctly_classified_crop / float(len(crop_median_excess_green)))

    weed_miss1 = imread("/Users/jonegilsson/Data/Drone/shared_annotation_folder/weed_patches_10m_64px/12.png")
    weed_miss2 = imread("/Users/jonegilsson/Data/Drone/shared_annotation_folder/weed_patches_10m_64px/36.png")

    plt.subplot(2,3,1)
    plt.title("Weed")
    plt.axis('off')
    plt.imshow(excess_green(weed_miss1))

    plt.subplot(2,3,2)
    plt.title("Weed")
    plt.axis('off')
    plt.imshow(excess_green(weed_miss2))

    plt.subplot(2,3,5)
    plt.axis('off')
    plt.imshow(weed_miss1)

    plt.subplot(2,3,4)
    plt.axis('off')
    plt.imshow(weed_miss2)

    crop_miss = imread("/Users/jonegilsson/Data/Drone/shared_annotation_folder/wheat_patches_10m_64px/13.png")

    plt.subplot(2,3,3)
    plt.title("Crop")
    plt.axis('off')
    plt.imshow(excess_green(crop_miss))

    plt.subplot(2,3,6)
    plt.axis('off')
    plt.imshow(crop_miss)
