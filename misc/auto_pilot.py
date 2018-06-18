import random
from PUs import IPU_vision
from datetime import datetime
from time import sleep
import multiprocessing as mp
from misc import brain_functions, universal_functions, visualizer

if universal_functions.parameters["Switches"]["vis_show"]:
    pass


def training_num_gen(num):
    rand_img_index = random.randrange(10, 500, 1)
    mnist_data = IPU_vision.read_image(rand_img_index)
    labeled_img = IPU_vision.read_image(random.randrange(10, 500, 1))

    while int(num) != mnist_data[1]:
        rand_img_index = random.randrange(10, 500, 1)
        mnist_data = IPU_vision.read_image(rand_img_index)
        print("mnist_data[1] type is: ", type(mnist_data[1]))
        labeled_img = IPU_vision.read_image(random.randrange(10, 500, 1))
        print("training number generator is using the random index :", rand_img_index)
        print("training number is: ", num)
        print("mnist data label is:", mnist_data[1])
        print("\n")
    return rand_img_index, labeled_img

