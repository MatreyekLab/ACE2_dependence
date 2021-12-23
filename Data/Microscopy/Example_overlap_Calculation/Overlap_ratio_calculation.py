import codecs
import matplotlib.pyplot as plt
import sys
import csv
import numpy as np
from scipy import ndimage as ndi
import cv2
from skimage import (color, feature, filters, measure, morphology, segmentation, util)
import os
from skimage import io
io.use_plugin('matplotlib')
from skimage import img_as_ubyte
from skimage.color import rgb2gray
from PIL import Image
Image.LOAD_TRUNCATED_IMAGES = True
import warnings
warnings.filterwarnings("ignore")

# Set up the path where your chosen image is located
directory = os.getcwd() #str(sys[1])
#os.chdir(directory)

# Ask which folder you want to apply it to (If no folder, enter nothing)
folder = input("Which directory do you want to apply this to? (If current directory, leave blank):")

directory2 = os.path.join(directory, folder)
os.chdir(directory2)

if os.path.exists(os.path.join(directory2, "Merged")) == False:
    os.mkdir(os.path.join(directory2, "Merged"))

outfilename = "Outfile.tsv"
outfile = codecs.open(outfilename, "w", "utf-8", "replace")
outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("file","gfp_pixels","mcherry_pixels","nir_pixels","mcherry_overlap_pixels","nir_overlap_pixels","mcherry_overlap_pct","nir_overlap_pct","nir_mcherry_overlap_ratio"))

file_list = sorted(os.listdir(directory2))
print(file_list)

for filename in file_list:
    if filename.endswith(".tiff"):
        img = Image.open(filename)
        print(filename)
        #frames = [img.seek(0), img.seek(1), img.seek(2)]
        frames = []
        print(img.seek(0))
        for i in range(3):
            img.seek(i)
            frames.append(img.copy())
        # Choose your mCherry cells
        mcherry = img_as_ubyte(frames[0])
        # Choose your gfp
        gfp = img_as_ubyte(frames[1])
        # Choose your nir
        nir = img_as_ubyte(frames[2])
        # https://pythontic.com/numpy/ndarray/subtract
        nir = nir.__sub__((mcherry * 0.1).astype(int)) # https://www.kite.com/python/answers/how-to-convert-a-numpy-array-of-floats-into-integers-in-python

        # https://stackoverflow.com/questions/48406578/adjusting-contrast-of-image-purely-with-numpy
        # Get brightness range - i.e. darkest and lightest pixels
        min_mcherry =np.min(mcherry)        # result=144
        max_mcherry =np.max(mcherry)        # result=216
        # Make a LUT (Look-Up Table) to translate image values
        LUT=np.zeros(256,dtype=np.uint8)
        LUT[min_mcherry:max_mcherry+1]=np.linspace(start=0,stop=255,num=(max_mcherry-min_mcherry)+1,endpoint=True,dtype=np.uint8)
        # Apply LUT and save resulting image
        #Image.fromarray(LUT[mcherry]).save('mcherry.png')
        adjusted_mcherry = Image.fromarray(LUT[mcherry])
        #adjusted_mcherry.save('mcherry.png')

        ## Now for nir
        min_nir =np.min(nir)        # result=144
        max_nir =np.max(nir)        # result=216
        # Make a LUT (Look-Up Table) to translate image values
        LUT=np.zeros(256,dtype=np.uint8)
        LUT[min_nir:max_nir+1]=np.linspace(start=0,stop=255,num=(max_nir-min_nir)+1,endpoint=True,dtype=np.uint8)
        # Apply LUT and save resulting image
        #Image.fromarray(LUT[nir]).save('nir.png')
        adjusted_nir = Image.fromarray(LUT[nir])
        #adjusted_nir.save('nir.png')

        ## Now for gfp
        min_gfp =np.min(gfp)        # result=144
        max_gfp =np.max(gfp)        # result=216
        # Make a LUT (Look-Up Table) to translate image values
        LUT=np.zeros(256,dtype=np.uint8)
        LUT[min_gfp:max_gfp+1]=np.linspace(start=0,stop=255,num=(max_gfp-min_gfp)+1,endpoint=True,dtype=np.uint8)
        # Apply LUT and save resulting image
        #Image.fromarray(LUT[gfp]).save('gfp.png')
        adjusted_gfp = Image.fromarray(LUT[gfp])
        #adjusted_gfp.save('gfp.png')

        rgb_uint8 = (np.dstack((adjusted_mcherry,adjusted_gfp,adjusted_nir))).astype(np.uint8)
        #img_rgb_uint8 = rgb_uint8.convert("RGB")
        #img_rgb_uint8.save("superimposed.png")
        data = Image.fromarray(rgb_uint8)
        data.save("Merged/"+filename[0:8]+'adjusted.png')

        # Setting up the threshold array to identify the cells
        # The class might be modified depending on the cell image, the range is 2 to 4
        mcherry_thresholds = filters.threshold_multiotsu(mcherry, classes=2)
        mcherry_mask = mcherry > mcherry_thresholds[0]
        gfp_thresholds = filters.threshold_multiotsu(gfp, classes=2)
        gfp_mask = gfp > gfp_thresholds[0]
        nir_thresholds = filters.threshold_multiotsu(nir, classes=2)
        nir_mask = nir > nir_thresholds[0]

        gfp_count  = np.count_nonzero(gfp_mask)
        nir_overlap = np.logical_and(gfp_mask, nir_mask) #https://stackoverflow.com/questions/44578571/intersect-two-boolean-arrays-for-true
        nir_overlap_count = np.count_nonzero(nir_overlap) #https://www.kite.com/python/answers/how-to-count-the-number-of-true-elements-in-a-numpy-boolean-array-in-python#:~:text=Use%20numpy.,elements%20in%20a%20boolean%20array%20.
        nir_count = np.count_nonzero(nir_mask)
        nir_overlap_pct = nir_overlap_count / nir_count

        mcherry_overlap = np.logical_and(gfp_mask, mcherry_mask) #https://stackoverflow.com/questions/44578571/intersect-two-boolean-arrays-for-true
        mcherry_overlap_count = np.count_nonzero(mcherry_overlap) #https://www.kite.com/python/answers/how-to-count-the-number-of-true-elements-in-a-numpy-boolean-array-in-python#:~:text=Use%20numpy.,elements%20in%20a%20boolean%20array%20.
        mcherry_count = np.count_nonzero(mcherry_mask)
        mcherry_overlap_pct = mcherry_overlap_count / mcherry_count

        nir_mcherry_overlap_ratio = nir_overlap_pct / mcherry_overlap_pct

        outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(filename,gfp_count,mcherry_count,nir_count,mcherry_overlap_count,nir_overlap_count,mcherry_overlap_pct,nir_overlap_pct,nir_mcherry_overlap_ratio))

        '''
        f, axarr = plt.subplots(2,3)
        axarr[0,0].imshow(gfp_mask, 'gray', interpolation='none')
        axarr[0,0].set_title('GFP')
        axarr[0,1].imshow(nir_mask, 'gray', interpolation='none')
        axarr[0,1].set_title('miRFP670')
        axarr[0,2].imshow(mcherry_mask, 'gray', interpolation='none')
        axarr[0,2].set_title('mCherry')
        axarr[1,0].imshow(gfp_mask, 'gray', interpolation='none')
        axarr[1,0].set_title('GFP')
        axarr[1,1].imshow(nir_overlap, 'gray', interpolation='none')
        axarr[1,1].set_title('miRFP670 & GFP')
        axarr[1,2].imshow(mcherry_overlap, 'gray', interpolation='none')
        axarr[1,2].set_title('mCherry & GFP')
        plt.show()
        '''

outfile.close()
