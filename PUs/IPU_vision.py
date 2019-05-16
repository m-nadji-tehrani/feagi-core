
import sys
sys.path.append('/Users/mntehrani/PycharmProjects/Metis/venv/lib/python3.7/site-packages/')
import os
import struct
import numpy as np
import random
from math import floor
from scipy.misc import imresize
from evolutionary import architect
from configuration import runtime_data
from datetime import datetime
# from cython_libs import ipu_vision_cy as ipu_cy
np.set_printoptions(threshold=np.nan)

"""
# This file acts as the Input Processing Unit (IPU) for the system.
# Functions in this file will provide methods to pass raw data through basic filters and feed them to the
# Ocipital lobe processing layers such as V1, V2, V4 and IT

# For test purposes only and need to see how it can be eliminated from code for efficiency
"""


if __name__ == '__main__':

    from misc import disk_ops
    disk_ops.load_parameters_in_memory()
    from configuration import runtime_data

    disk_ops.genome_handler("/Users/mntehrani/PycharmProjects/Metis/connectome/")


class MNIST:
    def __init__(self):
        # global mnist_array, mnist_iterator
        self.mnist_training_iterator = self.read_mnist_raw(dataset="training")
        self.mnist_test_iterator = self.read_mnist_raw(dataset="testing")
        self.mnist_training_array = []
        self.mnist_test_array = []
        for _ in self.mnist_training_iterator:
            self.mnist_training_array.append(_)
        for __ in self.mnist_test_iterator:
            self.mnist_test_array.append(__)
        print(">><<>><<>><<>><< **  **  **  **   **  **  **  ****  >><<>><<>><<>><<>><<")
        # print(len(mnist_array))

    @staticmethod
    def read_mnist_raw(dataset="training", database=runtime_data.parameters["InitData"]["image_database"]):
        """
        Python function for importing the MNIST data set.  It returns an iterator
        of 2-tuples with the first element being the label and the second element
        being a numpy.uint8 2D array of pixel data for the given image.
        """

        path = "../" + database + "/"
        absolute_path = "/Users/mntehrani/PycharmProjects/" + database + "/"

        if dataset is "training":
            fname_img = os.path.join(path, 'train-images.idx3-ubyte')
            fname_lbl = os.path.join(path, 'train-labels.idx1-ubyte')
            # fname_img = 'train-images.idx3-ubyte'
            # fname_lbl = 'train-labels.idx1-ubyte'

        elif dataset is "testing":
            fname_img = os.path.join(path, 't10k-images.idx3-ubyte')
            fname_lbl = os.path.join(path, 't10k-labels.idx1-ubyte')
        else:
            raise Exception(ValueError, "data set must be 'testing' or 'training'")

        # Load everything in some numpy arrays
        with open(absolute_path + fname_lbl, 'rb') as flbl:
            magic, num = struct.unpack(">II", flbl.read(8))
            lbl = np.fromfile(flbl, dtype=np.int8)

        with open(absolute_path + fname_img, 'rb') as fimg:
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

    # def mnist_img_fetcher(self, num):
    #     # Returns a random image from the entire MNIST matching the requested number
    #     # global mnist_array
    #     img_lbl = ''
    #     # print("An image is being fetched from MNIST")
    #     if runtime_data.parameters["Switches"]["ipu_vision_dynamic_img_fetch"]:
    #         while img_lbl != int(num):
    #             img_index = random.randrange(10, len(self.mnist_array), 1)
    #             img_lbl, img_data = self.mnist_array[img_index]
    #         print('>>> MNIST img id >>>', img_index)
    #         if runtime_data.parameters["Logs"]["print_mnist_img_info"]:
    #             print("The image for number %s has been fetched." %str(num))
    #         return img_data, img_lbl
    #     else:
    #
    #         if runtime_data.parameters["Switches"]["MNIST_set_option"] == 1:
    #                     hand_picked_list = [33485, 37518, 55170, 30273, 58049, 40258, 45668, 20162, 28940, 35002]
    #
    #         elif runtime_data.parameters["Switches"]["MNIST_set_option"] == 2:
    #                     hand_picked_list = [33485, 37518, 55170, 30273, 58049, 40258, 45668, 20162, 28940, 35002,
    #                                         18896, 46916, 9054, 37745, 21653, 21883, 27934, 7446, 35120, 11015]
    #
    #         elif runtime_data.parameters["Switches"]["MNIST_set_option"] == 3:
    #                     hand_picked_list = range(100, 200)
    #
    #         while img_lbl != int(num):
    #             selected_img = hand_picked_list[random.randrange(len(hand_picked_list))]
    #             img_lbl, img_data = self.mnist_array[selected_img]
    #         if runtime_data.parameters["Logs"]["print_mnist_img_info"]:
    #             print("The image for number %s has been fetched." % str(num))
    #         return img_data, img_lbl

    def mnist_img_fetcher2(self, num, seq, mnist_type):
        """
        returns the nth digit within MNIST that equals the desirable number
        """
        img_lbl = ''
        img_data_ = ''
        seq_counter = 0
        mnist_counter = 1
        while not (img_lbl == int(num) and seq_counter == seq):
            if mnist_type == 'training':
                img_lbl, img_data_ = self.mnist_training_array[mnist_counter]
                # print("img_lbl=", img_lbl)
                # print("mnist_counter=", mnist_counter)
                # print("seq_counter=", seq_counter)
            elif mnist_type == 'test':
                img_lbl, img_data_ = self.mnist_test_array[mnist_counter]
                # print("%%%:", img_lbl, img_data_)
            else:
                print("ERROR: Invalid data type selected for MNIST")
            if img_lbl == int(num):
                seq_counter += 1
                # print("$->>-->>", counter, "$->>-->>", seq)
            mnist_counter += 1
        return img_data_, img_lbl

    def read_image(self, index):
        # Reads an image from MNIST matching the index number requested in the function
        # global mnist_iterator
        tmp = 1
        image_db = self.mnist_iterator
        for labeledImage in image_db:
            tmp += 1
            if tmp == index:
                # print(i[1])
                img = labeledImage[1]
                label = labeledImage[0]
                return img, label


class Filter:
    @staticmethod
    def brightness(image):
        new_image = np.zeros(image.shape)
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                if image[x, y] >= runtime_data.genome["image_color_intensity_tolerance"]:
                    new_image[x, y] = image[x, y]
                else:
                    new_image[x, y] = 1
        return new_image

    @staticmethod
    def contrast(image, kernel_size):
        """This function simulates the effect of Amacrine and Horizontal cells within human Retina"""
        if divmod(kernel_size, 2)[1] == 0:
            print("Error: Kernel size should only be Odd number!")
            return
        row_index = 0
        col_index = 0
        new_image = [[] for x in range(np.shape(image)[1])]
        for row in image:
            for row_item in row:
                kernel_values = Image.image_read_by_block(image, kernel_size, [row_index, col_index])
                cell_value = Kernel.kernel_contrast(kernel_values=kernel_values, kernel_size=kernel_size)
                new_image[row_index].append(cell_value)
                col_index += 1
            col_index = 0
            row_index += 1
        new_image = np.asarray(new_image, dtype=np.int)

        # print("Pre-normalized image:\n", new_image)

        # Normalize pixel values
        image_max_value = np.amax(new_image)
        # print("Max value:", image_max_value)
        row_index = 0
        col_index = 0
        normalized_image = [[] for x in range(np.shape(new_image)[1])]
        for row in new_image:
            for row_item in row:
                # 255 is the max intensity value that each image cell can be
                normalized_value = floor(row_item * 255 / image_max_value)
                normalized_image[row_index].append(normalized_value)
                col_index += 1
            col_index = 0
            row_index += 1
        # print("NNN\n", normalized_image)
        # normalized_image = np.asarray(normalized_image, dtype=np.int)
        return normalized_image

    @staticmethod
    def direction(kernel_values, kernel_size, direction_key):
        """Function to apply a particular filter to a kernel region of any size"""
        # end_result = {}
        result = np.zeros((kernel_size, kernel_size))
        filter_value = runtime_data.genome["IPU_vision_filters"][str(kernel_size)][direction_key]
        for i in range(0, kernel_size):
            for ii in range(0, kernel_size):
                result[i][ii] = kernel_values[i][ii] * filter_value[i][ii]
                ii += 1
            i += 1
        # end_result[direction_key] = result
        return result

    @staticmethod
    def monochrome(image):
        """This function converts a gray-scale image to monochrome by setting all the pixels below a threshold to
        zero and above that threshold to 255."""
        row_index = 0
        col_index = 0
        new_image = [[] for x in range(np.shape(image)[1])]
        for row in image:
            for row_item in row:
                if row_item < runtime_data.parameters["InitData"]["image_monochromization_threshold"]:
                    new_image[row_index].append(0)
                else:
                    new_image[row_index].append(255)
                col_index += 1
            col_index = 0
            row_index += 1
        new_image = np.asarray(new_image, dtype=np.int)
        return new_image


class Kernel:
    @staticmethod
    def kernel_sizer(kernel_values):
        np.tmp = kernel_values
        kernel_size = np.shape(np.tmp)
        kernel_size = kernel_size[0]
        if divmod(kernel_size, 2)[1] == 0:
            print("Error: Kernel size should only be Odd number!")
            return
        return kernel_size

    def kernel_direction(self, kernel_values):
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
        kernel_size = self.kernel_sizer(kernel_values)
        # print("Kernel size is: ", kernel_size)
        for filter_entry in runtime_data.genome["IPU_vision_filters"][str(kernel_size)]:
            end_result[filter_entry] = Filter.direction(kernel_values, kernel_size, filter_entry)

        tmpArray = []
        # print('this is tmp before all appends', tmpArray)
        for entry in end_result:
            # print(entry, "\n", end_result[entry], "\n\n\n")
            sumation = np.sum(end_result[entry])
            # print("Appending: %s Sum: %d \n End_result: \n %s" % (entry, summation,end_result[entry]))
            # tmp = np.append(tmp, [entry, np.sum(end_result[entry])], axis=0)
            tmpArray.append([entry, np.sum(end_result[entry])])
            # print('***', tmpArray)
        # print("This is the end result: \n %s" % end_result)
        # print('tmp after appends %s' % tmpArray)
        maxValue = max(list(zip(*tmpArray))[1])
        # print("MaxValue: ", maxValue)
        maxValueIndex = list(zip(*tmpArray))[1].index(maxValue)
        direction = tmpArray[maxValueIndex][0]
        # direction = direction.replace('\\', '\')
        # print('max value is %s' % maxValue)
        # print('max index is %s' % maxValueIndex)
        # print('direction is %s' % direction)
        tempSum = 0
        for entry in tmpArray:
            tempSum += abs(entry[1])
        if tempSum == 0:
            return "^"
        return direction

    @staticmethod
    def kernel_contrast(kernel_values, kernel_size):
        filtered_kernel = Filter.direction(kernel_values, kernel_size, 'o')
        # contrast_value = np.sum(kernel_values * filtered_kernel)
        contrast_value = np.sum(filtered_kernel)
        if contrast_value < 0:
            contrast_value = 0
        return contrast_value

    # todo: This function is super slow............
    def create_direction_matrix(self, image, kernel_size, direction_sensitivity=''):
        """
        Generates a Matrix where each element outlines the direction detected by the Kernel filters against each
        corresponding pixel in the image.
        """
        # print(">>> >>>", kernel_size, type(kernel_size))
        if divmod(kernel_size, 2)[1] == 0:
            print("Error: Kernel size should only be Odd number!")
            return
        row_index = 0
        col_index = 0
        direction_matrix = [[] for x in range(np.shape(image)[1])]
        for row in image:
            for row_item in row:
                direction = self.kernel_direction(Image.image_read_by_block(image, kernel_size, [row_index, col_index]))
                if direction == direction_sensitivity or direction_sensitivity == '':
                    direction_matrix[row_index].append(direction)
                else:
                    direction_matrix[row_index].append('')
                col_index += 1
            col_index = 0
            row_index += 1
        return direction_matrix

    def create_direction_matrix2(self, image, kernel_size):
        """
        Generates a Matrix where each element outlines the direction detected by the Kernel filters against each
        corresponding pixel in the image.
        """
        if divmod(kernel_size, 2)[1] == 0:
            print("Error: Kernel size should only be Odd number!")
            return
        direction_sensitivity_options = runtime_data.genome["IPU_vision_filters"][str(kernel_size)]
        direction_matrix = {}

        row_index = 0
        col_index = 0

        # building a blank direction matrix
        blank_matrix_template = [[] for x in range(np.shape(image)[1])]
        for direction_sensitivity in direction_sensitivity_options:
            direction_matrix[direction_sensitivity] = blank_matrix_template

        for row in image:
            for row_item in row:
                image_block = Image.image_read_by_block(image, kernel_size, [row_index, col_index])
                for direction_sensitivity in direction_sensitivity_options:
                    actual_direction = self.kernel_direction(image_block)
                    if actual_direction == direction_sensitivity or direction_sensitivity == '':
                        direction_matrix[direction_sensitivity][row_index].append(direction_sensitivity)
                    else:
                        direction_matrix[direction_sensitivity][row_index].append('')
                col_index += 1
            col_index = 0
            row_index += 1
        return direction_matrix

    @staticmethod
    def orientation_matrix(raw_image, orientation_key, kernel_size):
        """
        Function to produce an orientation matrix based on the raw image data
        """
        return


class Image:
    @staticmethod
    def resize_image(img):
        img = imresize(img, size=runtime_data.parameters["InitData"]["image_magnification_factor"], interp='bicubic')
        return img

    @staticmethod
    def convert_image_to_coordinates(image):   # Image is currently assumed to be a 28 x 28 numpy array
        """
        Function responsible for reading an image and converting the pixel values to coordinates
        """
        # Note: currently set to function based on Gray scale image
        genome = runtime_data.genome

        image_locations = []
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                if image[x, y] >= genome["image_color_intensity_tolerance"]:
                    image_locations.append([x, y, 0])

        # Image location will be fed to another function to identify the Id of neurons to be activated
        return image_locations

    @staticmethod
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

    # todo: Cythonize this
    @staticmethod
    def convert_image_locations_to_neuron_ids_old(image_locations, cortical_area):
        """
        Queries the connectome for each location and provides the list of Neuron Ids matching the location
        :param image_locations:
        :return:
        """
        genome = runtime_data.genome

        neuron_id_list = []
        for x in range(len(image_locations)):
                # call the function to find neuron candidates for a given location
                tmp = architect.neuron_finder(cortical_area, image_locations[x], genome["location_tolerance"])
                for item in tmp:
                    if (item is not None) and (neuron_id_list.count(item) == 0):
                        neuron_id_list.append(item)

        return neuron_id_list

    @staticmethod
    def convert_image_locations_to_neuron_ids(image_locations, cortical_area):
        """
        Queries the connectome for each location and provides the list of Neuron Ids matching the location
        :param image_locations:
        :return:
        """
        neuron_id_list = []
        for x in range(len(image_locations)):
                block_reference = str(image_locations[x][0]) + '-' + \
                                  str(image_locations[x][1]) + '-' + \
                                  str(image_locations[x][2])
                if block_reference in runtime_data.block_dic[cortical_area]:
                    neuron_list = runtime_data.block_dic[cortical_area][block_reference]
                    # print("XXXXXXXXXX    XXXXXXXXX     XXXXXXXX", cortical_area, block_reference, len(neuron_list))
                    for item in neuron_list:
                        if (item is not None) and (neuron_id_list.count(item) == 0):
                            neuron_id_list.append(item)
        # print("YYYYYYYY    YYYYYYYY     YYYYYYY", cortical_area, neuron_id_list)
        return neuron_id_list

    @staticmethod
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

    # todo: Need to add a method to combine multiple IPU layer data into a single one
    #        -Think how to build a direction agnostic representation of an object

    @staticmethod
    def image_processing():
        """
        Function to read an image from a file and have it converted to it's fundamental components
        """
        return

    @staticmethod
    def image_orientation_detector():
        """
        Performs higher level analysis to detect the direction of an image
        """
        # todo: need to figure which processing layer this belongs to. It might need to go thru entire stack
        return

    @staticmethod
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


if __name__ == '__main__':

    filter = Filter()
    kernel = Kernel()
    image = Image()

    a = [
      [ .1,  .1,  .1]
     ,[ .1,  .1,  .1]
     ,[ .1,  .1,  .1]]


    b1 =[
      [ 10,  1,  1,  1,  1]
     ,[ 1,  10,  1,  1,  1]
     ,[ 1,  1,  10,  1,  1]
     ,[ 1,  1,  1,  10,  1]
     ,[ 1,  1,  1,  1,  10]]

    b2 =[
      [ 1,  1,  1,  1,  10]
     ,[ 1,  1,  1,  10,  1]
     ,[ 1,  1,  10,  1,  1]
     ,[ 1,  10,  1,  1,  1]
     ,[ 10,  1,  1,  1,  1]]


    b3 =[
      [ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]
     ,[ 10,  10,  10,  10,  10]
     ,[ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]]


    b4 =[
      [ 1,  1,  10,  1,  1]
     ,[ 1,  1,  10,  1,  1]
     ,[ 1,  1,  10,  1,  1]
     ,[ 1,  1,  10,  1,  1]
     ,[ 1,  1,  10,  1,  1]]


    b5 =[
      [ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]
     ,[ 1,  1,  10,  1,  1]
     ,[ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]]


    b6 =[
      [ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1]]

    b7 =[
      [ 0,  0,  0,  0,  0]
     ,[ 0,  0,  0,  0,  0]
     ,[ 0,  0,  0,  0,  0]
     ,[ 0,  0,  0,  0,  0]
     ,[ 0,  0,  0,  0,  0]]


    c = [
      [ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]]

    d = [
      [ 1,  1,  1]
     ,[ 1,  10,  1]
     ,[ 1,  1,  1]]

    e = [
      [10,  1,  1]
     ,[1, 10, 1]
     ,[1,  1,  10]]

    f = [
      [ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]
     ,[ 1,  1,  1,  1,  1,  1,  1]]

    thing = [b1, b2, b3, b4, b5, b6, b7]

    # for l1 in runtime_data.genome["IPU_vision_filters"]:
    #     print(l1)
    #     for l2 in runtime_data.genome["IPU_vision_filters"][l1]:
    #         print("    ", l2, "\n           ", runtime_data.genome["IPU_vision_filters"][l1][l2])
    #
    # for item in thing:
    #     print("\n\n\n\n** ** ** ** ** ")
    #     matrix = item
    #     for _ in matrix:
    #         print(_)
    #     print("\nKernel direction is: ", kernel.kernel_direction(matrix))
    #     print("** ** ** ** ** ")

    mnist = MNIST()

    img = mnist.mnist_img_fetcher2(4, 2, "training")

    print(">>>", img[0], "\n", img[1])

    direction = '/'

    # start_time = datetime.now()
    # direction_matrix = (kernel.create_direction_matrix(image=img[0], kernel_size=3, direction_sensitivity=direction))
    # print(">> Time taken for kernel=3: ", datetime.now()-start_time)
    #
    # start_time = datetime.now()
    # direction_matrix = (kernel.create_direction_matrix(image=img[0], kernel_size=5, direction_sensitivity=direction))
    # print(">> Time taken for kernel=5: ", datetime.now()-start_time)
    #
    # start_time = datetime.now()
    # direction_matrix = (kernel.create_direction_matrix(image=img[0], kernel_size=7, direction_sensitivity=direction))
    # print(">> Time taken for kernel=7: ", datetime.now()-start_time)
    #
    # print("\n")
    # direction = '/'
    #
    # start_time = datetime.now()
    # direction_matrix = (kernel.create_direction_matrix(image=img[0], kernel_size=3, direction_sensitivity=direction))
    # print(">> Time taken for kernel=3: ", datetime.now()-start_time)
    #
    # start_time = datetime.now()
    # direction_matrix = (kernel.create_direction_matrix(image=img[0], kernel_size=5, direction_sensitivity=direction))
    # print(">> Time taken for kernel=5: ", datetime.now()-start_time)
    #
    # start_time = datetime.now()
    # direction_matrix = (kernel.create_direction_matrix(image=img[0], kernel_size=7, direction_sensitivity=direction))
    # print(">> Time taken for kernel=7: ", datetime.now()-start_time)

    start_time = datetime.now()
    direction_matrix = (kernel.create_direction_matrix2(image=img[0], kernel_size=3))
    print(">> Time taken for 3: ", datetime.now()-start_time)

    start_time = datetime.now()
    direction_matrix = (kernel.create_direction_matrix2(image=img[0], kernel_size=5))
    print(">> Time taken for 5: ", datetime.now()-start_time)

    start_time = datetime.now()
    direction_matrix = (kernel.create_direction_matrix2(image=img[0], kernel_size=7))
    print(">> Time taken for 7: ", datetime.now()-start_time)

    for direction in direction_matrix:
        print(direction, "\n", direction_matrix[direction])

