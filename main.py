

"""
This file contains the main Brain control code
"""

__author__ = 'Mohammad Nadji-tehrani'


if __name__ == '__main__':
    from datetime import datetime
    import brain_gen
    import tkinter
    from time import sleep
    import multiprocessing as mp
    from PUs import IPU_vision
    from misc import brain_functions, auto_pilot, neuron_functions, universal_functions, visualizer

    if universal_functions.parameters["Switches"]["vis_show"]:
        pass

    print("The main function is running... ... ... ... ... ... ... ... ... ... |||||   ||||   ||||")

    mp.set_start_method('spawn')

    def submit_entry_fields():
        print("Command entered is: %s\nParameter is: %s" % (e1.get(), e2.get()))
        if universal_functions.parameters["Input"]["user_input"]:
            universal_functions.parameters["Input"]["previous_user_input"] = \
                universal_functions.parameters["Input"]["user_input"]
        if universal_functions.parameters["Input"]["previous_user_input"]:
            universal_functions.parameters["Input"]["previous_user_input_param"] = \
                universal_functions.parameters["Input"]["user_input_param"]
        universal_functions.parameters["Input"]["user_input"] = e1.get()
        universal_functions.parameters["Input"]["user_input_param"] = e2.get()
        user_input_queue.put(universal_functions.parameters["Input"]["user_input"])
        # print("Current value for user_input field under parameters is : ",
        #       universal_functions.parameters["Input"]["user_input"])
        # print("Previous value for user_input field under parameters was : ",
        #       universal_functions.parameters["Input"]["previous_user_input"])
        # print("Current value for user_input_param field under parameters is : ",
        #       universal_functions.parameters["Input"]["user_input_param"])
        # print("Previous value for user_input field under parameters was : ",
        #       universal_functions.parameters["Input"]["previous_user_input_param"])

    master = tkinter.Tk()

    tkinter.Label(master, text="Command").grid(row=0)
    tkinter.Label(master, text="Parameter").grid(row=1)

    e1 = tkinter.Entry(master)
    e2 = tkinter.Entry(master)

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)

    tkinter.Button(master, text='Quit', command=master.quit).grid(row=3, column=0, pady=4)
    tkinter.Button(master, text='Submit', command=submit_entry_fields).grid(row=3, column=1, pady=4)

    b = brain_functions.Brain()

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
            visualizer.cortical_heatmap(IPU_vision.read_image(int(universal_functions.parameters["Input"]
                                                             ["user_input_param"]))[0], [])
        mnist_img = IPU_vision.mnist_img_fetcher(int(universal_functions.parameters["Input"]["user_input_param"]))
        process_3 = mp.Process(name='Seeing_MNIST_image', target=b.see_from_mnist,
                               args=(mnist_img, FCL_queue, event_queue))
        process_3.start()
        process_3.join()
        universal_functions.parameters["Input"]["user_input"] = ''
        return

    def process_read_char():
        process_4 = mp.Process(name='Reading input char',
                               target=brain_functions.Brain.read_char,
                               args=(universal_functions.parameters["Input"]["user_input_param"], FCL_queue))
        process_4.start()
        process_4.join()
        universal_functions.parameters["Input"]["user_input"] = ''
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
            #           universal_functions.parameters["Input"]["user_input"]_param != \
            # settings.Input.previous_user_input_param:
            # print(">>>>>>   >>>>>>>   >>>>>   >>>>>  >>  >>  --\__/--  <<  <<    <<<<<<",
            # universal_functions.parameters["Input"]["user_input"], settings.Input.previous_user_input)
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

                # elif universal_functions.parameters["Input"]["user_input"] == 'a':
                #     # auto_pilot.auto_train(FCL_queue, event_queue)
                #     universal_functions.parameters["Switches"]["auto_train"] = True
                #     universal_functions.parameters["Input"]["user_input"] = ''

                elif universal_functions.parameters["Input"]["user_input"] == 't':
                    auto_pilot.auto_test(FCL_queue, event_queue)
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
# todo: Neuron finder is too inefficient
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

# Auto training
# todo: Compare results if you randomly show different variation of the same number vs one at a time
