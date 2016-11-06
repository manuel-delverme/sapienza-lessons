from skimage.data import imread
from skimage.filter import threshold_otsu
import matplotlib.pyplot as plt
import numpy as np
import glob
# %matplotlib inline"
weed_datapath = "/Users/jonegilsson/Data/Drone/shared_annotation_folder/weed_patches_10m_64px"
weed_images = glob.glob(weed_datapath + "/*.png"
crop_datapath = "/Users/jonegilsson/Data/Drone/shared_annotation_folder/wheat_patches_10m_64px"
crop_images = glob.glob(crop_datapath + "/*.png")
