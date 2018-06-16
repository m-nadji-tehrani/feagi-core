
"""
# This file acts as the Input Processing Unit (IPU) for the system.
# Functions in this file will provide methods to pass raw data through basic filters and feed them to the
# ocipital lobe processing layers such as V1, V2, V4 and IT

# For test purposes only and need to see how it can be eliminated from code for efficiency
"""
import os
import struct
from datetime import datetime
import numpy as np
import sys
import random
sys.path.append('/usr/local/lib/python2.7/site-packages')
# import cv2


from misc import universal_functions
import architect


def read_mnist_raw(dataset="training", path="../MNIST/"):
    """
    Python function for importing the MNIST data set.  It returns an iterator
    of 2-tuples with the first element being the label and the second element
    being a numpy.uint8 2D array of pixel data for the given image.
    """
    if dataset is "training":
        fname_img = os.path.join(path, 'train-images.idx3-ubyte')
        fname_lbl = os.path.join(path, 'train-labels.idx1-ubyte')
    elif dataset is "testing":
        fname_img = os.path.join(path, 't10k-images.idx3-ubyte')
        fname_lbl = os.path.join(path, 't10k-labels.idx1-ubyte')
    else:
        raise Exception(ValueError, "data set must be 'testing' or 'training'")

    # Load everything in some numpy arrays
    with open(fname_lbl, 'rb') as flbl:
        magic, num = struct.unpack(">II", flbl.read(8))
        lbl = np.fromfile(flbl, dtype=np.int8)

    with open(fname_img, 'rb') as fimg:
        magic, num, rows, cols = struct.unpack(">IIII", fimg.read(16))
        img = np.fromfile(fimg, dtype=np.uint8).reshape(len(lbl), rows, cols)

    get_img = lambda idx: (lbl[idx], img[idx])

    # Create an iterator which returns each image in turn
    for i in range(len(lbl)):
        yield get_img(i)


# def read_training_img_from_mnist():
#     image_num = random.randrange(10, 500, 1)
#     training_image = read_image(image_num)
#     return training_image


def mnist_img_fetcher(num):
    # Returns a random image from MNIST matching the requested number
    img_lbl = ''
    print("An image is being fetched from MNIST")
    while img_lbl != int(num):
        img_index = random.randrange(10, len(universal_functions.mnist_array), 1)
        img_lbl, img_data = universal_functions.mnist_array[img_index]
    print("The image for number %s has been fetched." %str(num))
    return img_data, img_lbl


def read_image(index):
    # Reads an image from MNIST matching the index number requested in the function
    tmp = 1
    image_db = universal_functions.mnist_iterator
    for labeledImage in image_db:
        tmp += 1
        if tmp == index:
            # print(i[1])
            img = labeledImage[1]
            label = labeledImage[0]
            return img, label


class Filter:
    def brightness(self, image):
        new_image = np.zeros(image.shape)
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                if image[x, y] >= universal_functions.genome["image_color_intensity_tolerance"]:
                    new_image[x, y] = image[x, y]
                else:
                    new_image[x, y] = 1
        return new_image


def kernel_sizer(kernel_values):
    np.tmp = kernel_values
    kernel_size = np.shape(np.tmp)
    kernel_size = kernel_size[0]
    if divmod(kernel_size, 2)[1] == 0:
        print("Error: Kernel size should only be Odd number!")
        return
    return kernel_size


def convert_image_to_coordinates(image):   # Image is currently assumed to be a 28 x 28 numpy array
    """
    Function responsible for reading an image and converting the pixel values to coordinates
    """
    # Note: currently set to function based on Gray scale image
    genome = universal_functions.genome

    image_locations = []
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if image[x, y] >= genome["image_color_intensity_tolerance"]:
                image_locations.append([x, y, 0])

    # Image location will be fed to another function to identify the Id of neurons to be activated
    return image_locations


def convert_direction_matrix_to_coordinates(image):
    # print("Polarized image type = ", type(image))
    image_locations = []
    x = 0
    y = 0
    for row in image:
        for column in row:
            if image[x][y] != '':
                image_locations.append([x, y, 0])
            y += 1
        y = 0
        x += 1
    return image_locations


def convert_image_locations_to_neuron_ids(image_locations, cortical_area):
    """
    Queries the connectome for each location and provides the list of Neuron Ids matching the location
    :param image_locations:
    :return:
    """
    genome = universal_functions.genome

    neuron_id_list = []
    for x in range(len(image_locations)):
            # call the function to find neuron candidates for a given location
            tmp = architect.neuron_finder(cortical_area, image_locations[x], genome["location_tolerance"])
            for item in tmp:
                if (item is not None) and (neuron_id_list.count(item) == 0):
                    neuron_id_list.append(item)

    return neuron_id_list


def image_read_by_block(image, kernel_size, seed_coordinates):
    x = seed_coordinates[0]
    y = seed_coordinates[1]
    if divmod(kernel_size, 2)[1] == 0:
        print("Error: Kernel size should only be Odd number!")
        return
    kernel_values = np.zeros((kernel_size, kernel_size))
    scan_length = divmod(kernel_size, 2)[0]
    for a in range(0, kernel_size):
        for b in range(0, kernel_size):
            if ((x-scan_length+a >= 0) and (y-scan_length+b >= 0) and (x-scan_length+a < np.shape(image)[0])
                    and (y-scan_length+b < np.shape(image)[1])):
                kernel_values[a, b] = image[x-scan_length+a, y-scan_length+b]
    return kernel_values


def kernel_direction(kernel_values):
    """
    Apply all filters from the IPU_vision_filters to the kernel and evaluate the best match
    Output is the Type of directional cell which will be activated 
    :param kernel_size: 
    :param kernel_values: 
    :return: 
    
    The following conditions will estimate the line orientation angle into 4 standard options as following:
    1: /        2: \        3: -       4: |       0 : none
    Each if condition will perform a simple statistical analysis on the concentration of the pixels
    """
    # todo: Important >>> Something is wrong with this function returning incorrect values as direction label changes

    end_result = {}
    kernel_size = kernel_sizer(kernel_values)
    for filter_entry in universal_functions.genome["IPU_vision_filters"][str(kernel_size)]:
        end_result[filter_entry] = apply_direction_filter(kernel_values, kernel_size, filter_entry)

    tmpArray = []
    # print('this is tmp before all appends', tmpArray)
    for entry in end_result:
        sumation = np.sum(end_result[entry])
        # print("Appending: %s Sum: %d \n End_result: \n %s" % (entry, summation,end_result[entry]))
        # tmp = np.append(tmp, [entry, np.sum(end_result[entry])], axis=0)
        tmpArray.append([entry, np.sum(end_result[entry])])
        # print('***', tmpArray)
    # print("This is the end result: \n %s" % end_result)
    # print('tmp after appends %s' % tmpArray)
    maxValue = max(list(zip(*tmpArray))[1])
    maxValueIndex = list(zip(*tmpArray))[1].index(maxValue)
    direction = tmpArray[maxValueIndex][0]
    # direction = direction.replace('\\', '\')
    # print('max value is %s' % maxValue)
    # print('max index is %s' % maxValueIndex)
    # print('direction is %s' % direction)
    return direction


def apply_direction_filter(kernel_values, kernel_size, direction_key):
    """Function to apply a particular filter to a kernel region of any size"""
    # end_result = {}
    result = np.zeros((kernel_size, kernel_size))
    filter_value = universal_functions.genome["IPU_vision_filters"][str(kernel_size)][direction_key]
    for i in range(0, kernel_size):
        for ii in range(0, kernel_size):
            result[i][ii] = kernel_values[i][ii] * filter_value[i][ii]
            ii += 1
        i += 1
    # end_result[direction_key] = result

    return result


def create_direction_matrix(image, kernel_size, direction_sensitivity=''):
    """
    Generates a Matrix where each element outlines the direction detected by the Kernel filters against each
    corresponding pixel in the image. 
    :param image: 
    :param kernel_size: 
    :return: 
    """
    if divmod(kernel_size, 2)[1] == 0:
        print("Error: Kernel size should only be Odd number!")
        return
    row_index = 0
    col_index = 0
    direction_matrix = [[] for x in range(np.shape(image)[1])]
    for row in image:
        for row_item in row:
            direction = kernel_direction(image_read_by_block(image, kernel_size, [row_index, col_index]))
            if direction == direction_sensitivity or direction_sensitivity == '':
                direction_matrix[row_index].append(direction)
            else:
                direction_matrix[row_index].append('')
            col_index += 1
        col_index = 0
        row_index += 1
    return direction_matrix


# todo: Need to add a method to combine multiple IPU layer data into a single one
#        -Think how to build a direction agnostic representation of an object
        

def kernel_edge_detector(kernel_values):


    return


def image_processing():
    """
    Function to read an image from a file and have it converted to it's fundamental components
    """
    return


def image_orientation_detector():
    """
    Performs higher level analysis to detect the direction of an image
    """
    # todo: need to figure which processing layer this belongs to. It might need to go thru entire stack
    return


def orientation_matrix(raw_image, orientation_key, kernel_size):
    """
    Function to produce an orientation matrix based on the raw image data
    """

    return


def direction_stats(image_block):
    """
    Reads direction Kernel data and returns statistics on the percentage of each direction
    :param kernel: 
    :return: 
    """
    # direction_matrix = (image, kernel_size))
    # print(image)

    direction_matrix = ''
    for row in image_block:
        for item in row:
            direction_matrix = direction_matrix + str(item)

    # generate a list of all unique Characters present in the image block
    unique_chars = []
    for item in direction_matrix:
        if unique_chars.count(item) == 0 and item != ' ':
            unique_chars.append(item)
    # print('list of unique chars = %s' % unique_chars)

    # Count number of occurrences of each unique character
    counts = []
    for item in unique_chars:
        counts.append([item, direction_matrix.count(item)])

    # Calculate the percentage of usage of each word
    stats = []
    count_total = direction_matrix.__len__() - direction_matrix.count(' ')
    for key in range(0, counts.__len__()):
        stats.append([counts[key][0], str(counts[key][1] * 100 / float(count_total)) + ' %'])

    return stats




# settings.init()
#
#
# print(kernel_direction([
#   [ .1,  .1,  .1]
#  ,[ .1,  .1,  .1]
#  ,[ .1,  .1,  .1]]))
# print(kernel_direction([
#   [ 1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1]]))
# print(kernel_direction([
#   [ 10,  1,  1,  1,  1,  1,  1]
#  ,[ 1,  10,  1,  1,  1,  1,  1]
#  ,[ 1,  1,  10,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  10,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  10,  1,  1]
#  ,[ 1,  1,  1,  1,  1,  10,  1]
#  ,[ 1,  1,  1,  1,  1,  1,  10]]))

#
# print(direction_stats(kernel_direction([
#   [ 1,  1,  1]
#  ,[ 1,  10,  1]
#  ,[ 1,  1,  1]])))


# print(apply_direction_filter([
#   [ 1,  10,  1]
#  ,[ 1,  10,  1]
#  ,[ 1,  10,  1]], '\\'))
#
# print(kernel_sizer([
#   [ 1,  1,  1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1,  1,  1]
#  ,[ 1,  1,  1,  1,  1,  1,  1]]))