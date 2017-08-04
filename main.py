
"""
This file contains the main Brain control code
"""
import multiprocessing as mp

import settings
settings.init()

import time
import visualizer
import architect
import mnist
import IPU_vision
import neuron_functions
import stats


__authur__ = 'Mohammad Nadji-tehrani'


class Brain:

    # def __init__(self):

    def print_basic_info(self):
        cp = mp.current_process()
        print("\rstarting", cp.name, cp.pid)
        print("\rconnectome database =                  %s" % settings.connectome_path)
        print("\rInitial input Neuron trigger list 1 =    %s" % settings.input_neuron_list_1)
        print("\rInitial input Neuron trigger list 2 =    %s" % settings.input_neuron_list_2)
        print("\rTotal neuron count in the connectome  %s  is: %i" % (
        settings.connectome_path + 'vision_v1.json', stats.connectome_neuron_count(cortical_area='vision_v1')))
        print(' \rexiting', cp.name, cp.pid)
        return

    def show_cortical_areas(self):
        # The following visualizes the connectome. Pass neighbor_show='true' as a parameter to view neuron relationships
        visualizer.connectome_visualizer(cortical_area='vision_v1', neighbor_show='true')
        visualizer.connectome_visualizer(cortical_area='vision_v2', neighbor_show='true')
        visualizer.connectome_visualizer(cortical_area='vision_IT', neighbor_show='true')
        return

    def read_from_mnist(self, image_number):
        # Read image from MNIST database and translate them to activation in vision_v1 neurons & injects to FCL
        IPU_vision_array = IPU_vision.convert_image_to_coordinates(mnist.read_image(image_number))
        neuron_id_list = IPU_vision.convert_image_locations_to_neuron_ids(IPU_vision_array)
        init_fire_list = []
        for item in neuron_id_list:
            init_fire_list.append(['vision_v1', item])
        settings.event_id = architect.event_id_gen()
        print('Initial Fire List:')
        print(init_fire_list)
        return init_fire_list

    def inject_to_fcl(self, fire_list, fcl_queue):
        # Update FCL with new input data. FCL is read from the Queue and updated
        # todo:
        fcl = fcl_queue.get()
        for item in fire_list:
            FCL.append(item)
        fcl_queue.put(fcl)
        return

    def show_cortical_heatmap(self, image_number):
        # Visualize a list of cortical areas passed in in List format
        visualizer.cortical_heatmap(mnist.read_image(image_number), ['vision_v1', 'vision_v2', 'vision_IT', 'Memory'])
        return

    def see_mnist(self, image_number, fcl_queue):
        cp = mp.current_process()
        print(' starting', cp.name, cp.pid)
        settings.reset_cumulative_counter_instances()
        fire_list = self.read_from_mnist(image_number)
        print(fire_list)
        self.inject_to_fcl(fire_list, fcl_queue)
        print(' exiting', cp.name, cp.pid)
        return


if __name__ == '__main__':
    import sys
    from tty import setraw
    import termios

    b = Brain()

    # Initializing queues
    user_input_queue = mp.Queue()
    FCL_queue = mp.Queue()

    def read_user_input():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            setraw(sys.stdin.fileno())
            settings.user_input = sys.stdin.read(1)
            sys.stdout.write("\r%s" % user_input_queue)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # sys.stdout.flush()
        return

    def read_user_input2():
        settings.user_input = input()
        user_input_queue.put(settings.user_input)
        return

    def join_processes():
        process_1.join()
        process_2.join()
        process_3.join()
        process_burst.join()
        return

    # Initialize Fire Candidate List (FCL)
    FCL = []
    FCL_queue.put(FCL)

    # Starting the burst machine
    process_burst = mp.Process(name='Burst process', target=neuron_functions.burst, args=(user_input_queue, FCL_queue))
    process_burst.deamon = True
    process_burst.start()

    read_user_input2()

    try:
        while settings.user_input != 'q':
            try:
                if settings.user_input == 'a':
                    process_1 = mp.Process(name='print_basic_info', target=b.print_basic_info)
                    process_1.start()
                    settings.user_input = ''

                elif settings.user_input == 's':
                    process_2 = mp.Process(name='show_cortical_areas', target=b.show_cortical_areas())
                    process_2.start()
                    settings.user_input = ''

                elif settings.user_input == 'd':
                    process_3 = mp.Process(name='Seeing_MNIST_image', target=b.see_mnist, args=(10,FCL_queue))
                    process_3.start()
                    settings.user_input = ''

                # elif settings.user_input == 'f':
                #     process_burst = mp.Process(name='Burst process', target=b.start, args=(10))
                #     process_burst.deamon = True
                #     process_burst.start()
                #     settings.user_input = ''

                elif settings.user_input == 'g':
                    process_3.terminate()
                    # sys.stdout.write("\rHaHaHa!!!")
                    # sys.stdout.flush()
                    settings.user_input = ''

                else:
                    read_user_input2()

            except IOError:
                print("an error has occurred!!!")
                pass

    finally:
        print("Finally!")
        settings.save_brain_to_disk()


# neuron_functions.burst()

# show_cortical_areas()

# stats.print_cortical_stats()

# visualizer.connectome_visualizer('vision_v1', neighbor_show='true', threshold=0)

# visualizer.cortical_activity_visualizer(['vision_v1', 'vision_v2', 'vision_IT', 'Memory'], x=30, y=30, z=30)

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


#       Multi processing objectives:
#           -Ability to read text from user at any time
#           -Ability to read image number from user at any time

# todo: Next >>>>> Turn things around      <<<<<<<<<<    NEXT!!!!!!!!!!!    <<<<<<<<<<<<<<<<
#   -start with the first burst eventhough FCL is empty
#   -Remove the exit criteria which exits burst if FCL is empty. Add a sleep and make it unlimited loop
#   -Build a function to Inject into FCL
#   -Have a way to share the connectome, FCL and User Input shared between processes and implement locks to protect it
#           Options:    Pipe, Queue, joinableQueue, Manager, Value


# todo:  How to get output from memory ??? How to comprehend it ????
# todo: Look into  GPU leverage



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
# todo: Figure how to pass the Brain Physiology to Genome as well. Currently Genome drives Brain Anatomy only.
# todo: Define streams containing a chain of cortical areas for various functions such as vision, hearing, etc.


# todo: Synaptic_strenght currently growing out of bound. Need to impose limits
# todo: Use directional kernal analysis data as part of input data
# todo: Fine tune Genome to produce distinguishable results as Neurons fire
# todo: Update IPU module to include combination of multiple input types e.g. brightness, edges, etc.
# todo: Fix issue on the visualization related to 3D init not compatible with 2D ones
# todo: Need to figure how the Direction sensitive neurons in brain function
# todo: Need to design a neuronal system that can receive an input and its output be a combination of matching objects

# todo: Think of how to implement an alternative path so when an object is seen by visual it can be labeled “trained”
# using alternate path.
#     1. In this case training the network is equal to exposing Network to two simultaneous events at the same time. The simultaneous occurrence would trigger a binding between Neurons in the Memory Module
# todo: Figure how Memory Module should be configured so it can behave as explained above
# todo: Configure an output module so after Memory module is activated the activation can be read back.
# todo: Figure how to Associate ASCii characters with neuronal readouts
# todo: Need to implement a looped structure to account for connecting events happening within a time delay of each-other

