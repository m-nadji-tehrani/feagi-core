
"""
This Library contains various functions simulating human cortical behaviors
Function list:
neuron:           This function is triggered as a Neuron instance and stays up for period of time
                  till Neuron is fired
neuron_prop:      Returns the properties for a given neuron
neuron_neighbors: Reruns the list of neighbors for a given neuron
"""
# import multiprocessing as mp
# import subprocess
import os
import glob
import pickle
import json
from datetime import datetime
from collections import deque
from time import sleep
from PUs import OPU_utf8, IPU_utf8
from . import brain_functions
from misc import disk_ops
from configuration import settings, runtime_data
from PUs.IPU_vision import mnist_img_fetcher
from evolutionary.architect import test_id_gen, run_id_gen, synapse


class InitData:
    def __init__(self):
        self.genome_id = ""
        self.event_id = '_'
        self.blueprint = ""
        # self.rules = ""
        self.brain_is_running = False
        # live_mode_status can have modes of idle, learning, testing, tbd
        self.live_mode_status = 'idle'
        self.fcl_history = {}
        self.brain_run_id = ""
        self.burst_detection_list = {}
        self.burst_count = 0
        self.fire_candidate_list = []
        self.previous_fcl = []
        self.labeled_image = []
        self.training_neuron_list_utf = []
        self.training_neuron_list_img = []


class InjectorParams:
    def __init__(self):
        self.img_flag = False
        self.utf_flag = False
        self.injection_has_begun = False
        self.variation_handler = True
        self.exposure_handler = True
        self.utf_handler = True
        self.variation_counter = runtime_data.parameters["Auto_injector"]["variation_default"]
        self.exposure_counter = runtime_data.parameters["Auto_injector"]["exposure_default"]
        self.utf_counter = runtime_data.parameters["Auto_injector"]["utf_default"]
        self.variation_counter_actual = self.variation_counter
        self.exposure_counter_actual = self.exposure_counter
        self.utf_counter_actual = self.utf_counter
        self.injection_start_time = datetime.now()
        self.num_to_inject = ''
        self.utf_to_inject = ''
        self.injection_mode = ''


class TesterParams:
    def __init__(self):
        self.img_flag = False
        self.utf_flag = False
        self.testing_has_begun = False
        self.variation_handler = True
        self.exposure_handler = True
        self.utf_handler = True
        self.variation_counter = runtime_data.parameters["Auto_tester"]["variation_default"]
        self.exposure_counter = runtime_data.parameters["Auto_tester"]["exposure_default"]
        self.utf_counter = runtime_data.parameters["Auto_tester"]["utf_default"]
        self.variation_counter_actual = self.variation_counter
        self.exposure_counter_actual = self.exposure_counter
        self.utf_counter_actual = self.utf_counter
        self.test_start_time = datetime.now()
        self.num_to_inject = ''
        self.test_mode = ''
        self.comprehension_counter = 0
        self.test_attempt_counter = 0
        # self.temp_stats = []
        self.test_stats = {}
        self.test_id = ""


global init_data, injector_params, test_params


def burst(user_input, user_input_param, fire_list, brain_queue, event_queue,
          genome_stats_queue, parameters_queue, block_dic_queue):
    """This function behaves as instance of Neuronal activities"""
    # This function is triggered when another Neuron output targets the Neuron ID of another Neuron
    # which would start a timer since the first input is received and keep collecting inputs till
    # either the timeout is expired or the Firing threshold is met and neuron fires
    # Function Overview:
    #     This function receives a collection of inputs from multiple neurons, performs processing and generate a new
    #     output targeting other neurons which will be fed back to the same function for similar processing.
    # Initial trigger:
    #     This function can be initially called from the Input Processing Unit and will be recalled from within itself.
    # Function input contents:
    #     -List of Neurons which have fired
    # Function processing:
    #     -To Fire all the Neurons listed in the fire_candidate_list and update connectome accordingly
    #     -To do a check on all the recipients of the Fire and identify which is ready to fire and list them as output

    runtime_data.parameters = parameters_queue.get()
    disk_ops.load_genome_in_memory(runtime_data.parameters['InitData']['connectome_path'],
                                   static=runtime_data.parameters["Switches"]["use_static_genome"])

    # todo: Move comprehension span to genome
    comprehension_span = 1
    
    # Initializing the comprehension queue
    comprehension_queue = deque(['-'] * comprehension_span)

    global init_data, test_params, injector_params

    init_data = InitData()
    injector_params = InjectorParams()
    test_params = TesterParams()

    if not init_data.brain_is_running:
        toggle_brain_status()
        init_data.brain_run_id = run_id_gen()
        if runtime_data.parameters["Switches"]["capture_brain_activities"]:
            print(settings.Bcolors.HEADER + " *** Warning!!! *** Brain activities are being recorded!!" +
                  settings.Bcolors.ENDC)

    init_data.event_id = event_queue.get()
    runtime_data.brain = brain_queue.get()
    runtime_data.genome_stats = genome_stats_queue.get()
    runtime_data.block_dic = block_dic_queue.get()

    cortical_list = []
    for cortical_area in runtime_data.genome['blueprint']:
        cortical_list.append(cortical_area)
    runtime_data.cortical_list = cortical_list

    verbose = runtime_data.parameters["Switches"]["verbose"]

    if runtime_data.parameters["Switches"]["capture_brain_activities"]:
        init_data.fcl_history = {}

    DataFeeder()

    while not runtime_data.parameters["Switches"]["ready_to_exit_burst"]:
        burst_start_time = datetime.now()
        # print(datetime.now(), "Burst count = ", init_data.burst_count, file=open("./logs/burst.log", "a"))

        # List of Fire candidates are placed in global variable fire_candidate_list to be passed for next Burst

        # Read FCL from the Multiprocessing Queue
        init_data.fire_candidate_list = fire_list.get()
        init_data.previous_fcl = list(init_data.fire_candidate_list)
        init_data.burst_count += 1

        # Live mode condition
        if runtime_data.parameters["Switches"]["live_mode"] and init_data.live_mode_status == 'idle':
            init_data.live_mode_status = 'learning'
            print(settings.Bcolors.RED + "Starting an automated learning process...<> <> <> <>" + settings.Bcolors.ENDC)
            injection_manager(injection_mode="l1", injection_param="")

        # todo: Currently feeding a single random number n times. Add the ability to train variations of the same number
        # todo: create a number feeder

        # todo: need to break down the training function into peices with one feeding a streem of data
        if runtime_data.parameters["Auto_injector"]["injector_status"]:
            auto_injector()

        if runtime_data.parameters["Auto_tester"]["tester_status"]:
            auto_tester()

        # todo: The following is to have a check point to assess the perf of the in-use genome and make on the fly adj.
        # if init_data.burst_count % runtime_data.genome['evolution_burst_count'] == 0:
        #     print('Evolution phase reached...')
        #     genethesizer.generation_assessment()

        # Add a delay if fire_candidate_list is empty
        if len(init_data.fire_candidate_list) < 1:
            sleep(runtime_data.parameters["Timers"]["idle_burst_timer"])
            print("FCL is empty!")
        else:
            # brain_neuron_count, brain_synapse_count = stats.brain_total_synapse_cnt(verbose=False)
            # print(settings.Bcolors.YELLOW +
            #       'Burst count = %i  --  Neuron count in FCL is %i  -- Total brain synapse count is %i'
            #       % (init_data.burst_count, len(init_data.fire_candidate_list), brain_synapse_count) +
            # settings.Bcolors.ENDC)
            if runtime_data.parameters["Logs"]["print_cortical_activity_counters"]:
                for cortical_area in set([i[0] for i in init_data.fire_candidate_list]):
                    print(settings.Bcolors.YELLOW + '    %s : %i  '
                          % (cortical_area, len(set([i[1]
                                                     for i in init_data.fire_candidate_list if i[0] == cortical_area])))
                          + settings.Bcolors.ENDC)
                # for entry in init_data.fire_candidate_list:
                #     if runtime_data.genome['blueprint'][entry[0]]['group_id'] == 'Memory':
                #         print(settings.Bcolors.YELLOW + entry[0], entry[1] + settings.Bcolors.ENDC)
                    # if runtime_data.genome['blueprint'][cortical_area]['group_id'] == 'Memory' \
                    #         and len(set([i[1] for i in init_data.fire_candidate_list if i[0] == cortical_area])) > 0:
                    #     sleep(runtime_data.parameters["Timers"]["idle_burst_timer"])

            # todo: Look into multi-threading for Neuron neuron_fire and wire_neurons function
            # Firing all neurons in the Fire Candidate List

            for x in list(init_data.fire_candidate_list):
                if verbose:
                    print(settings.Bcolors.YELLOW + 'Firing Neuron: ' + x[1] + ' from ' + x[0] + settings.Bcolors.ENDC)
                neuron_fire(x[0], x[1])

            neuro_plasticity()
            if verbose:
                print(settings.Bcolors.YELLOW + 'Current fire_candidate_list is %s'
                      % init_data.fire_candidate_list + settings.Bcolors.ENDC)

        burst_duration = datetime.now() - burst_start_time
        if runtime_data.parameters["Logs"]["print_burst_info"]:
            print(">>> Burst duration: %s" % burst_duration)

        # Push back updated fire_candidate_list into FCL from Multiprocessing Queue
        fire_list.put(init_data.fire_candidate_list)

        detected_char = utf_detection_logic(init_data.burst_detection_list)
        comprehension_queue.append(detected_char)
        comprehension_queue.popleft()

        # Comprehension check
        counter_list = {}
        if runtime_data.parameters["Logs"]["print_comprehension_queue"]:
            if init_data.burst_detection_list != {}:
                print(settings.Bcolors.RED + "<><><><><><><><><><><><><><>"
                                             "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
                      + settings.Bcolors.ENDC)
            print(">>comprehension_queue  ", comprehension_queue, "  <<")

        for item in comprehension_queue:
            if item in counter_list:
                counter_list[item] += 1
            else:
                counter_list[item] = 1
        list_length = len(counter_list)

        if runtime_data.parameters["Logs"]["print_comprehension_queue"]:
            print("+++++++This is the counter list", counter_list)
        for item in counter_list:
            if list_length == 1 and item != '-':
                runtime_data.parameters["Input"]["comprehended_char"] = item[0]
                print(settings.Bcolors.HEADER + "UTF8 out was stimulated with the following character:    "
                                                "                     <<<     %s      >>>                 #*#*#*#*#*#*#"
                      % runtime_data.parameters["Input"]["comprehended_char"] + settings.Bcolors.ENDC)
            else:
                if list_length >= 2:
                    runtime_data.parameters["Input"]["comprehended_char"] = ''

        # Resetting burst detection list
        init_data.burst_detection_list = {}

        # todo: *** Danger *** The following section could cause considerable memory expansion. Need to add limitations.
        # Condition to save FCL data to disk
        user_input_processing(user_input, user_input_param)
        if runtime_data.parameters["Switches"]["capture_brain_activities"]:
            init_data.fcl_history[init_data.burst_count] = init_data.fire_candidate_list

        if runtime_data.parameters["Switches"]["save_fcl_to_disk"]:
            with open('./fcl_repo/fcl.json', 'w') as fcl_file:
                fcl_file.write(json.dumps(init_data.fire_candidate_list))
                fcl_file.truncate()
            sleep(0.5)

    # Push updated brain data back to the queue
    brain_queue.put(runtime_data.brain)
    block_dic_queue.put(runtime_data.block_dic)
    genome_stats_queue.put(runtime_data.genome_test_stats)
    if runtime_data.parameters["Switches"]["live_mode"]:
        user_input.put('q')


def utf_detection_logic(detection_list):
    # Identifies the detected UTF character with highest activity
    highest_ranked_item = '-'
    for item in detection_list:
        if highest_ranked_item == '-':
            highest_ranked_item = item
        else:
            if detection_list[item]['rank'] > detection_list[highest_ranked_item]['rank']:
                highest_ranked_item = item
    return highest_ranked_item

    # list_length = len(detection_list)
    # if list_length == 1:
    #     for key in detection_list:
    #         return key
    # elif list_length >= 2 or list_length == 0:
    #     return '-'
    # else:
    #     temp = []
    #     counter = 0
    #     # print(">><<>><<>><<", detection_list)
    #     for key in detection_list:
    #         temp[counter] = (key, detection_list[key])
    #     if temp[0][1] > (3 * temp[1][1]):
    #         return temp[0][0]
    #     elif temp[1][1] > (3 * temp[0][1]):
    #         return temp[1][0]
    #     else:
    #         return '-'

    # Load copy of all MNIST training images into mnist_data in form of an iterator. Each object has image label + image


def test_manager(test_mode, test_param):
    """
    This function has three modes t1, t2.
    Mode t1: Assist in learning numbers from 0 to 9
    Mode t2: Assist in learning variations of the same number
    """
    global test_params
    global init_data
    try:
        if test_mode == 't1':
            test_params.test_mode = "t1"
            print("Automatic learning for 0..9 has been turned ON!")
            test_params.img_flag = True
            test_params.utf_flag = True
            test_params.utf_handler = True
            test_params.variation_handler = True
            test_params.variation_counter = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.variation_counter_actual = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.utf_counter = runtime_data.parameters["Auto_tester"]["utf_default"]
            test_params.utf_counter_actual = runtime_data.parameters["Auto_tester"]["utf_default"]
            test_params.num_to_inject = test_params.utf_counter

        elif test_mode == 't2':
            test_params.test_mode = "t2"
            test_params.img_flag = True
            test_params.utf_flag = True
            test_params.utf_handler = False
            test_params.variation_handler = True
            test_params.variation_counter = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.variation_counter_actual = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.utf_counter = -1
            test_params.utf_counter_actual = -1
            test_params.num_to_inject = int(test_param)
            print("   <<<   Automatic learning for variations of number << %s >> has been turned ON!   >>>"
                  % test_param)

        else:
            print("Error detecting the test mode...")
            return

    finally:
        toggle_test_mode()
        test_params.test_id = test_id_gen()
        test_params.test_stats["genome_id"] = init_data.genome_id
        test_params.test_stats["test_id"] = test_params.test_id
        test_params.testing_has_begun = True


def auto_tester():
    """
    Test approach:

    - Ask user for number of times testing every digit call it x
    - Inject each number x rounds with each round conclusion being a "Comprehensions"
    - Count the number of True vs. False Comprehensions
    - Collect stats for each number and report at the end of testing

    """
    data_feeder = DataFeeder()
    global test_params
    if test_params.testing_has_begun:
        # Beginning of a injection process
        print("----------------------------------------Testing has begun------------------------------------")
        test_params.testing_has_begun = False
        test_params.test_start_time = datetime.now()
        if test_params.img_flag:
            data_feeder.image_feeder(test_params.num_to_inject)

    # Exposure counter
    test_params.exposure_counter_actual -= 1

    # print("Exposure counter actual: ", test_params.exposure_counter_actual)
    # print("Variation counter actual: ", test_params.variation_counter_actual,
    #       test_params.variation_handler)
    # print("UTF counter actual: ", test_params.utf_counter_actual, test_params.utf_handler)

    # Test stats
    update_test_stats()

    # Exit condition
    if test_exit_condition():
        test_exit_process()

    # Counter logic
    if test_params.variation_handler:
        if test_params.exposure_counter_actual < 1 and not test_exit_condition():
            test_params.exposure_counter_actual = test_params.exposure_counter
            test_params.test_attempt_counter += 1
            test_comprehension_logic()

            # Variation counter
            test_params.variation_counter_actual -= 1
            if test_params.img_flag:
                data_feeder.image_feeder(test_params.num_to_inject)

        if test_params.utf_handler \
                and test_params.variation_counter_actual < 0  \
                and not test_exit_condition():
                test_params.exposure_counter_actual = test_params.exposure_counter
                test_params.variation_counter_actual = test_params.variation_counter
                test_params.test_attempt_counter = 0
                test_params.comprehension_counter = 0
                # UTF counter
                test_params.utf_counter_actual -= 1
                if test_params.utf_flag:
                    test_params.num_to_inject -= 1

    # print(test_params.utf_counter,
    #       test_params.variation_counter,
    #       test_params.exposure_counter)
    #
    # print(test_params.utf_counter_actual,
    #       test_params.variation_counter_actual,
    #       test_params.exposure_counter_actual)

    if test_params.img_flag:
        data_feeder.img_neuron_list_feeder()


def update_test_stats():
    global test_params
    utf_exposed = str(test_params.num_to_inject) + '_exposed'
    utf_comprehended = str(test_params.num_to_inject) + '_comprehended'

    if utf_exposed not in test_params.test_stats:
        test_params.test_stats[utf_exposed] = 1

    if utf_comprehended not in test_params.test_stats:
        test_params.test_stats[utf_exposed] = 0

    test_params.test_stats[utf_exposed] = test_params.test_attempt_counter
    test_params.test_stats[utf_comprehended] = test_params.comprehension_counter


def test_comprehension_logic():
    global test_params
    # Comprehension logic
    print("> ", runtime_data.parameters["Input"]["comprehended_char"], "> ", test_params.num_to_inject)
    if runtime_data.parameters["Input"]["comprehended_char"] == str(test_params.num_to_inject):
        print(settings.Bcolors.HEADER +
              "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
              + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              ">> >> >>                                                   << << <<"
              + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              ">> >> >> The Brain successfully identified the image as > %s < !!!!"
              % runtime_data.parameters["Input"]["comprehended_char"] + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              ">> >> >>                                                   << << <<"
              + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
              + settings.Bcolors.ENDC)
        test_params.comprehension_counter += 1
        runtime_data.parameters["Input"]["comprehended_char"] = ''


def test_exit_condition():
    global test_params
    if test_params.utf_counter_actual < 1 and \
            test_params.variation_counter_actual < 1 and \
            test_params.exposure_counter_actual < 1:
        exit_condition = True
        print(">> Test exit condition has been met <<")
    else:
        exit_condition = False

    return exit_condition


def test_exit_process():
    global test_params
    global init_data
    
    runtime_data.parameters["Auto_tester"]["tester_status"] = False
    test_params.exposure_counter_actual = runtime_data.parameters["Auto_tester"]["exposure_default"]
    test_params.variation_counter_actual = runtime_data.parameters["Auto_tester"]["variation_default"]
    test_params.utf_counter_actual = runtime_data.parameters["Auto_tester"]["utf_default"]
    test_duration = datetime.now() - test_params.test_start_time
    print("----------------------------All testing rounds has been completed-----------------------------")
    print("Total test duration was: ", test_duration)
    print("-----------------------------------------------------------------------------------------------")
    print("Test statistics are as follows:\n")
    for test in test_params.test_stats:
        print(test, "\n", test_params.test_stats[test])
    print("-----------------------------------------------------------------------------------------------")

    test_params.test_attempt_counter = 0
    test_params.comprehension_counter = 0
    # logging stats into Genome
    runtime_data.genome_test_stats.append(test_params.test_stats.copy())
    test_params.test_stats = {}
    if runtime_data.parameters["Switches"]["live_mode"] and init_data.live_mode_status == 'testing':
        init_data.live_mode_status = 'idle'
        print(settings.Bcolors.RED + "Burst exit triggered by the automated workflow >< >< >< >< >< " +
              settings.Bcolors.ENDC)
        burst_exit_process()


def injection_manager(injection_mode, injection_param):
    """
    This function has three modes l1, l2, r and c.
    Mode l1: Assist in learning numbers from 0 to 9
    Mode l2: Assist in learning variations of the same number
    Mode r: Assist in exposing a single image to the brain for a number of bursts
    Mode c: Assist in exposing a single utf8 char to the brain for a number of bursts
    """
    global injector_params
    try:
        if injection_mode == 'l1':
            injector_params.injection_mode = "l1"
            print("Automatic learning for 0..9 has been turned ON!")
            injector_params.img_flag = True
            injector_params.utf_flag = True
            injector_params.utf_handler = True
            injector_params.variation_handler = True
            injector_params.variation_counter = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.variation_counter_actual = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.utf_counter = runtime_data.parameters["Auto_injector"]["utf_default"]
            injector_params.utf_counter_actual = runtime_data.parameters["Auto_injector"]["utf_default"]
            injector_params.num_to_inject = injector_params.utf_counter

        elif injection_mode == 'l2':
            injector_params.injection_mode = "l2"
            injector_params.img_flag = True
            injector_params.utf_flag = True
            injector_params.utf_handler = False
            injector_params.variation_handler = True
            injector_params.variation_counter = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.variation_counter_actual = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.utf_counter = 1
            injector_params.utf_counter_actual = 1
            injector_params.num_to_inject = int(injection_param)
            print("   <<<   Automatic learning for variations of number << %s >> has been turned ON!   >>>"
                  % injection_param)

        elif injection_mode == 'r':
            injector_params.injection_mode = "r"
            injector_params.variation_handler = False
            injector_params.img_flag = True
            injector_params.utf_flag = False
            injector_params.variation_counter = 0
            injector_params.variation_counter_actual = 0
            injector_params.utf_counter = -1
            injector_params.utf_counter_actual = -1
            injector_params.num_to_inject = injection_param

        elif injection_mode == 'c':
            injector_params.injection_mode = "c"
            injector_params.variation_handler = False
            injector_params.utf_handler = False
            injector_params.img_flag = False
            injector_params.utf_flag = True
            injector_params.utf_to_inject = injection_param
            injector_params.variation_counter = 0
            injector_params.variation_counter_actual = 0
            injector_params.utf_counter = -1
            injector_params.utf_counter_actual = -1

        else:
            print("Error detecting the injection mode...")
            return

    finally:
        toggle_injection_mode()
        injector_params.injection_has_begun = True


def auto_injector():
    global injector_params
    data_feeder = DataFeeder()
    if injector_params.injection_has_begun:
        # Beginning of a injection process
        print("----------------------------------------Data injection has begun------------------------------------")
        injector_params.injection_has_begun = False
        injector_params.injection_start_time = datetime.now()
        if injector_params.img_flag:
            data_feeder.image_feeder(injector_params.num_to_inject)

    # print("Exposure, Variation, and UTF counters actual values are: ",
    #       injector_params.exposure_counter_actual,
    #       injector_params.variation_counter_actual,
    #       injector_params.utf_counter_actual)

    # Exposure counter
    injector_params.exposure_counter_actual -= 1

    # print("Exposure counter actual: ", injector_params.exposure_counter_actual)
    # print("Variation counter actual: ", injector_params.variation_counter_actual,
    #       injector_params.variation_handler)
    # print("UTF counter actual: ", injector_params.utf_counter_actual, injector_params.utf_handler)

    # Exit condition
    if injection_exit_condition():
        injection_exit_process()

    # Counter logic
    if injector_params.variation_handler:
        if injector_params.exposure_counter_actual < 1 and not injection_exit_condition():
            injector_params.exposure_counter_actual = injector_params.exposure_counter
            # Variation counter
            injector_params.variation_counter_actual -= 1
            if injector_params.img_flag:
                data_feeder.image_feeder(injector_params.num_to_inject)
        if injector_params.utf_handler \
                and injector_params.variation_counter_actual < 0  \
                and not injection_exit_condition():
                injector_params.exposure_counter_actual = injector_params.exposure_counter
                injector_params.variation_counter_actual = injector_params.variation_counter
                # UTF counter
                injector_params.utf_counter_actual -= 1
                if injector_params.utf_flag:
                    injector_params.num_to_inject -= 1

    if injector_params.img_flag:
        data_feeder.img_neuron_list_feeder()
    if injector_params.utf_flag:
        data_feeder.utf8_feeder()


def injection_exit_condition():
    global injector_params
    if (injector_params.utf_handler and
        injector_params.utf_counter_actual < 1 and
        injector_params.variation_counter_actual < 1 and
        injector_params.exposure_counter_actual < 1) or \
            (not injector_params.utf_handler and
             injector_params.variation_handler and
             injector_params.variation_counter_actual < 1 and
             injector_params.exposure_counter_actual < 1) or \
            (not injector_params.utf_handler and
             not injector_params.variation_handler and
             injector_params.exposure_counter_actual < 1):
        exit_condition = True
        print(">> Injection exit condition has been met <<")
    else:
        exit_condition = False
    return exit_condition


def injection_exit_process():
    global init_data
    global injector_params
    runtime_data.parameters["Auto_injector"]["injector_status"] = False
    injector_params.exposure_counter_actual = runtime_data.parameters["Auto_injector"]["exposure_default"]
    injector_params.variation_counter_actual = runtime_data.parameters["Auto_injector"]["variation_default"]
    injector_params.utf_counter_actual = runtime_data.parameters["Auto_injector"]["utf_default"]
    injection_duration = datetime.now() - injector_params.injection_start_time
    print("----------------------------All injection rounds has been completed-----------------------------")
    print("Total injection duration was: ", injection_duration)
    print("-----------------------------------------------------------------------------------------------")
    if runtime_data.parameters["Switches"]["live_mode"] and init_data.live_mode_status == 'learning':
        init_data.live_mode_status = 'testing'
        print(settings.Bcolors.RED + "Starting automated testing process XXX XXX XXX XXX XXX" +
              settings.Bcolors.ENDC)
        test_manager(test_mode="t1", test_param="")


class DataFeeder:
    @staticmethod
    def utf8_feeder():
        global init_data
        global injector_params
        # inject label to FCL

        if injector_params.injection_mode == 'c':
            init_data.training_neuron_list_utf = IPU_utf8.convert_char_to_fire_list(injector_params.utf_to_inject)
        else:
            init_data.training_neuron_list_utf = IPU_utf8.convert_char_to_fire_list(str(init_data.labeled_image[1]))
        init_data.fire_candidate_list = inject_to_fcl(init_data.training_neuron_list_utf, init_data.fire_candidate_list)
        # print("Activities caused by image label are now part of the FCL")

    @staticmethod
    def img_neuron_list_feeder():
        global init_data
        # inject neuron activity to FCL
        init_data.fire_candidate_list = inject_to_fcl(init_data.training_neuron_list_img, init_data.fire_candidate_list)
        # print("Activities caused by image are now part of the FCL")

    @staticmethod
    def image_feeder(num):
        global init_data
        brain = brain_functions.Brain()
        if int(num) < 0 or num == '':
            num = 0
            print(settings.Bcolors.RED + "Error: image feeder has been fed a Null or less than 0 number" +
                  settings.Bcolors.ENDC)
        init_data.labeled_image = mnist_img_fetcher(num)
        # Convert image to neuron activity
        init_data.training_neuron_list_img = brain.retina(init_data.labeled_image)
        # print("image has been converted to neuronal activities...")


def neuro_plasticity():
    # The following handles neuro-plasticity
    global init_data
    if runtime_data.parameters["Switches"]["plasticity"]:
        # Plasticity between T1 and Vision memory
        # todo: generalize this function
        # Long Term Potentiation (LTP) between vision_IT and vision_memory
        for src_neuron in init_data.previous_fcl:
            if src_neuron[0] == "vision_IT":
                for dst_neuron in init_data.fire_candidate_list:
                    if dst_neuron[0] == "vision_memory" and dst_neuron[1] \
                            in runtime_data.brain["vision_IT"][src_neuron[1]]["neighbors"]:
                        apply_plasticity_ext(src_cortical_area='vision_IT', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='vision_memory', dst_neuron_id=dst_neuron[1])
                        if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                            print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWMWMWM"
                                                         "...........LTP between vision_IT and vision_memory occurred "
                                  + settings.Bcolors.ENDC)

        # Long Term Depression (LTD) between vision_IT and vision_memory
        for src_neuron in init_data.fire_candidate_list:
            if src_neuron[0] == "vision_IT":
                for dst_neuron in init_data.previous_fcl:
                    if dst_neuron[0] == "vision_memory" and dst_neuron[1] \
                            in runtime_data.brain["vision_IT"][src_neuron[1]]["neighbors"]:
                        apply_plasticity_ext(src_cortical_area='vision_IT', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='vision_memory', dst_neuron_id=dst_neuron[1],
                                             long_term_depression=True)
                        if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                            print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWM"
                                                         "...........LTD between vision_IT and vision_memory occurred "
                                  + settings.Bcolors.ENDC)

        # todo: The following loop is very inefficient___ fix it!!
        # todo: Read the following memory list from Genome
        memory_list = cortical_group_members('Memory')
        # memory_list = ['utf8_memory', 'vision_memory']

        # Building a bidirectional synapse between memory neurons who fire together within a cortical area
        for cortical_area in memory_list:
            if runtime_data.genome['blueprint'][cortical_area]['location_generation_type'] == 'random':
                for src_neuron in set([i[1] for i in init_data.fire_candidate_list if i[0] == cortical_area]):
                    for dst_neuron in set([j[1] for j in init_data.fire_candidate_list if j[0] == cortical_area]):
                        if src_neuron != dst_neuron:
                            apply_plasticity(cortical_area=cortical_area,
                                             src_neuron=src_neuron, dst_neuron=dst_neuron)

        # Wiring Vision memory to UIF-8 memory
        for dst_neuron in init_data.fire_candidate_list:
            if dst_neuron[0] == "utf8_memory":
                for src_neuron in init_data.previous_fcl:
                    if src_neuron[0] == "vision_memory":
                        apply_plasticity_ext(src_cortical_area='vision_memory', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='utf8_memory', dst_neuron_id=dst_neuron[1])

                        if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                            print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWM"
                                                         "..........LTP between vision_memory and UTF8_memory occurred "
                                  + settings.Bcolors.ENDC)
                            print(init_data.fire_candidate_list)
                            print("*************________**************")

                        # print(
                        #     settings.Bcolors.OKGREEN + "............................................................."
                        #                                "........A new memory was formed against utf8_memory location "
                        #     + OPU_utf8.convert_neuron_acticity_to_utf8_char('utf8_memory',
                        #                                                     dst_neuron[1]) + settings.Bcolors.ENDC)
                        # dst_neuron_id_list = neighbor_finder_ext('utf8_memory', 'utf8_out', _[1], 'rule_3', 0)
                        # for dst_neuron_id in dst_neuron_id_list:
                        #     wire_neurons_together_ext(src_cortical_area='vision_memory', src_neuron=neuron[1],
                        #                               dst_cortical_area='utf8_out', dst_neuron=dst_neuron_id)

        # Counting number of active UTF8_memory cells in the fire_candidate_list
        utf_mem_in_fcl = 0
        for neuron in init_data.fire_candidate_list:
            if neuron[0] == 'utf8_memory':
                utf_mem_in_fcl += 1

        # Reducing synaptic strength when one vision memory cell activates more than one UTF cell
        if utf_mem_in_fcl >= 2:
            for src_neuron in set([i[1] for i in init_data.previous_fcl if i[0] == 'vision_memory']):
                synapse_to_utf = 0
                dst_neuron_list = []
                for synapse in runtime_data.brain['vision_memory'][src_neuron]['neighbors']:
                    if runtime_data.brain['vision_memory'][src_neuron]['neighbors'][synapse]['cortical_area'] \
                            == 'utf8_memory':
                        synapse_to_utf += 1
                        dst_neuron_list.append(synapse)
                    if synapse_to_utf >= 2:
                        for dst_neuron in dst_neuron_list:
                            apply_plasticity_ext(src_cortical_area='vision_memory', src_neuron_id=src_neuron,
                                                 dst_cortical_area='utf8_memory', dst_neuron_id=dst_neuron,
                                                 long_term_depression=True)
                            if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                                print(
                                    settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWM  > 2 UTF detected MWMWMWWMWMWMWMWMWMWM"
                                                           "........LTD between vision_memory and UTF8_memory occurred "
                                    + settings.Bcolors.ENDC)


def burst_exit_process():
    print(settings.Bcolors.YELLOW + '>>>Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
    global init_data
    init_data.burst_count = 0
    runtime_data.parameters["Switches"]["ready_to_exit_burst"] = True
    if runtime_data.parameters["Switches"]["capture_brain_activities"]:
        save_fcl_to_disk()


def user_input_processing(user_input, user_input_param):
    while not user_input.empty():
        try:
            user_input_value = user_input.get()
            user_input_value_param = user_input_param.get()

            print("User input value is ", user_input_value)
            print("User input param is ", user_input_value_param)

            if user_input_value == 'x':
                burst_exit_process()

            elif user_input_value == 'v':
                toggle_verbose_mode()

            # elif user_input_value == 'g':
            #     toggle_visualization_mode()

            elif user_input_value in ['l1', 'l2', 'r', 'c']:
                injection_manager(injection_mode=user_input_value, injection_param=user_input_value_param)

            elif user_input_value in ['t1', 't2']:
                test_manager(test_mode=user_input_value, test_param=user_input_value_param)

        finally:
            runtime_data.parameters["Input"]["user_input"] = ''
            runtime_data.parameters["Input"]["user_input_param"] = ''
            break


#  >>>>>> Review this function against what we had in past
def fire_candidate_locations(fire_cnd_list):
    """Extracts Neuron locations from the fire_candidate_list"""

    # print('***')
    # print(fire_cnd_list)

    neuron_locations = {}
    # Generate a dictionary of cortical areas in the fire_candidate_list
    for item in runtime_data.cortical_list:
        neuron_locations[item] = []

    # Add neuron locations under each cortical area
    for item in fire_cnd_list:
        neuron_locations[item[0]].append([runtime_data.brain[item[0]][item[1]]["location"][0],
                                         runtime_data.brain[item[0]][item[1]]["location"][1],
                                         runtime_data.brain[item[0]][item[1]]["location"][2]])

    return neuron_locations


def neuron_fire(cortical_area, neuron_id):
    """This function initiate the firing of Neuron in a given cortical area"""
    global init_data
    # if runtime_data.parameters["Switches"]["logging_fire"]:
    #     print(datetime.now(), " Firing...", cortical_area, neuron_id, file=open("./logs/fire.log", "a"))

    # Setting Destination to the list of Neurons connected to the firing Neuron
    neighbor_list = runtime_data.brain[cortical_area][neuron_id]["neighbors"]

    # print("<><><>________<><><><>_______<><><><><>", cortical_area, neuron_id, neighbor_list)
    # print("Neighbor list:", neighbor_list)
    # if runtime_data.parameters["Switches"]["logging_fire"]:
    #     print(datetime.now(), "      Neighbors...", neighbor_list, file=open("./logs/fire.log", "a"))
    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_fire"]:
    #     print(settings.Bcolors.RED +
    #           "Firing neuron %s using firing pattern %s" %
    #           (neuron_id, json.dumps(runtime_data.brain[cortical_area][neuron_id]["firing_pattern_id"], indent=3)) +
    #           settings.Bcolors.ENDC)
    #     print(settings.Bcolors.RED + "Neuron %s neighbors are %s" % (neuron_id, json.dumps(neighbor_list, indent=3)) +
    #           settings.Bcolors.ENDC)

    # Condition to update neuron activity history currently only targeted for UTF-OPU
    # todo: move activity_history_span to genome
    activity_history_span = 4
    if cortical_area == 'utf8_memory':
        if not runtime_data.brain[cortical_area][neuron_id]["activity_history"]:
            zeros = deque([0] * activity_history_span)
            tmp_burst_list = []
            tmp_burst_count = init_data.burst_count
            for _ in range(activity_history_span):
                tmp_burst_list.append(tmp_burst_count)
                tmp_burst_count -= 1
            runtime_data.brain[cortical_area][neuron_id]["activity_history"] = deque(list(zip(tmp_burst_list, zeros)))
        else:
            runtime_data.brain[cortical_area][neuron_id]["activity_history"].append([init_data.burst_count,
                                                                                     runtime_data.brain[cortical_area]
                                                                                    [neuron_id]["membrane_potential"]])
            runtime_data.brain[cortical_area][neuron_id]["activity_history"].popleft()

    # After neuron fires all cumulative counters on Source gets reset
    runtime_data.brain[cortical_area][neuron_id]["membrane_potential"] = 0
    runtime_data.brain[cortical_area][neuron_id]["last_membrane_potential_reset_burst"] = init_data.burst_count
    # runtime_data.brain[cortical_area][neuron_id]["last_membrane_potential_reset_time"] = str(datetime.now())
    runtime_data.brain[cortical_area][neuron_id]["cumulative_fire_count"] += 1
    runtime_data.brain[cortical_area][neuron_id]["cumulative_fire_count_inst"] += 1

    # Transferring the signal from firing Neuron's Axon to all connected Neuron Dendrites
    # Firing pattern to be accommodated here     <<<<<<<<<<  *****
    # neuron_update_list = []
    neighbor_count = len(neighbor_list)
    for dst_neuron_id in neighbor_list:
        if runtime_data.parameters["Verbose"]["neuron_functions-neuron_fire"]:
            print(settings.Bcolors.RED + 'Updating connectome for Neuron ' + dst_neuron_id + settings.Bcolors.ENDC)
        dst_cortical_area = runtime_data.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["cortical_area"]
        # print(".......................", dst_cortical_area, dst_neuron_id)
        neuron_update(dst_cortical_area, dst_neuron_id,
                      runtime_data.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"],
                      neighbor_count)

    # Condition to snooze the neuron if consecutive fire count reaches threshold
    if runtime_data.brain[cortical_area][neuron_id]["consecutive_fire_cnt"] > \
            runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["consecutive_fire_cnt_max"]:
        snooze_till(cortical_area, neuron_id, init_data.burst_count +
                    runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"])

    # Condition to increase the consecutive fire count
    if init_data.burst_count == runtime_data.brain[cortical_area][neuron_id]["last_burst_num"] + 1:
        runtime_data.brain[cortical_area][neuron_id]["consecutive_fire_cnt"] += 1

    # todo: rename last_burst_num to last_firing_burst
    runtime_data.brain[cortical_area][neuron_id]["last_burst_num"] = init_data.burst_count

    # Condition to translate activity in utf8_out region as a character comprehension
    if cortical_area == 'utf8_memory':
        detected_item, activity_rank = OPU_utf8.convert_neuron_acticity_to_utf8_char(cortical_area, neuron_id)
        if detected_item not in init_data.burst_detection_list:
            init_data.burst_detection_list[detected_item] = {}
            init_data.burst_detection_list[detected_item]['count'] = 1
        else:
            init_data.burst_detection_list[detected_item]['count'] += 1
        init_data.burst_detection_list[detected_item]['rank'] = activity_rank

    init_data.fire_candidate_list.pop(init_data.fire_candidate_list.index([cortical_area, neuron_id]))
    # print("FCL after fire pop: ", len(init_data.fire_candidate_list))
    # np.delete(init_data.fire_candidate_list, init_data.fire_candidate_list.index([cortical_area, neuron_id]))
    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_fire"]:
    #     print(settings.Bcolors.RED + "Fire Function triggered FCL: %s "
    #           % init_data.fire_candidate_list + settings.Bcolors.ENDC)

    # todo: add a check that if the firing neuron is part of OPU to perform an action

    return


def neuron_update(cortical_area, dst_neuron_id, postsynaptic_current, neighbor_count):
    """This function updates the destination parameters upon upstream Neuron firing"""
    global init_data
    dst_neuron_obj = runtime_data.brain[cortical_area][dst_neuron_id]

    # update the cumulative_intake_total, cumulative_intake_count and postsynaptic_current between source and
    # destination neurons based on XXX algorithm. The source is considered the Axon of the firing neuron and
    # destination is the dendrite of the neighbor.

    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_update"]:
    #     print("Update request has been processed for: ", cortical_area, dst_neuron_id, " >>>>>>>> >>>>>>> >>>>>>>>>>")
    #     print(settings.Bcolors.UPDATE +
    #           "%s's Cumulative_intake_count value before update: %s" %
    #           (dst_neuron_id, dst_neuron_obj["membrane_potential"])
    #           + settings.Bcolors.ENDC)

    last_membrane_potential_update = \
        max(runtime_data.brain[cortical_area][dst_neuron_id]["last_membrane_potential_reset_burst"],
            runtime_data.brain[cortical_area][dst_neuron_id]["last_burst_num"])

    # Leaky behavior
    # todo: rename last_membrane_potential_reset_burst to last_membrane_potential_update
    if last_membrane_potential_update < init_data.burst_count:
        leak_coefficient = runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["leak_coefficient"]
        leak_value = (init_data.burst_count - last_membrane_potential_update) / leak_coefficient
        # print("::", cortical_area, "***", dst_neuron_id, "***", leak_value, "::")
        runtime_data.brain[cortical_area][dst_neuron_id]["membrane_potential"] -= leak_value
        if runtime_data.brain[cortical_area][dst_neuron_id]["membrane_potential"] < 0:
            runtime_data.brain[cortical_area][dst_neuron_id]["membrane_potential"] = 0

    # # To simulate a leaky neuron membrane, after x number of burst passing the membrane potential resets to zero
    # if init_data.burst_count - last_membrane_potential_update > \
    #         runtime_data.brain[cortical_area][dst_neuron_id]["depolarization_threshold"]:
    #     dst_neuron_obj["last_membrane_potential_reset_burst"] = init_data.burst_count
    #     # todo: Might be better to have a reset func.
    #     dst_neuron_obj["membrane_potential"] = 0
    #     if runtime_data.parameters["Verbose"]["neuron_functions-neuron_update"]:
    #         print(settings.Bcolors.UPDATE + 'Cumulative counters for Neuron ' + dst_neuron_id +
    #               ' got rest' + settings.Bcolors.ENDC)

    # Increasing the cumulative counter on destination based on the received signal from upstream Axon
    # The following is considered as LTP or Long Term Potentiation of Neurons
    # todo: remove next line as this is for testing only
    neighbor_count = 1

    runtime_data.brain[cortical_area][dst_neuron_id]["membrane_potential"] += (postsynaptic_current / neighbor_count)

    # print("membrane_potential:", destination,
    #       ":", runtime_data.brain[cortical_area][destination]["membrane_potential"])

    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_update"]:
    #     print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value after update: %s" %
    #           (dst_neuron_id, dst_neuron_obj["membrane_potential"])
    #           + settings.Bcolors.ENDC)

    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # todo: Need to figure how to deal with Activation function and firing threshold
    # The following will evaluate if the destination neuron is ready to fire and if so adds it to fire_candidate_list
    if dst_neuron_obj["membrane_potential"] > dst_neuron_obj["firing_threshold"]:
        # Refractory period check
        if dst_neuron_obj["last_burst_num"] + \
                runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["refractory_period"] <= \
                init_data.burst_count:
            # Inhibitory effect check
            if dst_neuron_obj["snooze_till_burst_num"] <= init_data.burst_count:
                # To prevent duplicate entries
                if init_data.fire_candidate_list.count([cortical_area, dst_neuron_id]) == 0:
                    init_data.fire_candidate_list.append([cortical_area, dst_neuron_id])
                    if runtime_data.parameters["Verbose"]["neuron_functions-neuron_update"]:
                        print(settings.Bcolors.UPDATE +
                              "    Update Function triggered FCL: %s " % init_data.fire_candidate_list
                              + settings.Bcolors.ENDC)

    # Resetting last time neuron was updated to the current burst id
    runtime_data.brain[cortical_area][dst_neuron_id]["last_burst_num"] = init_data.burst_count

    return init_data.fire_candidate_list


def neuron_prop(cortical_area, neuron_id):
    """This function accepts neuron id and returns neuron properties"""

    data = runtime_data.brain[cortical_area]

    if runtime_data.parameters["Switches"]["verbose"]:
        print('Listing Neuron Properties for %s:' % neuron_id)
        print(json.dumps(data[neuron_id], indent=3))
    return data[neuron_id]


def neuron_neighbors(cortical_area, neuron_id):
    """This function accepts neuron id and returns the list of Neuron neighbors"""

    data = runtime_data.brain[cortical_area]

    if runtime_data.parameters["Switches"]["verbose"]:
        print('Listing Neuron Neighbors for %s:' % neuron_id)
        print(json.dumps(data[neuron_id]["neighbors"], indent=3))
    return data[neuron_id]["neighbors"]


def apply_plasticity(cortical_area, src_neuron, dst_neuron):
    """
    This function simulates neuron plasticity in a sense that when neurons in a given cortical area fire in the 
     same burst they wire together. This is done by increasing the postsynaptic_current associated with a link between
     two neuron. Additionally an event id is associated to the neurons who have fired together.
    """
    global init_data
    genome = runtime_data.genome

    # Since this function only targets Memory regions and neurons in memory regions do not have neighbor relationship
    # by default hence here we first need to synapse the source and destination together
    # Build neighbor relationship between the source and destination if its not already in place

    # Check if source and destination have an existing synapse if not create one here
    if dst_neuron not in runtime_data.brain[cortical_area][src_neuron]["neighbors"]:
        synapse(cortical_area, src_neuron, cortical_area, dst_neuron,
                genome["blueprint"][cortical_area]["postsynaptic_current"])

    # Every time source and destination neuron is fired at the same time which in case of the code architecture
    # reside in the same burst, the postsynaptic_current will be increased simulating the fire together, wire together.
    # This phenomenon is also considered as long term potentiation or LTP
    runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"] += \
        genome["blueprint"][cortical_area]["plasticity_constant"]

    # Condition to cap the postsynaptic_current and provide prohibitory reaction
    runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"] = \
        min(runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"],
            genome["blueprint"][cortical_area]["postsynaptic_current_max"])

    # Append a Group ID so Memory clusters can be uniquely identified
    if init_data.event_id:
        if init_data.event_id in runtime_data.brain[cortical_area][src_neuron]["event_id"]:
            runtime_data.brain[cortical_area][src_neuron]["event_id"][init_data.event_id] += 1
        else:
            runtime_data.brain[cortical_area][src_neuron]["event_id"][init_data.event_id] = 1

    return


def apply_plasticity_ext(src_cortical_area, src_neuron_id, dst_cortical_area,
                         dst_neuron_id, long_term_depression=False):

    genome = runtime_data.genome
    plasticity_constant = genome["blueprint"][src_cortical_area]["plasticity_constant"]

    if long_term_depression:
        # When long term depression flag is set, there will be negative synaptic influence caused
        plasticity_constant = plasticity_constant * (-1)

    # Check if source and destination have an existing synapse if not create one here
    if dst_neuron_id not in runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"]:
        synapse(src_cortical_area, src_neuron_id, dst_cortical_area, dst_neuron_id, max(plasticity_constant, 0))

    runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"] += \
        genome["blueprint"][src_cortical_area]["plasticity_constant"]

    # Condition to cap the postsynaptic_current and provide prohibitory reaction
    runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"] = \
        min(runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"],
            genome["blueprint"][src_cortical_area]["postsynaptic_current_max"])

    return


def snooze_till(cortical_area, neuron_id, burst_id):
    """ Acting as an inhibitory neurotransmitter to suppress firing of neuron till a later burst

    *** This function instead of inhibitory behavior is more inline with Neuron Refractory period

    """
    runtime_data.brain[cortical_area][neuron_id]["snooze_till_burst_num"] \
        = burst_id + runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"]
    # print("%s : %s has been snoozed!" % (cortical_area, neuron_id))
    return


def inject_to_fcl(neuron_list, fcl):
    # print("Injecting to FCL.../\/\/\/")
    # print("Neuron list is: ", neuron_list)
    # Update FCL with new input data. FCL is read from the Queue and updated
    for item in neuron_list:
        fcl.append(item)
    # print("Injected to FCL.../\/\/\/")
    return fcl


def save_fcl_to_disk():
    global init_data
    with open("./fcl_repo/fcl-" + init_data.brain_run_id + ".json", 'w') as fcl_file:
        # Saving changes to the connectome
        fcl_file.seek(0)  # rewind
        fcl_file.write(json.dumps(init_data.fcl_history, indent=3))
        fcl_file.truncate()

    print("Brain activities has been preserved!")


def load_fcl_in_memory(file_name):
    with open(file_name, 'r') as fcl_file:
        fcl_data = json.load(fcl_file)
    return fcl_data


def latest_fcl_file():
    list_of_files = glob.glob('./fcl_repo/*.json')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def pickler(data):
    global init_data
    id_ = init_data.brain_run_id
    with open("./pickle_jar/fcl-" + id_ + ".pkl", 'wb') as output:
        pickle.dump(data, output)


def unpickler(data_type, id_):
    if data_type == 'fcl':
        with open("./pickle_jar/fcl-" + id_ + ".pkl", 'rb') as input_data:
            data = pickle.load(input_data)
            return data
    else:
        print("Error: Type not found!")


def toggle_verbose_mode():
    if runtime_data.parameters["Switches"]["verbose"]:
        runtime_data.parameters["Switches"]["verbose"] = False
        print("Verbose mode is Turned OFF!")
    else:
        runtime_data.parameters["Switches"]["verbose"] = True
        print("Verbose mode is Turned On!")


def toggle_injection_mode():
    if runtime_data.parameters["Auto_injector"]["injector_status"]:
        runtime_data.parameters["Auto_injector"]["injector_status"] = False
        print("Auto_train mode is Turned OFF!")
    else:
        runtime_data.parameters["Auto_injector"]["injector_status"] = True
        print("Auto_train mode is Turned On!")


def toggle_test_mode():
    if runtime_data.parameters["Auto_tester"]["tester_status"]:
        runtime_data.parameters["Auto_tester"]["tester_status"] = False
        print("Auto_test mode is Turned OFF!")
    else:
        runtime_data.parameters["Auto_tester"]["tester_status"] = True
        print("Auto_test mode is Turned On!")


def toggle_brain_status():
    global init_data
    if init_data.brain_is_running:
        init_data.brain_is_running = False
        print("Brain is not running!")
    else:
        init_data.brain_is_running = True
        print("Brain is now running!!!")


def cortical_group_members(group):
    members = []
    for item in runtime_data.cortical_list:
        if runtime_data.genome['blueprint'][item]['group_id'] == group:
            members.append(item)
    return members


def reset_cumulative_counter_instances():
    """
    To reset the cumulative counter instances
    """
    for cortical_area in runtime_data.brain:
        for neuron in runtime_data.brain[cortical_area]:
            runtime_data.brain[cortical_area][neuron]['cumulative_fire_count_inst'] = 0
    return
