import settings
settings.init()
import multiprocessing as mp
import visualizer
import architect
import mnist
import IPU_vision
import IPU_utf8
import neuron_functions
import stats
import numpy as np
from time import sleep

"""
This file contains the main Brain control code
"""

__author__ = 'Mohammad Nadji-tehrani'


class Brain:

    # def __init__(self):

    def print_basic_info(self):
        cp = mp.current_process()
        print("\rstarting", cp.name, cp.pid)
        print("\rConnectome database =                  %s" % settings.connectome_path)
        print("\rInitial input Neuron trigger list 1 =    %s" % settings.input_neuron_list_1)
        print("\rInitial input Neuron trigger list 2 =    %s" % settings.input_neuron_list_2)
        print("\rTotal neuron count in the connectome  %s  is: %i" % (
        settings.connectome_path + 'vision_v1.json', stats.connectome_neuron_count(cortical_area='vision_v1')))
        print(' \rexiting', cp.name, cp.pid)
        return

    def show_cortical_areas(self):
        # The following visualizes the connectome. Pass neighbor_show='true' as a parameter to view neuron relationships
        # visualizer.connectome_visualizer(cortical_area='vision_v1', neighbor_show='true')
        # visualizer.connectome_visualizer(cortical_area='vision_v2', neighbor_show='true')
        # visualizer.connectome_visualizer(cortical_area='vision_IT', neighbor_show='true')
        visualizer.connectome_visualizer(cortical_area='vision_memory', neighbor_show='true')
        return

    def see_from_mnist(self, image_number, fcl_queue, event_queue):
        cp = mp.current_process()
        print(' starting', cp.name, cp.pid)
        settings.reset_cumulative_counter_instances()   # ????
        fire_list= self.read_from_mnist(image_number, event_queue)
        self.inject_to_fcl(fire_list, fcl_queue)
        print(' exiting', cp.name, cp.pid)
        return

    def read_from_mnist(self, image_number, event_queue):
        # Read image from MNIST database and translate them to activation in vision_v1 neurons & injects to FCL
        init_fire_list = []
        IPU_vision_array = IPU_vision.convert_image_to_coordinates(mnist.read_image(image_number))    # todo  ?????
        cortical_list  = settings.cortical_list()
        vision_group = []
        for item in cortical_list:
            if settings.genome['blueprint'][item]['sub_group_id'] == 'vision_v1':
                vision_group.append(item)
        # print('vision group is: ', vision_group)
        image = mnist.read_image(image_number)
        print('image :\n ', np.array2string(image, max_line_width=np.inf))
        filter = IPU_vision.Filter()
        filtered_image = filter.brightness(image)
        print('Filtered image :\n ', np.array2string(filter.brightness(image), max_line_width=np.inf))
        for cortical_area in vision_group:
            cortical_direction_sensitivity = settings.genome['blueprint'][cortical_area]['direction_sensitivity']
            kernel_size = 7
            polarized_image = IPU_vision.create_direction_matrix(filtered_image, kernel_size, cortical_direction_sensitivity)
            print("Polarized image for :", cortical_area)
            print(np.array2string(np.array(polarized_image), max_line_width=np.inf))
            IPU_vision_array = IPU_vision.convert_direction_matrix_to_coordinates(polarized_image)
            neuron_id_list = IPU_vision.convert_image_locations_to_neuron_ids(IPU_vision_array, cortical_area)
            for item in neuron_id_list:
                init_fire_list.append([cortical_area, item])
        event_id = architect.event_id_gen()
        event_queue.put(event_id)
        # print('Initial Fire List:')
        # print(init_fire_list)
        return init_fire_list

    def inject_to_fcl(self, fire_list, fcl_queue):
        # Update FCL with new input data. FCL is read from the Queue and updated
        flc = fcl_queue.get()
        for item in fire_list:
            flc.append(item)
        fcl_queue.put(flc)
        return

    def read_char(self, char, fcl_queue):
        cp = mp.current_process()
        print(' starting', cp.name, cp.pid)
        if char:
            fire_list = IPU_utf8.convert_char_to_fire_list(char)
            print(fire_list)
            self.inject_to_fcl(fire_list, fcl_queue)
        print(' exiting', cp.name, cp.pid)

    def read_user_input(self):
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

    # def kernel_view(self):
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
        # return


if __name__ == '__main__':

    import sys
    from tty import setraw
    import termios
    import brain_gen
    import tkinter


    def submit_entry_fields():
        print("Command entered is: %s\nParameter is: %s" % (e1.get(), e2.get()))
        settings.user_input = e1.get()
        settings.user_input_param = e2.get()
        user_input_queue.put(settings.user_input)

    master = tkinter.Tk()

    tkinter.Label(master, text="Command").grid(row=0)
    tkinter.Label(master, text="Parameter").grid(row=1)

    e1 = tkinter.Entry(master)
    e2 = tkinter.Entry(master)

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)

    tkinter.Button(master, text='Quit', command=master.quit).grid(row=3, column=0, pady=4)
    tkinter.Button(master, text='Submit', command=submit_entry_fields).grid(row=3, column=1, pady=4)

    # Calling function to regenerate the Brain from the Genome
    brain_gen.brain_gen()

    b = Brain()

    # visualizer.cortical_activity_visualizer(['vision_v1', 'vision_v2', 'vision_IT', 'Memory'], x=30, y=30, z=30)

    mp.set_start_method('spawn')

    # Initializing queues
    user_input_queue = mp.Queue()
    FCL_queue = mp.Queue()
    brain_queue = mp.Queue()
    event_queue = mp.Queue()

    # Initialize Fire Candidate List (FCL)
    FCL = []
    FCL_queue.put(FCL)

    # Setting up Brain queue for multiprocessing
    brain_data = settings.brain
    brain_queue.put(brain_data)


    def read_user_input():
        master.update_idletasks()
        master.update()
        return

    def join_processes():
        # process_burst.join()
        process_burst.close()
        return

    # Starting the burst machine
    # pool = mp.Pool(max(1, mp.cpu_count()))

    process_burst = mp.Pool(1, neuron_functions.burst, (user_input_queue, FCL_queue, brain_queue, event_queue,))

    # process_burst = mp.Process(name='Burst process', target=neuron_functions.burst,
    #                            args=(user_input_queue, FCL_queue, brain_queue, event_queue))

    process_burst.deamon = False


    read_user_input()

    try:
        while settings.user_input != 'q':
            try:
                if settings.user_input == 'a':
                    process_1 = mp.Process(name='print_basic_info', target=b.print_basic_info)
                    process_1.start()
                    process_1.join()
                    settings.user_input = ''

                elif settings.user_input == 's':
                    process_2 = mp.Process(name='show_cortical_areas', target=b.show_cortical_areas())
                    process_2.start()
                    process_2.join()
                    settings.user_input = ''

                elif settings.user_input == 'i':
                    # Visualize MNIST input
                    # visualizer.mnist_img_show(mnist.read_image(int(settings.user_input_param)))
                    visualizer.cortical_heatmap(mnist.read_image(int(settings.user_input_param)), [])
                    process_3 = mp.Process(name='Seeing_MNIST_image', target=b.see_from_mnist,
                                           args=(int(settings.user_input_param), FCL_queue, event_queue))
                    process_3.start()
                    process_3.join()
                    settings.user_input = ''

                elif settings.user_input == 'c':
                    process_4 = mp.Process(name='Reading input char',
                                           target=b.read_char, args=(settings.user_input_param, FCL_queue))
                    process_4.start()
                    process_4.join()
                    settings.user_input = ''

                else:
                    read_user_input()

            except IOError:
                print("an error has occurred!!!")
                pass

    finally:
        print("Finally!")
        settings.brain = brain_queue.get()
        join_processes()
        settings.save_brain_to_disk()

#
#
#          <<<<<<<  T O   D O   L I S T   >>>>>>>>
#


# General Architecture - Anatomy
# todo: Move Rules to Genome
# todo: Consider Synaptic capacity as a property of each neuron
# todo: Account for Neuron morphology as a Neuron property
# todo: Dynamic synaptic capacity when system is shaping vs its established
# todo: Accounting for Synaptic rearrangement
# todo: Fine tune Genome to produce distinguishable results as Neurons fire
# todo: Define streams containing a chain of cortical areas for various functions such as vision, hearing, etc.
# todo: find a way to speed up brain building when synapse creation is not needed e.g. memory, utf8
# todo: Synapse creation takes a very long time in presence of large neurons. Think of a way to limit the scope. zipcode

# Input handling
# todo: Use directional kernal analysis data as part of input data
# todo: Update IPU module to include combination of multiple input types e.g. brightness, edges, etc.
# todo: Perform edge detection on the images from MNIST and feed them to network (OpenCL or other methods)
# todo: Figure how to Associate ASCii characters with neuronal readouts
# todo: Need to figure how the Direction sensitive neurons in brain function
# todo: Need to design a neuronal system that can receive an input and its output be a combination of matching objects


# Neuron functions - Physiology
# todo: Create the pruner function
# todo: Synaptic_strenght currently growing out of bound. Need to impose limits
# todo: Handle burst scenarios where the input neuron does not have any neighbor neuron associated with
# todo: To account for LTD or Long Term Synaptic Depression
# todo: Update the algorithm responsible to improving the synapse strength to consider simultaneous firing of others
# todo: Figure how to pass the Brain Physiology to Genome as well. Currently Genome drives Brain Anatomy only.
# todo: Need to imp. a looped structure to account for connecting events happening within a time delay of each-other
# todo: Ability to detect the dominant direction before higher level processing


# Genetic Evolution
# todo: regenerative model.
# todo: Consideration for how to evolve the network over generations. Update Genome based on some constraints
# todo: What could trigger evolution of a cortical area?
# todo: Consider a method to reward or punish neuron so it can evolve
# todo: Build a Genome Generator


# Multi processing
# todo: Look into  GPU leverage


# Analysis
# todo: Come up with a way to analyze and categorize output data


# Memory
# todo: Think of how to implement an alternative path so when an object is seen by visual it can be labeled “trained”
# using alternate path.
#     1. In this case training the network is equal to exposing Network to two simultaneous events at the same time.
#  The simultaneous occurrence would trigger a binding between Neurons in the Memory Module
# todo: Figure how Memory Module should be configured so it can behave as explained above
# todo: Configure an output module so after Memory module is activated the activation can be read back.
# todo: How to get output from memory ??? How to comprehend it ????


# Visualization
# todo: Fix issue where some cortical activities are not showing up    <<<  NEXT !!!!!


# Speech
# todo: Make it learn to Speak!
