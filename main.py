
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
    visualizer.connectome_visualizer(cortical_area='vision_IT', neighbor_show='true')
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
    visualizer.cortical_heatmap(mnist.read_image(image_number), ['vision_v1', 'vision_v2', 'vision_IT'])
    return

image_number = 12

#show_cortical_areas()
trigger_first_burst(read_from_MNIST(image_number))
settings.save_brain_to_disk()



# IPU_vision.image_read_block(mnist.read_image(image_number), 3, [27, 27])

# print("Direction matrix with Kernel 3")
# a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 3))
# for items in range(0, np.shape(a)[0]):
#     print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))
#
# print("Direction matrix with Kernel 5")
# a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 5))
# for items in range(0, np.shape(a)[0]):
#     print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))
#
# print("Direction matrix with Kernel 7")
# a = (IPU_vision.create_direction_matrix(mnist.read_image(image_number), 7))
# for items in range(0, np.shape(a)[0]):
#     print(' '.join(map(str, [x.encode('utf-8') for x in a[items]])))
#
#
# print(IPU_vision.direction_stats(a))


# show_cortical_heatmap(image_number)

"""
# TODO: Handle burst scenarios where the input neuron does not have any neighbor neuron associated with
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
# todo: Figure how to pass the Brain Physiology to Genome as well. Currently Genome drives Brain Anatomy only.


# todo: NEXT    >>>>>   Fine tune Genome to produce distinguishable results as Neurons fire
#                       Update IPU module to include combination of multiple input types e.g. brightness, edges, etc.
#                       Fix issue on the visualization related to 3D init not compatible with 2D ones
#                       Update show_cortical_areas function to show all selected areas as sub_plots
#                       Need to figure how the Direction sensitive neurons in brain function
#               ****    Need to design a neuronal system that can receive an input and its output be a combination of
                        matching objects

Next Steps

1. Update Genome so a new Cortical area called “Memory” can be generated    >>>Done<<<
2. Rename Vision_MT to Vision_IT                                            >>>Done<<<
3. Do needed changes to map Vision_IT to Memory                             >>>Done<<<
4. Think of how to implement an alternative path so when an object is seen by visual it can be labeled “trained” using alternate path.
    1. In this case training the network is equal to exposing Network to two simultaneous events at the same time. The simultaneous occurrence would trigger a binding between Neurons in the Memory Module
5. Figure how Memory Module should be configured so it can behave as explained above
6. Configure an output module so after Memory module is activated the activation can be read back.
7. Figure how to Associate ASCii characters with neuronal readouts
8. Need to implement a looped structure to account for connecting events happening within a time delay of each-other

> Memory structure:
    -Don't have any of the neurons connected to each other
    -When neurons fire at the same time wire them together
    -Create a fire queue to account for minor firing time differences or have a service that periodically scans the 
    firing times and with a degree of error wire neurons together
    -Need to consider axon lenght as a factor driving the wiring of neurons in a given proximity. This is currently a 
    param in the Genome but not used anywhere int he code. Functions under neuron_functions module to be reviewed
    -Have the axon_avg_length as such that all the memory neurons can create synapse with all others this is to ensure
    when neurons react to an event but reside far from each other to be able to connect.
        Cons: Too many connections?
        

"""