

"""
This file contains the main Brain control code
"""

__author__ = 'Mohammad Nadji-tehrani'


if __name__ == '__main__':
    from datetime import datetime
    import tkinter
    import sys
    from time import sleep
    import multiprocessing as mp
    from misc import disk_ops
    disk_ops.load_parameters_in_memory()
    from misc import disk_ops
    from configuration import runtime_data, settings
    from evolutionary.genethesizer import genome_id_gen

    try:
        connectome_file_path = sys.argv[1]
        if connectome_file_path:
            runtime_data.parameters["InitData"]["connectome_path"] = connectome_file_path
            print("Connectome path is:", connectome_file_path)
    except IndexError or NameError:
        print("Default connectome path has been selected")

    global connectome_path
    connectome_path = runtime_data.parameters["InitData"]["connectome_path"]

    def regeneration_check():
        # Calling function to regenerate the Brain from the Genome
        if runtime_data.parameters["InitData"]["regenerate_brain"]:
            print("use_static_genome:", runtime_data.parameters["Switches"]["use_static_genome"])
            if runtime_data.parameters["Switches"]["use_static_genome"]:
                print("** ** ** ** ** ** ** ** **")
                disk_ops.load_genome_in_memory(connectome_path, static=True)
                print(settings.Bcolors.RED + ">> >> >> A static genome was used to generate the brain."
                      + settings.Bcolors.ENDC)
                runtime_data.parameters["Switches"]["use_static_genome"] = False
            else:
                disk_ops.stage_genome(connectome_path)
                disk_ops.load_genome_in_memory(connectome_path)

        else:
            disk_ops.stage_genome(connectome_path)
            disk_ops.load_genome_in_memory(connectome_path)


    regeneration_check()
    # disk_ops.stage_genome(connectome_path)
    # disk_ops.load_genome_in_memory(connectome_path)

    # Initialize runtime cortical list
    blueprint = runtime_data.genome["blueprint"]
    cortical_list = []
    for key in blueprint:
        cortical_list.append(key)
    runtime_data.cortical_list = cortical_list

    from misc import brain_functions, neuron_functions
    from evolutionary.brain_gen import brain_gen
    from evolutionary.architect import event_id_gen

    mp.set_start_method('spawn')

    if not runtime_data.parameters["Switches"]["live_mode"]:
        def submit_entry_fields():
            print("Command entered is: %s\nParameter is: %s" % (e1.get(), e2.get()))
            if runtime_data.parameters["Input"]["user_input"]:
                runtime_data.parameters["Input"]["previous_user_input"] = \
                    runtime_data.parameters["Input"]["user_input"]
            if runtime_data.parameters["Input"]["previous_user_input"]:
                runtime_data.parameters["Input"]["previous_user_input_param"] = \
                    runtime_data.parameters["Input"]["user_input_param"]
            runtime_data.parameters["Input"]["user_input"] = e1.get()
            runtime_data.parameters["Input"]["user_input_param"] = e2.get()
            user_input_queue.put(runtime_data.parameters["Input"]["user_input"])
            user_input_param_queue.put(runtime_data.parameters["Input"]["user_input_param"])

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

    def initialize_the_brain():
        global user_input_queue, user_input_param_queue, event_queue, \
            genome_test_stats, brain_queue, FCL_queue, genome_stats_queue, \
            parameters_queue, block_dic_queue, genome_id_queue
        # Initializing queues
        user_input_queue = mp.Queue()
        user_input_param_queue = mp.Queue()
        FCL_queue = mp.Queue()
        brain_queue = mp.Queue()
        event_queue = mp.Queue()
        genome_stats_queue = mp.Queue()
        genome_id_queue = mp.Queue()
        parameters_queue = mp.Queue()
        block_dic_queue = mp.Queue()

        # Initialize Fire Candidate List (FCL)
        FCL = []
        FCL_queue.put(FCL)

        # Setting up Brain queue for multiprocessing
        brain_data = disk_ops.load_brain_in_memory()
        runtime_data.brain = brain_data

        block_dic_data = disk_ops.load_block_dic_in_memory()
        brain_queue.put(brain_data)
        block_dic_queue.put(block_dic_data)

        # Setting up runtime_data.parameters queue for multiprocessing
        parameters_queue.put(runtime_data.parameters)

        # Setting up genome data
        genome_stats = {}
        genome_stats["test_stats"] = []
        genome_test_stats = []
        genome_stats_queue.put(genome_stats)
        genome_id_queue.put(genome_id_gen())

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
        runtime_data.parameters["Input"]["user_input"] = ''
        return


    if runtime_data.parameters["InitData"]["regenerate_brain"]:
        structural_fitness = 0
        while structural_fitness < 1:
            brain_generation_start_time = datetime.now()
            structural_fitness = brain_gen()
            brain_generation_duration = datetime.now() - brain_generation_start_time

        # todo: Move the following to stats module
        print("--------------------------------------------------------------")
        print("Brain generation lasted %s " % brain_generation_duration)
        print("--------------------------------------------------------------")
        print("Total Neuron count in Connectome is: ", b.connectome_neuron_count())
        print("--------------------------------------------------------------")
        print("Total Synapse count in Connectome is: ", b.connectome_synapse_count())
        print("--------------------------------------------------------------")

    initialize_the_brain()

    # Starting the burst machine
    # pool = mp.Pool(max(1, mp.cpu_count()))
    process_burst = mp.Pool(1, neuron_functions.burst, (user_input_queue, user_input_param_queue,
                                                        FCL_queue, brain_queue, event_queue,
                                                        genome_stats_queue, parameters_queue,
                                                        block_dic_queue, genome_id_queue,))
    print("The burst engine has been started...")

    event_id = event_id_gen()
    print(" <> ^^ <> ^^ <> ^^ <> ^^ <> An event related to mnist reading with following id has been logged:", event_id)
    event_queue.put(event_id)

    process_burst.deamon = False

    if not runtime_data.parameters["Switches"]["live_mode"]:
        read_user_input()

    # todo: implement the following using multiprocessing
    if runtime_data.parameters["Switches"]["vis_show"]:
        from . import visualizer
        visualizer.main()

    regenerate = True

    while regenerate:
        if not runtime_data.parameters["Switches"]["live_mode"]:
            regenerate = False
        try:
            while runtime_data.parameters["Input"]["user_input"] != 'q':
                # if runtime_data.parameters["Input"]["user_input"] != settings.Input.previous_user_input and \
                #           runtime_data.parameters["Input"]["user_input"]_param != \
                # settings.Input.previous_user_input_param:
                # print(">>>>>>   >>>>>>>   >>>>>   >>>>>  >>  >>  --\__/--  <<  <<    <<<<<<",
                # runtime_data.parameters["Input"]["user_input"], settings.Input.previous_user_input)
                try:
                    if runtime_data.parameters["Input"]["user_input"] == 'p':
                        process_print_basic_info()
                        runtime_data.parameters["Input"]["user_input"] = ''

                    # elif runtime_data.parameters["Input"]["user_input"] == 'live':
                    #     live()
                    #     runtime_data.parameters["Input"]["user_input"] = ''

                    else:
                        if runtime_data.parameters["Switches"]["live_mode"]:
                            runtime_data.parameters["Input"]["user_input"] = user_input_queue.get()
                        else:
                            read_user_input()
                        sleep(2)

                except IOError:
                    print("an error has occurred!!!")
                    pass

        finally:
            print("Finally!")
            runtime_data.brain = brain_queue.get()
            runtime_data.genome_id = genome_id_queue.get()
            print("*")
            runtime_data.block_dic = block_dic_queue.get()
            print("**")
            runtime_data.genome_test_stats = genome_stats_queue.get()
            print("***")
            join_processes()
            disk_ops.save_block_dic_to_disk(block_dic=runtime_data.block_dic,
                                            parameters=runtime_data.parameters, backup=True)
            print("****")
            disk_ops.save_brain_to_disk(brain=runtime_data.brain, parameters=runtime_data.parameters, backup=True)
            print("*****")
            print("genome id called from main function: ", runtime_data.genome_id)
            disk_ops.save_genome_to_disk()
            if runtime_data.parameters["Switches"]["live_mode"]:
                runtime_data.parameters["Input"]["user_input"] = ""
                print("Starting a new generation...")
                # Regenerate the brain
                disk_ops.stage_genome(connectome_path)
                print("$")
                disk_ops.load_genome_in_memory(connectome_path)
                print("$$")
                structural_fitness = 0
                while structural_fitness < 1:
                    brain_generation_start_time = datetime.now()
                    print("$$$")
                    runtime_data.block_dic = {}
                    structural_fitness = brain_gen()
                    print("$$$$")
                    brain_generation_duration = datetime.now() - brain_generation_start_time
                initialize_the_brain()
                print("$$$$$")

                # Starting the burst machine
                # pool = mp.Pool(max(1, mp.cpu_count()))
                process_burst = mp.Pool(1, neuron_functions.burst, (user_input_queue, user_input_param_queue,
                                                                    FCL_queue, brain_queue, event_queue,
                                                                    genome_stats_queue, parameters_queue,
                                                                    block_dic_queue, genome_id_queue,))
                print("The burst engine has been started...")

                event_id = event_id_gen()
                print(
                    " <> ^^ <> ^^ <> ^^ <> ^^ <> An event related to mnist reading with following id has been logged:",
                    event_id)
                event_queue.put(event_id)

                process_burst.deamon = False


#
#
#          <<<<<<<   T O   D O   L I S T   >>>>>>>>
#

# Key problem on hand
# todo: Need to reject bad genomes as soon as brain is generated and rebuild

# todo: only when the right portion of cell assembly is activated the rest shold become active
# todo: One number's visual memory is resembling all others
# todo: Neuron finder is too inefficient
# todo: Need a self tuning mechanism
# todo: find a way to measure layer level effectiveness metrics so it can be used for evolution

# Problems to fix
# todo: Synaptic activities in Memory everntually get to a point that does not ramp down
# todo: Event queue and events in general are not being used for any application or stored anywhere

# todo: Brain is being loaded in memory too regularly

# General Architecture - Anatomy
# todo: Add a generation age calculation to the main function
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
# todo: capture phenotype(connectome) highlights in database
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
# todo: Histogram of memory region activities when a single alphabet is trained

# Vision
# todo: Print visual memory to output in the form of pixels


# Speech
# todo: Make it learn to speak!


# Auto training
# todo: Compare results if you randomly show different variation of the same number vs one at a time


# Scalability
# todo: Explore services like Digital ocean, AWS, Spark, etc.
# todo: Figure how to manage running multiple instances of the brain on the same machine
