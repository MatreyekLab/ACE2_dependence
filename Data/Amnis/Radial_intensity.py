import codecs
import matplotlib.pyplot as plt
import sys
import csv
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import distance
import cv2
from skimage import (color, feature, filters, measure, morphology, segmentation, util)
import os
from skimage import io
io.use_plugin('matplotlib')
from skimage import img_as_ubyte
from skimage import img_as_uint
from skimage.color import rgb2gray
from PIL import Image
Image.LOAD_TRUNCATED_IMAGES = True
import warnings
warnings.filterwarnings("ignore")


## First have to convert all the files into pngs in the Unix Shell
## for f in *_Ch2.ome.tif; do
##     gdal_translate -of png "$f" "${f%.*}_Ch2.ome.png"
## done

## for f in *.ome.tif; do      gdal_translate -of png "$f" "${f%.*}.png" --config CPL_LOG image.log; done

# Set up the path where your chosen image is located
directory = os.getcwd() #str(sys[1])
#os.chdir(directory)

# Ask which folder you want to apply it to (If no folder, enter nothing)
folder = input("Which directory do you want to apply this to? (If current directory, leave blank):")
directory2 = os.path.join(directory, folder)
os.chdir(directory2)

file_list = sorted(os.listdir(directory2))
print(file_list)

# gdal_translate -of png 35_Ch11.ome.tif 35_Ch11.ome.png


total_af488_distance_list = []
total_af488_intensity_list = []
total_mirfp670_distance_list = []
total_mirfp670_intensity_list = []
total_bf_distance_list = []
total_bf_intensity_list = []


for filename in file_list:
	if filename.endswith("Ch2.ome.png"):
		img = Image.open(filename)
		image = img_as_uint(img)
		image_array = np.asarray(image)
		array_height = len(image_array)
		array_width = len(image_array[0])
		center_pixels = [array_height/2,array_height/2-1]
		center_point = [39.5,39.5]
		#print(image_array[39,39]) #This is how we can get the intenxity of a pixel
		#D = distance.euclidean((center_point[0], center_point[1]), (37, 40)) #This is an example of how to calculate the euclidian distance
		af488_distance_list = []
		af488_intensity_list = []

		for x in range(0,array_height):
			for y in range(0,array_width):
				Dtemp = distance.euclidean((center_point[0], center_point[1]), (x, y))
				temp_distance = int(Dtemp)
				#print(temp_distance)
				af488_distance_list.append(temp_distance)
				temp_intensity = image_array[x,y]
				#print(temp_intensity)
				af488_intensity_list.append(temp_intensity)

		#print(intensity_list)
		print(sum(af488_intensity_list))
		norm_af488_intensity_list = af488_intensity_list / sum(af488_intensity_list)
		#print(norm_intensity_list)

		total_af488_distance_list = [*total_af488_distance_list, *af488_distance_list]# str(total_af488_distance_list)+str(af488_distance_list)
		total_af488_intensity_list = [*total_af488_intensity_list, *norm_af488_intensity_list]# str(total_af488_intensity_list)+str(norm_af488_intensity_list)

	if filename.endswith("Ch11.ome.png"):
		img = Image.open(filename)
		image = img_as_uint(img)
		image_array = np.asarray(image)
		array_height = len(image_array)
		array_width = len(image_array[0])
		center_pixels = [array_height/2,array_height/2-1]
		center_point = [39.5,39.5]
		#print(image_array[39,39]) #This is how we can get the intenxity of a pixel
		#D = distance.euclidean((center_point[0], center_point[1]), (37, 40)) #This is an example of how to calculate the euclidian distance
		mirfp670_distance_list = []
		mirfp670_intensity_list = []

		for x in range(0,array_height):
			for y in range(0,array_width):
				Dtemp = distance.euclidean((center_point[0], center_point[1]), (x, y))
				temp_distance = int(Dtemp)
				#print(temp_distance)
				mirfp670_distance_list.append(temp_distance)
				temp_intensity = image_array[x,y]
				#print(temp_intensity)
				mirfp670_intensity_list.append(temp_intensity)

		print(sum(mirfp670_intensity_list))
		norm_mirfp670_intensity_list = mirfp670_intensity_list / sum(mirfp670_intensity_list)
		#print(norm_intensity_list)

		total_mirfp670_distance_list = [*total_mirfp670_distance_list, *mirfp670_distance_list]# str(total_mirfp670_distance_list)+str(mirfp670_distance_list)
		total_mirfp670_intensity_list = [*total_mirfp670_intensity_list, *norm_mirfp670_intensity_list]# str(total_mirfp670_intensity_list)+str(norm_mirfp670_intensity_list)

	if filename.endswith("Ch1.ome.png"):
		img = Image.open(filename)
		image = img_as_uint(img)
		image_array = np.asarray(image)
		array_height = len(image_array)
		array_width = len(image_array[0])
		center_pixels = [array_height/2,array_height/2-1]
		center_point = [39.5,39.5]
		#print(image_array[39,39]) #This is how we can get the intenxity of a pixel
		#D = distance.euclidean((center_point[0], center_point[1]), (37, 40)) #This is an example of how to calculate the euclidian distance
		bf_distance_list = []
		bf_intensity_list = []

		for x in range(0,array_height):
			for y in range(0,array_width):
				Dtemp = distance.euclidean((center_point[0], center_point[1]), (x, y))
				temp_distance = int(Dtemp)
				#print(temp_distance)
				bf_distance_list.append(temp_distance)
				temp_intensity = image_array[x,y]
				#print(temp_intensity)
				bf_intensity_list.append(temp_intensity)

		for w in range(0,len(bf_intensity_list)):
			if bf_intensity_list[w] < 38000:
				bf_intensity_list[w] = 1
			if bf_intensity_list[w] > 41000:
				bf_intensity_list[w] = 1
			else:
				bf_intensity_list[w] = 0

		print(sum(bf_intensity_list))
		norm_bf_intensity_list = bf_intensity_list #/ sum(bf_intensity_list)
		#print(norm_intensity_list)

		total_bf_distance_list = [*total_bf_distance_list, *bf_distance_list]# str(total_bf_distance_list)+str(bf_distance_list)
		total_bf_intensity_list = [*total_bf_intensity_list, *norm_bf_intensity_list]# str(total_bf_intensity_list)+str(norm_bf_intensity_list)

print(len(af488_distance_list))
print(len(norm_af488_intensity_list))
print(len(total_af488_distance_list))
print(len(total_af488_intensity_list))

print(len(mirfp670_distance_list))
print(len(norm_mirfp670_intensity_list))
print(len(total_mirfp670_distance_list))
print(len(total_mirfp670_intensity_list))

print(len(bf_distance_list))
print(len(norm_bf_intensity_list))
print(len(total_bf_distance_list))
print(len(total_bf_intensity_list))

textfile = open("af488_distance_intensity.txt", "w")
textfile.write("distance\tfraction_intensity\n")
for z in range(0,len(total_af488_intensity_list)):
	#print(norm_intensity_list[z])
	textfile.write(str(total_af488_distance_list[z]) + "\t" + str(total_af488_intensity_list[z]) + "\n")
textfile.close()

textfile2 = open("miRFP670_distance_intensity.txt", "w")
textfile2.write("distance\tfraction_intensity\n")
for z in range(0,len(total_mirfp670_intensity_list)):
	#print(norm_intensity_list[z])
	textfile2.write(str(total_mirfp670_distance_list[z]) + "\t" + str(total_mirfp670_intensity_list[z]) + "\n")
textfile2.close()

textfile3 = open("bf_distance_intensity.txt", "w")
textfile3.write("distance\tfraction_intensity\n")
for z in range(0,len(total_bf_intensity_list)):
	#print(norm_intensity_list[z])
	textfile3.write(str(total_bf_distance_list[z]) + "\t" + str(total_bf_intensity_list[z]) + "\n")
textfile3.close()

