
"""
This file contains the main Brain control code
"""

import settings

settings.init()
import numpy as np
import visualizer
import architect
import mnist
import IPU_vision
import neuron_functions
import stats


def print_basic_info():
    print("connectome database =                  %s" % settings.connectome_path)
    print("Initial input Neuron trigger list =    %s" % settings.input_neuron_list_1)
    print("Initial input Neuron trigger list =    %s" % settings.input_neuron_list_2)
    print("Total neuron count in the connectome  %s  is: %i" % (
    settings.connectome_path + 'vision_v1.json', stats.connectome_neuron_count(cortical_area='vision_v1')))

    return


def show_cortical_areas():
    # The following visualizes the connectome. Pass neighbor_show='true' as a parameter to view neuron relationships
    visualizer.connectome_visualizer(cortical_area='vision_v1', neighbor_show='true')
    visualizer.connectome_visualizer(cortical_area='vision_v2', neighbor_show='true')
    visualizer.connectome_visualizer(cortical_area='vision_MT', neighbor_show='true')
    return


def read_from_MNIST(image_number):
    # Read image from MNIST database and translate them to activation in vision_v1 neurons
    IPU_vision_array = IPU_vision.convert_image_to_coordinates(mnist.read_image(image_number))
    neuron_id_list = IPU_vision.convert_image_locations_to_neuron_ids(IPU_vision_array)
    init_fire_list = []
    for item in neuron_id_list:
        init_fire_list.append(['vision_v1', item])
    print(init_fire_list)
    return init_fire_list


def trigger_first_burst(init_fire_list):
    # The following initiates an initial burst of input to the System
    neuron_functions.burst(init_fire_list)
    return


def show_cortical_heatmap(image_number):
    # Visualize a list of cortical areas passed in in List format
    visualizer.cortical_heatmap(mnist.read_image(image_number), ['vision_v1', 'vision_v2', 'vision_MT'])
    return

image_number = 12

#show_cortical_areas()
#trigger_first_burst(read_from_MNIST(image_number))
#settings.save_brain_to_disk()



# IPU_vision.image_read_block(mnist.read_image(image_number), 3, [27, 27])

print("Direction matrix with Kernel 3")
a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 3))
for items in range(0, np.shape(a)[0]):
    print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))

print("Direction matrix with Kernel 5")
a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 5))
for items in range(0, np.shape(a)[0]):
    print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))

print("Direction matrix with Kernel 7")
a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 7))
for items in range(0, np.shape(a)[0]):
    print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))


print(IPU_vision.direction_stats(a))


# show_cortical_heatmap(image_number)

"""
# todo: Handle burst scenarios where the input neuron does not have any neighbor neuron associated with
# todo: Create the pruner function
# todo: Perform edge detection on the images from MNIST and feed them to network
# todo: Come up with a way to analyze and categorize output data
# todo: Build multiple layers which receive same image but with different angle so the overlay be remembered
# todo: Consideration for how to evolve the network over generations. Update Genome based on some constraints
# todo: Consider Synaptic capacity as a property of each neuron
# todo: Account for Neuron morphology as a Neuron property
# todo: What could trigger evolution of a cortical area?
# todo: Consider a method to reward or punish neuron so it can evolve
# todo: Dynamic synaptic capacity when system is shaping vs its established
# todo: Accounting for Synaptic rearrangement
# todo: Update the algorithm responsible to improving the synapse strength to consider simultaneous firing of others
# todo: To account for LTD or Long Term Synaptic Depression
# todo: Ability to detect the dominant direction before higher level processing


# todo: NEXT    >>>>>   Fine tune Genome to produce distinguishable results as Neurons fire
#                       Update IPU module to include combination of multiple input types e.g. brightness, edges, etc.
#                       Fix issue on the visualization related to 3D init not compatible with 2D ones
#                       Update show_cortical_areas function to show all selected areas as sub_plots
#                       Need to figure how the Direction sensitive neurons in brain function

"""




