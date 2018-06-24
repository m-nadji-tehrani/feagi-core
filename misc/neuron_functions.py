
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
import json
import datetime
from time import sleep
from architect import synapse, event_id_gen
from PUs import OPU_utf8
import genethesizer
from PUs import IPU_utf8
import brain_functions
from configuration import settings
from misc import universal_functions as uf, stats
from IPU_vision import mnist_img_fetcher
from architect import test_id_gen, run_id_gen


global burst_count
burst_count = 0


def burst(user_input, user_input_param, fire_list, brain_queue, event_queue, genome_stats_queue):
    """This function behaves as instance of Neuronal activities"""
    # This function is triggered when another Neuron output targets the Neuron ID of another Neuron
    # which would start a timer since the first input is received and keep collecting inputs till
    # either the timeout is expired or the Firing threshold is met and neuron Fires

    # todo: Consider to have burst instances so multiple burst can happen simultaneously: No need just update FLC!!!
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

    if not uf.brain_is_running:
        uf.toggle_brain_status()
        uf.brain_run_id = run_id_gen()
        if uf.parameters["Switches"]["capture_brain_activities"]:
            print(settings.Bcolors.HEADER + " *** Warning!!! *** Brain activities are being recorded!!" +
                  settings.Bcolors.ENDC)

    uf.event_id = event_queue.get()
    uf.brain = brain_queue.get()
    uf.genome_stats = genome_stats_queue.get()
    # my_brain = uf.brain
    verbose = uf.parameters["Switches"]["verbose"]

    while not uf.parameters["Switches"]["ready_to_exit_burst"]:
        burst_start_time = datetime.datetime.now()
        global burst_count

        # print(datetime.datetime.now(), "Burst count = ", burst_count, file=open("./logs/burst.log", "a"))

        # List of Fire candidates are placed in global variable fire_candidate_list to be passed for next Burst
        global fire_candidate_list
        global previous_fcl

        # Read FCL from the Multiprocessing Queue
        fire_candidate_list = fire_list.get()
        previous_fcl = list(fire_candidate_list)

        burst_count += 1

        # todo: Currently feeding a single random number n times. Add the ability to train variations of the same number
        # todo: create a number feeder

        # todo: need to break down the training function into peices with one feeding a streem of data
        if uf.parameters["Auto_injector"]["injector_status"]:
            auto_injector()

        if uf.parameters["Auto_tester"]["tester_status"]:
            auto_tester()

        # todo: The following is to have a check point to assess the perf of the in-use genome and make on the fly adj.
        if burst_count % uf.genome['evolution_burst_count'] == 0:
            print('Evolution phase reached...')
            genethesizer.generation_assessment()

        # Add a delay if fire_candidate_list is empty
        if len(fire_candidate_list) < 1:
            sleep(uf.parameters["Timers"]["idle_burst_timer"])
            print("FCL is empty!")
        else:
            if verbose:
                print(settings.Bcolors.YELLOW + 'Current fire_candidate_list is %s'
                      % fire_candidate_list + settings.Bcolors.ENDC)

            # brain_neuron_count, brain_synapse_count = stats.brain_total_synapse_cnt(verbose=False)
            # print(settings.Bcolors.YELLOW +
            #       'Burst count = %i  --  Neuron count in FCL is %i  -- Total brain synapse count is %i'
            #       % (burst_count, len(fire_candidate_list), brain_synapse_count) + settings.Bcolors.ENDC)

            for cortical_area in set([i[0] for i in fire_candidate_list]):
                print(settings.Bcolors.YELLOW + '    %s : %i  '
                      % (cortical_area, len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])))
                      + settings.Bcolors.ENDC)
            for entry in fire_candidate_list:
                if uf.genome['blueprint'][entry[0]]['group_id'] == 'Memory':
                    print(settings.Bcolors.YELLOW + entry[0], entry[1] + settings.Bcolors.ENDC)
                # if uf.genome['blueprint'][cortical_area]['group_id'] == 'Memory' \
                #         and len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])) > 0:
                #     sleep(uf.parameters["Timers"]["idle_burst_timer"])

            # todo: Look into multi-threading for Neuron neuron_fire and wire_neurons function
            # Firing all neurons in the Fire Candidate List
            for x in list(fire_candidate_list):
                if verbose:
                    print(settings.Bcolors.YELLOW + 'Firing Neuron: ' + x[1] + ' from ' + x[0] + settings.Bcolors.ENDC)
                neuron_fire(x[0], x[1])

            neuro_plasticity()

        burst_duration = datetime.datetime.now() - burst_start_time
        print(">>> Burst duration: %s" % burst_duration)

        # Push back updated fire_candidate_list into FCL from Multiprocessing Queue
        fire_list.put(fire_candidate_list)

        # todo: *** Danger *** The following section could cause considerable memory expansion. Need to add limitations.
        # Condition to save FCL data to disk
        user_input_processing(user_input, user_input_param)
        if uf.parameters["Switches"]["capture_brain_activities"]:
            uf.fcl_history[burst_count] = fire_candidate_list

        if uf.parameters["Switches"]["save_fcl_to_disk"]:
            with open('./fcl_repo/fcl.json', 'w') as fcl_file:
                fcl_file.write(json.dumps(fire_candidate_list))
                fcl_file.truncate()
            sleep(0.5)

    # Push updated brain data back to the queue
    brain_queue.put(uf.brain)
    genome_stats_queue.put(uf.genome_stats)


def test_manager(test_mode, test_param):
    """
    This function has three modes t1, t2.
    Mode t1: Assist in learning numbers from 0 to 9
    Mode t2: Assist in learning variations of the same number
    """
    try:
        if test_mode == 't1':
            uf.TesterParams.test_mode = "t1"
            print("Automatic learning for 0..9 has been turned ON!")
            uf.TesterParams.img_flag = True
            uf.TesterParams.utf_flag = True
            uf.TesterParams.utf_handler = True
            uf.TesterParams.variation_handler = True
            uf.TesterParams.variation_counter = uf.parameters["Auto_tester"]["variation_default"]
            uf.TesterParams.variation_counter_actual = uf.parameters["Auto_tester"]["variation_default"]
            uf.TesterParams.utf_counter = uf.parameters["Auto_tester"]["utf_default"]
            uf.TesterParams.utf_counter_actual = uf.parameters["Auto_tester"]["utf_default"]
            uf.TesterParams.num_to_inject = uf.TesterParams.utf_counter

        elif test_mode == 't2':
            uf.TesterParams.test_mode = "t2"
            uf.TesterParams.img_flag = True
            uf.TesterParams.utf_flag = True
            uf.TesterParams.utf_handler = False
            uf.TesterParams.variation_handler = True
            uf.TesterParams.variation_counter = uf.parameters["Auto_tester"]["variation_default"]
            uf.TesterParams.variation_counter_actual = uf.parameters["Auto_tester"]["variation_default"]
            uf.TesterParams.utf_counter = -1
            uf.TesterParams.utf_counter_actual = -1
            uf.TesterParams.num_to_inject = int(test_param)
            print("   <<<   Automatic learning for variations of number << %s >> has been turned ON!   >>>"
                  % test_param)

        else:
            print("Error detecting the test mode...")
            return

    finally:
        uf.toggle_test_mode()
        test_id = test_id_gen()
        uf.TesterParams.test_id = test_id
        num_list = []
        for _ in range(0, 10):
            num_list.append([_, 0, 0])
        uf.TesterParams.test_stats[test_id] = num_list
        uf.TesterParams.temp_stats = num_list

        uf.TesterParams.test_id = test_id_gen()
        uf.TesterParams.testing_has_begun = True


def auto_tester():
    """
    Test approach:

    - Ask user for number of times testing every digit call it x
    - Inject each number x rounds with each round conclusion being a "Comprehensions"
    - Count the number of True vs. False Comprehensions
    - Collect stats for each number and report at the end of testing

    """
    if uf.TesterParams.testing_has_begun:
        # Beginning of a injection process
        print("----------------------------------------Testing has begun------------------------------------")
        uf.TesterParams.testing_has_begun = False
        uf.TesterParams.test_start_time = datetime.datetime.now()
        if uf.TesterParams.img_flag:
            DataFeeder.image_feeder(uf.TesterParams.num_to_inject)

    # Exposure counter
    uf.TesterParams.exposure_counter_actual -= 1

    print("Exposure counter actual: ", uf.TesterParams.exposure_counter_actual)
    print("Variation counter actual: ", uf.TesterParams.variation_counter_actual,
          uf.TesterParams.variation_handler)
    print("UTF counter actual: ", uf.TesterParams.utf_counter_actual, uf.TesterParams.utf_handler)

    # Exit condition
    if test_exit_condition():
        test_exit_process()

    # Test stats
    uf.TesterParams.temp_stats[uf.TesterParams.num_to_inject] = [uf.TesterParams.num_to_inject,
                                                                 uf.TesterParams.test_attempt_counter,
                                                                 uf.TesterParams.comprehension_counter]

    # Counter logic
    if uf.TesterParams.variation_handler:
        if uf.TesterParams.exposure_counter_actual < 1 and not test_exit_condition():
            uf.TesterParams.exposure_counter_actual = uf.TesterParams.exposure_counter
            uf.TesterParams.test_attempt_counter += 1
            test_comprehension_logic()

            # Variation counter
            uf.TesterParams.variation_counter_actual -= 1
            if uf.TesterParams.img_flag:
                DataFeeder.image_feeder(uf.TesterParams.num_to_inject)

        if uf.TesterParams.utf_handler \
                and uf.TesterParams.variation_counter_actual < 0  \
                and not test_exit_condition():
                uf.TesterParams.exposure_counter_actual = uf.TesterParams.exposure_counter
                uf.TesterParams.variation_counter_actual = uf.TesterParams.variation_counter
                uf.TesterParams.test_attempt_counter = 0
                # UTF counter
                uf.TesterParams.utf_counter_actual -= 1
                if uf.TesterParams.utf_flag:
                    uf.TesterParams.num_to_inject -= 1

    print(uf.TesterParams.utf_counter,
          uf.TesterParams.variation_counter,
          uf.TesterParams.exposure_counter)

    print(uf.TesterParams.utf_counter_actual,
          uf.TesterParams.variation_counter_actual,
          uf.TesterParams.exposure_counter_actual)

    if uf.TesterParams.img_flag:
        DataFeeder.img_neuron_list_feeder()


def test_comprehension_logic():
    # Comprehension logic
    print("> ", uf.parameters["Input"]["comprehended_char"], "> ", uf.TesterParams.num_to_inject)
    if uf.parameters["Input"]["comprehended_char"] == str(uf.TesterParams.num_to_inject):
        print(settings.Bcolors.HEADER +
              "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
              + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              ">> >> >>                                                   << << <<"
              + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              ">> >> >> The Brain successfully identified the image as > %s < !!!!"
              % uf.parameters["Input"]["comprehended_char"] + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              ">> >> >>                                                   << << <<"
              + settings.Bcolors.ENDC)
        print(settings.Bcolors.HEADER +
              "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
              + settings.Bcolors.ENDC)
        uf.TesterParams.comprehension_counter += 1


def test_exit_condition():
    if uf.TesterParams.utf_counter_actual < 1 and \
            uf.TesterParams.variation_counter_actual < 1 and \
            uf.TesterParams.exposure_counter_actual < 1:
        exit_condition = True
        print(">> Test exit condition has been met <<")
    else:
        exit_condition = False

    return exit_condition


def test_exit_process():
    uf.parameters["Auto_tester"]["tester_status"] = False
    uf.TesterParams.exposure_counter_actual = uf.parameters["Auto_tester"]["exposure_default"]
    uf.TesterParams.variation_counter_actual = uf.parameters["Auto_tester"]["variation_default"]
    uf.TesterParams.utf_counter_actual = uf.parameters["Auto_tester"]["utf_default"]
    test_duration = datetime.datetime.now() - uf.TesterParams.test_start_time
    print("----------------------------All testing rounds has been completed-----------------------------")
    print("Total test duration was: ", test_duration)
    print("-----------------------------------------------------------------------------------------------")
    print("Test statistics are as follows:\n", uf.TesterParams.test_stats)
    print("-----------------------------------------------------------------------------------------------")
    uf.TesterParams.test_stats[uf.TesterParams.test_id] = uf.TesterParams.temp_stats
    uf.TesterParams.test_attempt_counter = 0
    uf.TesterParams.comprehension_counter = 0
    # logging stats into Genome
    uf.genome_stats["test_stats"] = uf.TesterParams.test_stats


def injection_manager(injection_mode, injection_param):
    """
    This function has three modes l1, l2, r and c.
    Mode l1: Assist in learning numbers from 0 to 9
    Mode l2: Assist in learning variations of the same number
    Mode r: Assist in exposing a single image to the brain for a number of bursts
    Mode c: Assist in exposing a single utf8 char to the brain for a number of bursts
    """
    try:
        if injection_mode == 'l1':
            uf.InjectorParams.injection_mode = "l1"
            print("Automatic learning for 0..9 has been turned ON!")
            uf.InjectorParams.img_flag = True
            uf.InjectorParams.utf_flag = True
            uf.InjectorParams.utf_handler = True
            uf.InjectorParams.variation_handler = True
            uf.InjectorParams.variation_counter = uf.parameters["Auto_injector"]["variation_default"]
            uf.InjectorParams.variation_counter_actual = uf.parameters["Auto_injector"]["variation_default"]
            uf.InjectorParams.utf_counter = uf.parameters["Auto_injector"]["utf_default"]
            uf.InjectorParams.utf_counter_actual = uf.parameters["Auto_injector"]["utf_default"]
            uf.InjectorParams.num_to_inject = uf.InjectorParams.utf_counter

        elif injection_mode == 'l2':
            uf.InjectorParams.injection_mode = "l2"
            uf.InjectorParams.img_flag = True
            uf.InjectorParams.utf_flag = True
            uf.InjectorParams.utf_handler = False
            uf.InjectorParams.variation_handler = True
            uf.InjectorParams.variation_counter = uf.parameters["Auto_injector"]["variation_default"]
            uf.InjectorParams.variation_counter_actual = uf.parameters["Auto_injector"]["variation_default"]
            uf.InjectorParams.utf_counter = 1
            uf.InjectorParams.utf_counter_actual = 1
            uf.InjectorParams.num_to_inject = int(injection_param)
            print("   <<<   Automatic learning for variations of number << %s >> has been turned ON!   >>>"
                  % injection_param)

        elif injection_mode == 'r':
            uf.InjectorParams.injection_mode = "r"
            uf.InjectorParams.variation_handler = False
            uf.InjectorParams.img_flag = True
            uf.InjectorParams.utf_flag = False
            uf.InjectorParams.variation_counter = 0
            uf.InjectorParams.variation_counter_actual = 0
            uf.InjectorParams.utf_counter = -1
            uf.InjectorParams.utf_counter_actual = -1
            uf.InjectorParams.num_to_inject = injection_param

        elif injection_mode == 'c':
            uf.InjectorParams.injection_mode = "c"
            uf.InjectorParams.variation_handler = False
            uf.InjectorParams.utf_handler = False
            uf.InjectorParams.img_flag = False
            uf.InjectorParams.utf_flag = True
            uf.InjectorParams.utf_to_inject = injection_param
            uf.InjectorParams.variation_counter = 0
            uf.InjectorParams.variation_counter_actual = 0
            uf.InjectorParams.utf_counter = -1
            uf.InjectorParams.utf_counter_actual = -1

        else:
            print("Error detecting the injection mode...")
            return

    finally:
        uf.toggle_injection_mode()
        uf.InjectorParams.injection_has_begun = True


def auto_injector():
    if uf.InjectorParams.injection_has_begun:
        # Beginning of a injection process
        print("----------------------------------------Data injection has begun------------------------------------")
        uf.InjectorParams.injection_has_begun = False
        uf.InjectorParams.injection_start_time = datetime.datetime.now()
        if uf.InjectorParams.img_flag:
            DataFeeder.image_feeder(uf.InjectorParams.num_to_inject)

    print("Exposure, Variation, and UTF counters actual values are: ",
          uf.InjectorParams.exposure_counter_actual,
          uf.InjectorParams.variation_counter_actual,
          uf.InjectorParams.utf_counter_actual)

    # Exposure counter
    uf.InjectorParams.exposure_counter_actual -= 1

    print("Exposure counter actual: ", uf.InjectorParams.exposure_counter_actual)
    print("Variation counter actual: ", uf.InjectorParams.variation_counter_actual,
          uf.InjectorParams.variation_handler)
    print("UTF counter actual: ", uf.InjectorParams.utf_counter_actual, uf.InjectorParams.utf_handler)

    # Exit condition
    if injection_exit_condition():
        injection_exit_process()

    # Counter logic
    if uf.InjectorParams.variation_handler:
        if uf.InjectorParams.exposure_counter_actual < 1 and not injection_exit_condition():
            uf.InjectorParams.exposure_counter_actual = uf.InjectorParams.exposure_counter
            # Variation counter
            uf.InjectorParams.variation_counter_actual -= 1
            if uf.InjectorParams.img_flag:
                DataFeeder.image_feeder(uf.InjectorParams.num_to_inject)
        if uf.InjectorParams.utf_handler \
                and uf.InjectorParams.variation_counter_actual < 0  \
                and not injection_exit_condition():
                uf.InjectorParams.exposure_counter_actual = uf.InjectorParams.exposure_counter
                uf.InjectorParams.variation_counter_actual = uf.InjectorParams.variation_counter
                # UTF counter
                uf.InjectorParams.utf_counter_actual -= 1
                if uf.InjectorParams.utf_flag:
                    uf.InjectorParams.num_to_inject -= 1

    if uf.InjectorParams.img_flag:
        DataFeeder.img_neuron_list_feeder()
    if uf.InjectorParams.utf_flag:
        DataFeeder.utf8_feeder()


def injection_exit_condition():
    if (uf.InjectorParams.utf_handler and
        uf.InjectorParams.utf_counter_actual < 1 and
        uf.InjectorParams.variation_counter_actual < 1 and
        uf.InjectorParams.exposure_counter_actual < 1) or \
            (not uf.InjectorParams.utf_handler and
             uf.InjectorParams.variation_handler and
             uf.InjectorParams.variation_counter_actual < 1 and
             uf.InjectorParams.exposure_counter_actual < 1) or \
            (not uf.InjectorParams.utf_handler and
             not uf.InjectorParams.variation_handler and
             uf.InjectorParams.exposure_counter_actual < 1):
        exit_condition = True
        print(">> Injection exit condition has been met <<")
    else:
        exit_condition = False
    return exit_condition


def injection_exit_process():
    uf.parameters["Auto_injector"]["injector_status"] = False
    uf.InjectorParams.exposure_counter_actual = uf.parameters["Auto_injector"]["exposure_default"]
    uf.InjectorParams.variation_counter_actual = uf.parameters["Auto_injector"]["variation_default"]
    uf.InjectorParams.utf_counter_actual = uf.parameters["Auto_injector"]["utf_default"]
    injection_duration = datetime.datetime.now() - uf.InjectorParams.injection_start_time
    print("----------------------------All injection rounds has been completed-----------------------------")
    print("Total injection duration was: ", injection_duration)
    print("-----------------------------------------------------------------------------------------------")


class DataFeeder:
    @staticmethod
    def utf8_feeder():
        # inject label to FCL
        global fire_candidate_list
        if uf.InjectorParams.injection_mode == 'c':
            uf.training_neuron_list_utf = IPU_utf8.convert_char_to_fire_list(uf.InjectorParams.utf_to_inject)
        else:
            uf.training_neuron_list_utf = IPU_utf8.convert_char_to_fire_list(str(uf.labeled_image[1]))
        fire_candidate_list = inject_to_fcl(uf.training_neuron_list_utf, fire_candidate_list)
        # print("Activities caused by image label are now part of the FCL")

    @staticmethod
    def img_neuron_list_feeder():
        global fire_candidate_list
        # inject neuron activity to FCL
        fire_candidate_list = inject_to_fcl(uf.training_neuron_list_img, fire_candidate_list)
        # print("Activities caused by image are now part of the FCL")

    @staticmethod
    def image_feeder(num):
        if int(num) < 0:
            num = 0
            print(settings.Bcolors.RED + "Error: image feeder has been fed a less than 0 number" +
                  settings.Bcolors.ENDC)
        uf.labeled_image = mnist_img_fetcher(num)
        # Convert image to neuron activity
        uf.training_neuron_list_img = brain_functions.Brain.retina(uf.labeled_image)
        # print("image has been converted to neuronal activities...")


def neuro_plasticity():
    # The following handles neuro-plasticity
    global fire_candidate_list
    global previous_fcl
    if uf.parameters["Switches"]["plasticity"]:
        # Plasticity between T1 and Vision memory
        # todo: generalize this function
        # Long Term Potentiation (LTP) between vision_IT and vision_memory
        for src_neuron in previous_fcl:
            if src_neuron[0] == "vision_IT":
                for dst_neuron in fire_candidate_list:
                    if dst_neuron[0] == "vision_memory" and dst_neuron[1] \
                            in uf.brain["vision_IT"][src_neuron[1]]["neighbors"]:
                        apply_plasticity_ext(src_cortical_area='vision_IT', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='vision_memory', dst_neuron_id=dst_neuron[1])

                        print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWM"
                                                     "...........LTP between vision_IT and vision_memory occurred "
                              + settings.Bcolors.ENDC)

        # Long Term Depression (LTD) between vision_IT and vision_memory
        for src_neuron in fire_candidate_list:
            if src_neuron[0] == "vision_IT":
                for dst_neuron in previous_fcl:
                    if dst_neuron[0] == "vision_memory" and dst_neuron[1] \
                            in uf.brain["vision_IT"][src_neuron[1]]["neighbors"]:
                        apply_plasticity_ext(src_cortical_area='vision_IT', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='vision_memory', dst_neuron_id=dst_neuron[1],
                                             long_term_depression=True)

                        print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWM"
                                                     "...........LTD between vision_IT and vision_memory occurred "
                              + settings.Bcolors.ENDC)

        # Building a bidirectional synapse between memory neurons who fire together within a cortical area
        # todo: The following loop is very inefficient___ fix it!!
        # todo: Read the following memory list from Genome
        memory_list = uf.cortical_group_members('Memory')
        # memory_list = ['utf8_memory', 'vision_memory']
        for cortical_area in memory_list:
            if uf.genome['blueprint'][cortical_area]['location_generation_type'] == 'random':
                for src_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
                    for dst_neuron in set([j[1] for j in fire_candidate_list if j[0] == cortical_area]):
                        if src_neuron != dst_neuron:
                            apply_plasticity(cortical_area=cortical_area,
                                             src_neuron=src_neuron, dst_neuron=dst_neuron)

        # Wiring Vision memory to UIF-8 memory
        for dst_neuron in fire_candidate_list:
            if dst_neuron[0] == "utf8_memory":
                for src_neuron in fire_candidate_list:
                    if src_neuron[0] == "vision_memory":
                        apply_plasticity_ext(src_cortical_area='vision_memory', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='utf8_memory', dst_neuron_id=dst_neuron[1])

                        print(
                            settings.Bcolors.OKGREEN + "..............................................................."
                                                       "..........A new memory was formed against utf8_memory location "
                            + OPU_utf8.convert_neuron_acticity_to_utf8_char('utf8_memory',
                                                                            dst_neuron[1]) + settings.Bcolors.ENDC)
                        # dst_neuron_id_list = neighbor_finder_ext('utf8_memory', 'utf8_out', _[1], 'rule_3', 0)
                        # for dst_neuron_id in dst_neuron_id_list:
                        #     wire_neurons_together_ext(src_cortical_area='vision_memory', src_neuron=neuron[1],
                        #                               dst_cortical_area='utf8_out', dst_neuron=dst_neuron_id)


def user_input_processing(user_input, user_input_param):
    while not user_input.empty():
        try:
            user_input_value = user_input.get()
            user_input_value_param = user_input_param.get()

            print("User input value is ", user_input_value)
            print("User input param is ", user_input_value_param)

            if user_input_value == 'x':
                print(settings.Bcolors.YELLOW + '>>>Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
                global burst_count
                burst_count = 0
                uf.parameters["Switches"]["ready_to_exit_burst"] = True
                if uf.parameters["Switches"]["capture_brain_activities"]:
                    uf.save_fcl_to_disk()

            elif user_input_value == 'v':
                uf.toggle_verbose_mode()

            elif user_input_value == 'g':
                uf.toggle_visualization_mode()

            elif user_input_value in ['l1', 'l2', 'r', 'c']:
                injection_manager(injection_mode=user_input_value, injection_param=user_input_value_param)

            elif user_input_value in ['t1', 't2']:
                test_manager(test_mode=user_input_value, test_param=user_input_value_param)

        finally:
            uf.parameters["Input"]["user_input"] = ''
            uf.parameters["Input"]["user_input_param"] = ''
            break


#  >>>>>> Review this function against what we had in past
def fire_candidate_locations(fire_cnd_list):
    """Extracts Neuron locations from the fire_candidate_list"""

    # print('***')
    # print(fire_cnd_list)

    neuron_locations = {}
    # Generate a dictionary of cortical areas in the fire_candidate_list
    for item in uf.cortical_areas:
        neuron_locations[item] = []

    # Add neuron locations under each cortical area
    for item in fire_cnd_list:
        neuron_locations[item[0]].append([uf.brain[item[0]][item[1]]["location"][0],
                                         uf.brain[item[0]][item[1]]["location"][1],
                                         uf.brain[item[0]][item[1]]["location"][2]])

    return neuron_locations


def neuron_fire(cortical_area, neuron_id):
    """This function initiate the firing of Neuron in a given cortical area"""
    if uf.parameters["Switches"]["logging_fire"]:
        print(datetime.datetime.now(), " Firing...", cortical_area, neuron_id, file=open("./logs/fire.log", "a"))

    global burst_count

    # Setting Destination to the list of Neurons connected to the firing Neuron
    neighbor_list = uf.brain[cortical_area][neuron_id]["neighbors"]
    # print("Neighbor list:", neighbor_list)
    if uf.parameters["Switches"]["logging_fire"]:
        print(datetime.datetime.now(), "      Neighbors...", neighbor_list, file=open("./logs/fire.log", "a"))
    if uf.parameters["Verbose"]["neuron_functions-neuron_fire"]:
        print(settings.Bcolors.RED +
              "Firing neuron %s using firing pattern %s" %
              (neuron_id, json.dumps(uf.brain[cortical_area][neuron_id]["firing_pattern_id"], indent=3)) +
              settings.Bcolors.ENDC)
        print(settings.Bcolors.RED + "Neuron %s neighbors are %s" % (neuron_id, json.dumps(neighbor_list, indent=3)) +
              settings.Bcolors.ENDC)

    # After neuron fires all cumulative counters on Source gets reset
    uf.brain[cortical_area][neuron_id]["membrane_potential"] = 0
    uf.brain[cortical_area][neuron_id]["last_membrane_potential_reset_time"] = str(datetime.datetime.now())
    uf.brain[cortical_area][neuron_id]["cumulative_fire_count"] += 1
    uf.brain[cortical_area][neuron_id]["cumulative_fire_count_inst"] += 1

    # Transferring the signal from firing Neuron's Axon to all connected Neuron Dendrites
    # Firing pattern to be accommodated here     <<<<<<<<<<  *****
    # neuron_update_list = []
    for dst_neuron_id in neighbor_list:
        if uf.parameters["Verbose"]["neuron_functions-neuron_fire"]:
            print(settings.Bcolors.RED + 'Updating connectome for Neuron ' + dst_neuron_id + settings.Bcolors.ENDC)
        dst_cortical_area = uf.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["cortical_area"]
        neuron_update(dst_cortical_area, dst_neuron_id,
                      uf.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"])

    # Placeholder for refractory period
    # todo: Implement refractory period logic

    # Condition to snooze the neuron if consecutive fire count reaches threshold
    if uf.brain[cortical_area][neuron_id]["consecutive_fire_cnt"] > \
            uf.genome["blueprint"][cortical_area]["neuron_params"]["consecutive_fire_cnt_max"]:
        snooze_till(cortical_area, neuron_id, burst_count +
                    uf.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"])

    # Condition to increase the consecutive fire count
    if burst_count == uf.brain[cortical_area][neuron_id]["last_burst_num"] + 1:
        uf.brain[cortical_area][neuron_id]["consecutive_fire_cnt"] += 1

    uf.brain[cortical_area][neuron_id]["last_burst_num"] = burst_count

    # Condition to translate activity in utf8_out region as a character comprehension
    if cortical_area == 'utf8_out':
        uf.parameters["Input"]["comprehended_char"] = \
            OPU_utf8.convert_neuron_acticity_to_utf8_char(cortical_area, neuron_id)
        print(settings.Bcolors.HEADER + "UTF8 out was stimulated with the following character:    "
              "                            <<<     %s      >>>                 #*#*#*#*#*#*#"
              % uf.parameters["Input"]["comprehended_char"] + settings.Bcolors.ENDC)

    #     neuron_update_list.append([uf.brain[cortical_area][id]["neighbors"][x]["cortical_area"],
        # uf.brain[cortical_area][id]["neighbors"][x]["postsynaptic_current"], x])
    #
    # pool = ThreadPool(4)
    # pool.starmap(neuron_update, neuron_update_list)
    # pool.close()
    # pool.join()

        # Important: Currently calling the update function from Fire function has the potential of running into
        #  recursive error. Need to address this. One solution is to count the number of recursive operations and
        #  exit function when number of steps are beyond a specific point.
        # Its worth noting that this situation is related to how system is architected as if 2 neuron are feeding
        #  to each other there is a bigger chance of this happening.

    global fire_candidate_list
    # print("FCL before fire pop: ", len(fire_candidate_list))
    fire_candidate_list.pop(fire_candidate_list.index([cortical_area, neuron_id]))
    # print("FCL after fire pop: ", len(fire_candidate_list))
    # np.delete(fire_candidate_list, fire_candidate_list.index([cortical_area, neuron_id]))
    if uf.parameters["Verbose"]["neuron_functions-neuron_fire"]:
        print(settings.Bcolors.RED + "Fire Function triggered FCL: %s " % fire_candidate_list + settings.Bcolors.ENDC)

    # todo: add a check that if the firing neuron is part of OPU to perform an action

    return


def neuron_update(cortical_area, dst_neuron_id, postsynaptic_current):
    """This function updates the destination parameters upon upstream Neuron firing"""

    dst_neuron_obj = uf.brain[cortical_area][dst_neuron_id]

    # update the cumulative_intake_total, cumulative_intake_count and postsynaptic_current between source and
    # destination neurons based on XXX algorithm. The source is considered the Axon of the firing neuron and
    # destination is the dendrite of the neighbor.

    if uf.parameters["Verbose"]["neuron_functions-neuron_update"]:
        print("Update request has been processed for: ", cortical_area, dst_neuron_id, " >>>>>>>>> >>>>>>> >>>>>>>>>>")
        print(settings.Bcolors.UPDATE +
              "%s's Cumulative_intake_count value before update: %s" %
              (dst_neuron_id, dst_neuron_obj["membrane_potential"])
              + settings.Bcolors.ENDC)

    # todo: Need to tune up the timer as depending on the application performance the timer could be always expired
    # Check if timer is expired on the destination Neuron and if so reset the counter - Leaky behavior
    # todo: Given time is quantized in this implementation, instead of absolute time need to consider using burst cnt.
    # todo: in rare cases the date conversion format is running into exception
    # if (datetime.datetime.strptime(uf.brain[cortical_area][dst_neuron_id]["last_membrane_potential_reset_time"]
    # , "%Y-%m-%d %H:%M:%S.%f")
    #     + datetime.timedelta(0, dst_neuron_obj["depolarization_timer_threshold"])) < \
    #         datetime.datetime.now():

    global burst_count

    # To simulate a leaky neuron membrane, after x number of burst passing the membrane potential resets to zero
    if burst_count - uf.brain[cortical_area][dst_neuron_id]["last_membrane_potential_reset_burst"] > \
            uf.brain[cortical_area][dst_neuron_id]["depolarization_threshold"]:
        dst_neuron_obj["last_membrane_potential_reset_time"] = str(datetime.datetime.now())
        dst_neuron_obj["last_membrane_potential_reset_burst"] = burst_count
        # todo: Might be better to have a reset func.
        dst_neuron_obj["membrane_potential"] = 0
        if uf.parameters["Verbose"]["neuron_functions-neuron_update"]:
            print(settings.Bcolors.UPDATE + 'Cumulative counters for Neuron ' + dst_neuron_id +
                  ' got rest' + settings.Bcolors.ENDC)

    # Increasing the cumulative counter on destination based on the received signal from upstream Axon
    # The following is considered as LTP or Long Term Potentiation of Neurons
    uf.brain[cortical_area][dst_neuron_id]["membrane_potential"] += postsynaptic_current

    # print("membrane_potential:", destination,
    #       ":", uf.brain[cortical_area][destination]["membrane_potential"])

    if uf.parameters["Verbose"]["neuron_functions-neuron_update"]:
        print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value after update: %s" %
              (dst_neuron_id, dst_neuron_obj["membrane_potential"])
              + settings.Bcolors.ENDC)

    # Add code to start a timer when neuron first receives a signal and reset counters when its expired

    # Need to call the Fire function if the threshold on the destination Neuron is met  <<<<<<<<<<<  ********
    # Need to figure how to deal with Activation function and firing threshold
    # Pass the cumulative_intake_total through the activation function and if pass the condition
    # fire destination neuron

    # The following will evaluate if the destination neuron is ready to fire and if so adds it to
    # fire_candidate_list
    global fire_candidate_list

    if dst_neuron_obj["membrane_potential"] > \
            dst_neuron_obj["firing_threshold"]:
        if dst_neuron_obj["snooze_till_burst_num"] <= burst_count:
            if fire_candidate_list.count([cortical_area, dst_neuron_id]) == 0:   # To prevent duplicate entries
                fire_candidate_list.append([cortical_area, dst_neuron_id])
                if uf.parameters["Verbose"]["neuron_functions-neuron_update"]:
                    print(settings.Bcolors.UPDATE + "    Update Function triggered FCL: %s " % fire_candidate_list
                          + settings.Bcolors.ENDC)

    return fire_candidate_list


def neuron_prop(cortical_area, neuron_id):
    """This function accepts neuron id and returns neuron properties"""

    data = uf.brain[cortical_area]

    if uf.parameters["Switches"]["verbose"]:
        print('Listing Neuron Properties for %s:' % neuron_id)
        print(json.dumps(data[neuron_id], indent=3))
    return data[neuron_id]


def neuron_neighbors(cortical_area, neuron_id):
    """This function accepts neuron id and returns the list of Neuron neighbors"""

    data = uf.brain[cortical_area]

    if uf.parameters["Switches"]["verbose"]:
        print('Listing Neuron Neighbors for %s:' % neuron_id)
        print(json.dumps(data[neuron_id]["neighbors"], indent=3))
    return data[neuron_id]["neighbors"]


def apply_plasticity(cortical_area, src_neuron, dst_neuron):
    """
    This function simulates neuron plasticity in a sense that when neurons in a given cortical area fire in the 
     same burst they wire together. This is done by increasing the postsynaptic_current associated with a link between
     two neuron. Additionally an event id is associated to the neurons who have fired together.
    """

    genome = uf.genome

    # Since this function only targets Memory regions and neurons in memory regions do not have neighbor relationship
    # by default hence here we first need to synapse the source and destination together
    # Build neighbor relationship between the source and destination if its not already in place

    # Check if source and destination have an existing synapse if not create one here
    if dst_neuron not in uf.brain[cortical_area][src_neuron]["neighbors"]:
        synapse(cortical_area, src_neuron, cortical_area, dst_neuron,
                genome["blueprint"][cortical_area]["postsynaptic_current"])

    # Every time source and destination neuron is fired at the same time which in case of the code architecture
    # reside in the same burst, the postsynaptic_current will be increased simulating the fire together, wire together.
    # This phenomenon is also considered as long term potentiation or LTP
    uf.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"] += \
        genome["blueprint"][cortical_area]["plasticity_constant"]

    # Condition to cap the postsynaptic_current and provide prohibitory reaction
    uf.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"] = \
        min(uf.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"],
            genome["blueprint"][cortical_area]["postsynaptic_current_max"])

    # Append a Group ID so Memory clusters can be uniquely identified
    if uf.event_id:
        if uf.event_id in uf.brain[cortical_area][src_neuron]["event_id"]:
            uf.brain[cortical_area][src_neuron]["event_id"][uf.event_id] += 1
        else:
            uf.brain[cortical_area][src_neuron]["event_id"][uf.event_id] = 1

    return


def apply_plasticity_ext(src_cortical_area, src_neuron_id, dst_cortical_area,
                         dst_neuron_id, long_term_depression=False):

    genome = uf.genome
    plasticity_constant = genome["blueprint"][src_cortical_area]["plasticity_constant"]

    if long_term_depression:
        # When long term depression flag is set, there will be negative synaptic influence caused
        plasticity_constant = plasticity_constant * (-1)

    # Check if source and destination have an existing synapse if not create one here
    if dst_neuron_id not in uf.brain[src_cortical_area][src_neuron_id]["neighbors"]:
        synapse(src_cortical_area, src_neuron_id, dst_cortical_area, dst_neuron_id, max(plasticity_constant, 0))

    else:
        neuron_update(src_cortical_area, src_neuron_id, plasticity_constant)

    return


def snooze_till(cortical_area, neuron_id, burst_id):
    """ Acting as an inhibitory neurotransmitter to suppress firing of neuron till a later burst

    *** This function instead of inhibitory behavior is more inline with Neuron Refractory period

    """
    uf.brain[cortical_area][neuron_id]["snooze_till_burst_num"] \
        = burst_id + uf.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"]
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
