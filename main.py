

from time import sleep
import multiprocessing as mp

"""
This file contains the main Brain control code
"""

__author__ = 'Mohammad Nadji-tehrani'


class Brain:
    @staticmethod
    def print_basic_info():
        import stats
        cp = mp.current_process()
        print("\rstarting", cp.name, cp.pid)
        print("\rConnectome database =                  %s" % universal_functions.parameters["InitData"]["connectome_path"])
        print("\rTotal neuron count in the connectome  %s  is: %i" % (
        universal_functions.parameters["InitData"]["connectome_path"] + 'vision_v1.json', stats.connectome_neuron_count(cortical_area='vision_v1')))
        print(' \rexiting', cp.name, cp.pid)
        return

    @staticmethod
    def show_cortical_areas():
        import visualizer
        # The following visualizes the connectome. Pass neighbor_show='true' as a parameter to view neuron relationships
        # visualizer.connectome_visualizer(cortical_area='vision_v1', neighbor_show='true')
        # visualizer.connectome_visualizer(cortical_area='vision_v2', neighbor_show='true')
        # visualizer.connectome_visualizer(cortical_area='vision_IT', neighbor_show='true')
        visualizer.connectome_visualizer(cortical_area='vision_memory', neighbor_show='true')
        return

    def see_from_mnist(self, mnist_img, fcl_queue, event_queue):
        cp = mp.current_process()
        # print(' starting', cp.name, cp.pid)
#        settings.reset_cumulative_counter_instances()   # ????
        fire_list= self.read_from_mnist(mnist_img, event_queue)
        self.inject_to_fcl(fire_list, fcl_queue)
        # print(' exiting', cp.name, cp.pid)
        return

    @staticmethod
    def read_from_mnist(mnist_img, event_queue):
        # print("Reading from MNIST")
        import architect
        import IPU_vision
        import universal_functions
        import mnist
        # Read image from MNIST database and translate them to activation in vision_v1 neurons & injects to FCL
        init_fire_list = []
#        IPU_vision_array = IPU_vision.convert_image_to_coordinates(mnist.read_image(image_number)[0])    # todo  ?????
        cortical_list = universal_functions.cortical_list()
        vision_group = []
        for item in cortical_list:
            if universal_functions.genome['blueprint'][item]['sub_group_id'] == 'vision_v1':
                vision_group.append(item)
        # print('vision group is: ', vision_group)
        image_ = mnist_img
        # image_ = mnist.read_image(image_number)
        image = image_[0]
        print("*** Image read from MNIST was :", image_[1])
        # print('image :\n ', np.array2string(image, max_line_width=np.inf))
        filter = IPU_vision.Filter()
        filtered_image = filter.brightness(image)
        # print('Filtered image :\n ', np.array2string(filter.brightness(image), max_line_width=np.inf))
        for cortical_area in vision_group:
            cortical_direction_sensitivity = universal_functions.genome['blueprint'][cortical_area]['direction_sensitivity']
            kernel_size = 7
            polarized_image = IPU_vision.create_direction_matrix(filtered_image, kernel_size, cortical_direction_sensitivity)
            # print("Polarized image for :", cortical_area)
            # print(np.array2string(np.array(polarized_image), max_line_width=np.inf))
            ipu_vision_array = IPU_vision.convert_direction_matrix_to_coordinates(polarized_image)
            neuron_id_list = IPU_vision.convert_image_locations_to_neuron_ids(ipu_vision_array, cortical_area)
            for item in neuron_id_list:
                init_fire_list.append([cortical_area, item])
        # Event is an instance of time where an IPU event has occurred
        event_id = architect.event_id_gen()
        print(" <> <> <> <> <> <> <> <> An event related to mnist reading with following id has been logged:", event_id)
        event_queue.put(event_id)
        # print('Initial Fire List:')
        # print(init_fire_list)
        return init_fire_list

    @staticmethod
    def inject_to_fcl(fire_list, fcl_queue):
        # print("Injecting to FCL.../\/\/\/")
        # Update FCL with new input data. FCL is read from the Queue and updated
        flc = fcl_queue.get()
        for item in fire_list:
            flc.append(item)
        fcl_queue.put(flc)
        # print("Injected to FCL.../\/\/\/")
        return

    @staticmethod
    def read_char(char, fcl_queue):
        import IPU_utf8
        cp = mp.current_process()
        # print(' starting', cp.name, cp.pid)
        if char:
            fire_list = IPU_utf8.convert_char_to_fire_list(char)
            print(fire_list)
            print("% % % % % % % % % % % % % % % % % % Injecting character >>>  %s <<<" % char)
            Brain.inject_to_fcl(fire_list, fcl_queue)
        # print(' exiting', cp.name, cp.pid)

    @staticmethod
    def read_user_input():
        print("Func: read_user_input : start")
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            setraw(sys.stdin.fileno())
            universal_functions.parameters["Input"]["user_input"] = sys.stdin.read(1)
            sys.stdout.write("\r%s" % user_input_queue)
            print("hahaha______hehehe")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # sys.stdout.flush()
        print("Func: read_user_input : end")
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

    @staticmethod
    def cortical_area_neuron_count(cortical_area):
        """
        Returns number of Neurons in the connectome
        """
        data = universal_functions.brain[cortical_area]
        neuron_count = 0
        for key in data:
            neuron_count += 1
        return neuron_count

    @staticmethod
    def cortical_area_synapse_count(cortical_area):
        """
        Returns number of Neurons in the connectome
        """
        data = universal_functions.brain[cortical_area]
        synapse_count = 0
        for neuron in data:
            for _ in data[neuron]['neighbors']:
                synapse_count += 1
        return synapse_count

    def connectome_neuron_count(self):
        total_neuron_count = 0
        for cortical_area in universal_functions.cortical_areas:
            total_neuron_count += self.cortical_area_neuron_count(cortical_area)
        return total_neuron_count

    def connectome_synapse_count(self):
        total_synapse_count = 0
        for cortical_area in universal_functions.cortical_areas:
            total_synapse_count += self.cortical_area_synapse_count(cortical_area)

        return total_synapse_count


if __name__ == '__main__':
    import sys
    from tty import setraw
    from datetime import datetime
    import termios
    import brain_gen
    import tkinter

    import mnist
    import neuron_functions
    import universal_functions

    if universal_functions.parameters["Switches"]["vis_show"]:
        import visualizer

    print("The main function is running... ... ... ... ... ... ... ... ... ... |||||   ||||   ||||")

    mp.set_start_method('spawn')

    def submit_entry_fields():
        print("Command entered is: %s\nParameter is: %s" % (e1.get(), e2.get()))
        if universal_functions.parameters["Input"]["user_input"]:
            universal_functions.parameters["Input"]["previous_user_input"] = universal_functions.parameters["Input"]["user_input"]
        if universal_functions.parameters["Input"]["previous_user_input"]:
            universal_functions.parameters["Input"]["previous_user_input_param"] = universal_functions.parameters["Input"]["user_input_param"]
        universal_functions.parameters["Input"]["user_input"] = e1.get()
        universal_functions.parameters["Input"]["user_input_param"] = e2.get()
        user_input_queue.put(universal_functions.parameters["Input"]["user_input"])

    master = tkinter.Tk()

    tkinter.Label(master, text="Command").grid(row=0)
    tkinter.Label(master, text="Parameter").grid(row=1)

    e1 = tkinter.Entry(master)
    e2 = tkinter.Entry(master)

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)

    tkinter.Button(master, text='Quit', command=master.quit).grid(row=3, column=0, pady=4)
    tkinter.Button(master, text='Submit', command=submit_entry_fields).grid(row=3, column=1, pady=4)

    b = Brain()

    # Calling function to regenerate the Brain from the Genome
    if universal_functions.parameters["InitData"]["regenerate_brain"]:
        brain_generation_start_time = datetime.now()
        brain_gen.main()
        brain_generation_duration = datetime.now() - brain_generation_start_time
        # settings.init_data()

        # todo: Move the following to stats module
        print("--------------------------------------------------------------")
        print("Brain generation lasted %s " % brain_generation_duration)
        print("--------------------------------------------------------------")
        print("Total Neuron count in Connectome is: ", b.connectome_neuron_count())
        print("--------------------------------------------------------------")
        print("Total Synapse count in Connectome is: ", b.connectome_synapse_count())
        print("--------------------------------------------------------------")

    # visualizer.cortical_activity_visualizer(['vision_v1', 'vision_v2', 'vision_IT', 'Memory'], x=30, y=30, z=30)

    # Initializing queues
    user_input_queue = mp.Queue()
    FCL_queue = mp.Queue()
    brain_queue = mp.Queue()
    event_queue = mp.Queue()

    # Initialize Fire Candidate List (FCL)
    FCL = []
    FCL_queue.put(FCL)

    # Setting up Brain queue for multiprocessing
    brain_data = universal_functions.brain
    brain_queue.put(brain_data)


    def read_user_input():
        master.update_idletasks()
        master.update()
        return

    def join_processes():
        # process_burst.join()
        process_burst.close()
        return

    def process_print_basic_info():
        process_1 = mp.Process(name='print_basic_info', target=b.print_basic_info)
        process_1.start()
        process_1.join()
        universal_functions.parameters["Input"]["user_input"] = ''
        return

    def process_show_cortical_areas():
        process_2 = mp.Process(name='show_cortical_areas', target=b.show_cortical_areas())
        process_2.start()
        process_2.join()
        universal_functions.parameters["Input"]["user_input"] = ''
        return

    def process_see_from_mnist():
        if universal_functions.parameters["Switches"]["vis_show"]:
            print(universal_functions.parameters["Switches"]["vis_show"])
            visualizer.cortical_heatmap(mnist.read_image(int(universal_functions.parameters["Input"]["user_input_param"]))[0], [])
        mnist_img = mnist.read_image(int(universal_functions.parameters["Input"]["user_input_param"]))
        process_3 = mp.Process(name='Seeing_MNIST_image', target=b.see_from_mnist,
                               args=(mnist_img, FCL_queue, event_queue))
        process_3.start()
        process_3.join()
        universal_functions.parameters["Input"]["user_input"] = ''
        return

    def process_read_char():
        process_4 = mp.Process(name='Reading input char',
                               target=Brain.read_char, args=(universal_functions.parameters["Input"]["user_input_param"], FCL_queue))
        process_4.start()
        process_4.join()
        universal_functions.parameters["Input"]["user_input"] = ''
        return

    def training_num_gen(num):
        import random
        rand_num = random.randrange(10, 500, 1)
        mnist_data = mnist.read_image(rand_num)
        while int(num) != mnist_data[1]:
            rand_num = random.randrange(10, 500, 1)
            mnist_data = mnist.read_image(random.randrange(10, 500, 1))
        return rand_num, mnist_data

    def process_auto_training():
        import random
        from time import sleep
        from datetime import datetime
        b = Brain()
        training_start_time = datetime.now()
        print("---------------------------------------------------------------------Auto training has been initiated.")
        for number in range(10):
            mnist_num, mnist_img = training_num_gen(number)
            if universal_functions.parameters["Switches"]["vis_show"]:
                visualizer.cortical_heatmap(mnist.read_image(mnist_num), [])
            # Following for loop help to train for a single number n number of times
            for x in range(int(universal_functions.parameters["Input"]["user_input_param"])):
                print(">>  >>  >>  >>  >>  >>  >>  >>  >>  Training round %i for number %s" % (x + 1, mnist_img[1]))
                mnist_img_char = str(mnist_img[1])
                process_5 = mp.Process(name='Seeing_MNIST_image', target=b.see_from_mnist,
                                       args=(mnist_img, FCL_queue, event_queue))
                process_6 = mp.Process(name='Reading input char', target=b.read_char, args=(str(mnist_img_char), FCL_queue))
                process_5.start()
                sleep(universal_functions.parameters["Timers"]["auto_train_delay"])
                process_6.start()
                # process_5.join()
                # process_6.join()

            # Placing training on hold till neuronal activities for previous training set is ramped down
            fcl = FCL_queue.get()
            fcl_length = len(fcl)
            FCL_queue.put(fcl)
            while fcl_length > 0:
                sleep(5)
                fcl = FCL_queue.get()
                fcl_length = len(fcl)
                FCL_queue.put(fcl)

        training_duration = datetime.now() - training_start_time
        print("---------------------------------------------------------------------Auto training has been completed.")
        print("Training lasted %s " % training_duration)
        print("--------------------------------------------------------------")
        universal_functions.parameters["Input"]["user_input"] = 'x'
        return

    def process_auto_test():
        """
        Test approach:
        
        - Ask user for number of times testing every digit call it x
        - Inject each number x rounds with each round conclusion being a "Comprehensions"
        - Count the number of True vs. False Comprehensions
        - Collect stats for each number and report at the end of testing
        
        """

        print('Testing Testing Testing', universal_functions.parameters["Input"]["comprehended_char"])
        import random
        from time import sleep
        from datetime import datetime
        b = Brain()
        testing_start_time = datetime.now()
        print("---------------------------------------------------------------------Auto testing has been initiated.")

        test_stats = list()

        for number in range(10):
            mnist_num, mnist_img = training_num_gen(number)
            if universal_functions.parameters["Switches"]["vis_show"]:
                visualizer.cortical_heatmap(mnist.read_image(mnist_num), [])

            # Following For loop test brain comprehension of a character x number of times
            true_comprehensions = 0
            total_comprehensions = 0
            for x in range(int(universal_functions.parameters["Input"]["user_input_param"])):
                print(">>  >>  >>  >>  >>  >>  >>  >>  >>  Testing round %i out of %i for number %s"
                      %(x + 1, int(universal_functions.parameters["Input"]["user_input_param"]), mnist_img[1]))
                mnist_img_char = str(mnist_img[1])

                # Periodically check to see what Character was comprehended and evaluate True or False
                comprehension = False
                comprehension_attempts = 0
                while not comprehension:
                    # The following process starts reading from MNIST and injecting it into the brain
                    process_7 = mp.Process(name='Seeing_MNIST_image', target=b.see_from_mnist,
                                           args=(mnist_img, FCL_queue, event_queue))
                    process_7.start()
                    comprehension_attempts += 1
                    print("This is comprehension attempt # %i" %comprehension_attempts)
                    if comprehension_attempts >= universal_functions.parameters["Switches"]["auto_test_comp_attempt_threshold"]:
                        print("Comprehension attempt threshold for this round has been exceeded!!")
                        break
                    # Read the flag to see if there has been comprehension
                    comprehended_value = universal_functions.parameters["Input"]["comprehended_char"]
                    print("++++++++   ++++  ++  + The value for comprehended_char is currently: ", comprehended_value)
                    if comprehended_value:
                        print("$$$$$$      Current comprehended value is:", comprehended_value)
                        total_comprehensions += 1
                        if comprehended_value == mnist_img_char:
                            true_comprehensions += 1
                        universal_functions.parameters["Input"]["comprehended_char"] = ''
                    print("So far there were %i correct comprehension out of total of %i"
                          % (true_comprehensions, total_comprehensions))

                    sleep(universal_functions.parameters["Timers"]["auto_test_delay"])
                    # process_5.join()
                    # process_6.join()

            test_stats.append([number, total_comprehensions, true_comprehensions])

            # Placing training on hold till neuronal activities for previous training set is ramped down
            fcl = FCL_queue.get()
            fcl_length = len(fcl)
            FCL_queue.put(fcl)
            while fcl_length > 0:
                sleep(5)
                fcl = FCL_queue.get()
                fcl_length = len(fcl)
                FCL_queue.put(fcl)

        testing_duration = datetime.now() - testing_start_time
        print("---------------------------------------------------------------------Auto testing has been completed.")
        print("Testing lasted %s " % testing_duration)
        print("--------------------------------------------------------------")
        print("Test Stats")
        print(test_stats)
        print("--------------------------------------------------------------")

        # logging stats into Genome
        universal_functions.genome_stats["test_stats"] = test_stats

        universal_functions.parameters["Input"]["user_input"] = 'x'
        return


    # Starting the burst machine
    # pool = mp.Pool(max(1, mp.cpu_count()))

    process_burst = mp.Pool(1, neuron_functions.burst, (user_input_queue, FCL_queue, brain_queue, event_queue,))

    # process_burst = mp.Process(name='Burst process', target=neuron_functions.burst,
    #                            args=(user_input_queue, FCL_queue, brain_queue, event_queue))

    process_burst.deamon = False

    read_user_input()

    try:
        while universal_functions.parameters["Input"]["user_input"] != 'q':
            # if universal_functions.parameters["Input"]["user_input"] != settings.Input.previous_user_input and \
                 #           universal_functions.parameters["Input"]["user_input"]_param != settings.Input.previous_user_input_param:
            # print(">>>>>>   >>>>>>>   >>>>>   >>>>>  >>  >>  --\__/--  <<  <<    <<<<<<", universal_functions.parameters["Input"]["user_input"], settings.Input.previous_user_input)
            try:
                if universal_functions.parameters["Input"]["user_input"] == 'p':
                    process_print_basic_info()
                    universal_functions.parameters["Input"]["user_input"] = ''

                elif universal_functions.parameters["Input"]["user_input"] == 's':
                    process_show_cortical_areas()
                    universal_functions.parameters["Input"]["user_input"] = ''

                elif universal_functions.parameters["Input"]["user_input"] == 'i':
                    process_see_from_mnist()
                    universal_functions.parameters["Input"]["user_input"] = ''

                elif universal_functions.parameters["Input"]["user_input"] == 'c':
                    process_read_char()
                    universal_functions.parameters["Input"]["user_input"] = ''

                elif universal_functions.parameters["Input"]["user_input"] == 'a':
                    process_auto_training()
                    universal_functions.parameters["Input"]["user_input"] = ''

                elif universal_functions.parameters["Input"]["user_input"] == 't':
                    process_auto_test()
                    universal_functions.parameters["Input"]["user_input"] = ''

                else:
                    read_user_input()
                    sleep(2)

            except IOError:
                print("an error has occurred!!!")
                pass

    finally:
        print("Finally!")
        universal_functions.brain = brain_queue.get()
        join_processes()
        universal_functions.save_brain_to_disk()
        universal_functions.save_genome_to_disk()

#
#
#          <<<<<<<   T O   D O   L I S T   >>>>>>>>
#

# Key problem on hand
# todo: The value from comprehended char from settings is keep reseting hence the correct value not being passed on
# todo: Need a self tuning mechanism

# Problems to fix
# todo: Synaptic activities in Memory everntually get to a point that does not ramp down
# todo: One number's visual memory is resembling all others
# todo: Brain is being loaded in memory too regularly

# General Architecture - Anatomy
# todo: Consider Headache and Sleep needs
# todo: Move Rules to Genome
# todo: Consider Synaptic capacity as a property of each neuron
# todo: Account for Neuron morphology as a Neuron property
# todo: Dynamic synaptic capacity when system is shaping vs its established
# todo: Accounting for Synaptic rearrangement
# todo: Fine tune Genome to produce distinguishable results as Neurons fire
# todo: Define streams containing a chain of cortical areas for various functions such as vision, hearing, etc.
# todo: find a way to speed up brain building when synapse creation is not needed e.g. memory, utf8
# todo: Synapse creation takes a very long time in presence of large neurons. Think of a way to limit the scope. zipcode
# todo: Build a cost function to measure the effectiveness and quality of relative synapse count in each layer

# Input handling
# todo: Use directional kernal analysis data as part of input data
# todo: Update IPU module to include combination of multiple input types e.g. brightness, edges, etc.
# todo: Perform edge detection on the images from MNIST and feed them to network (OpenCL or other methods)
# todo: Figure how to Associate ASCii characters with neuronal readouts
# todo: Need to figure how the Direction sensitive neurons in brain function
# todo: Need to design a neuronal system that can receive an input and its output be a combination of matching objects


# Neuron functions - Physiology
# todo: Let all the Neuron times be a factor of average Burst duration instead of fix number
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
# todo: Main function is running with every process along with all the initializations. This needs optimization


# Analysis
# todo: Come up with a way to analyze and categorize output data
# todo: Add ability to show activity percentage for each cortical area


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
