
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
import json, csv
from datetime import datetime
from collections import deque
from time import sleep
from PUs import OPU_utf8, IPU_utf8
from . import brain_functions
from misc import disk_ops
from misc import db_handler
from configuration import settings, runtime_data
from PUs.IPU_vision import MNIST
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
        self.empty_fcl_counter = 0
        self.neuron_mp_list = []
        self.time_neuron_update = datetime.now()


class InjectorParams:
    def __init__(self):
        self.img_flag = False
        self.utf_flag = False
        self.injection_has_begun = False
        self.variation_handler = True
        self.exposure_handler = True
        self.utf_handler = True
        self.variation_counter = runtime_data.parameters["Auto_injector"]["variation_default"]
        self.exposure_default = runtime_data.parameters["Auto_injector"]["exposure_default"]
        self.utf_default = runtime_data.parameters["Auto_injector"]["utf_default"]
        self.variation_counter_actual = self.variation_counter
        self.exposure_counter_actual = self.exposure_default
        self.utf_counter_actual = self.utf_default
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
        self.exposure_default = runtime_data.parameters["Auto_tester"]["exposure_default"]
        self.utf_default = runtime_data.parameters["Auto_tester"]["utf_default"]
        self.variation_counter_actual = self.variation_counter
        self.exposure_counter_actual = self.exposure_default
        self.utf_counter_actual = self.utf_default
        self.test_start_time = datetime.now()
        self.num_to_inject = ''
        self.test_mode = ''
        self.comprehension_counter = 0
        self.test_attempt_counter = 0
        self.no_response_counter = 0
        # self.temp_stats = []
        self.test_stats = {}
        self.test_id = ""


global init_data, injector_params, test_params


def burst(user_input, user_input_param, fire_list, brain_queue, event_queue,
          genome_stats_queue, parameters_queue, block_dic_queue, genome_id_queue, activity_stats_queue):
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

    print('Starting the burst engine...')
    runtime_data.parameters = parameters_queue.get()
    runtime_data.activity_stats = activity_stats_queue.get()
    print(runtime_data.parameters['Switches']['use_static_genome'])
    disk_ops.genome_handler(runtime_data.parameters['InitData']['connectome_path'])

    # todo: Move comprehension span to genome that is currently in parameters
    comprehension_span = runtime_data.parameters["InitData"]["comprehension_span"]
    
    # Initializing the comprehension queue
    comprehension_queue = deque(['-'] * comprehension_span)

    global init_data, test_params, injector_params

    init_data = InitData()
    injector_params = InjectorParams()
    test_params = TesterParams()
    mongo = db_handler.MongoManagement()

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
    runtime_data.genome_id = genome_id_queue.get()

    print('runtime_data.genome_id = ', runtime_data.genome_id)

    cortical_list = []
    for cortical_area in runtime_data.genome['blueprint']:
        cortical_list.append(cortical_area)
    runtime_data.cortical_list = cortical_list
    runtime_data.memory_list = cortical_group_members('Memory')

    verbose = runtime_data.parameters["Switches"]["verbose"]

    if runtime_data.parameters["Switches"]["capture_brain_activities"]:
        init_data.fcl_history = {}

    # todo: add a logic to exit bust engine if during the training multiple consecutive burst are empty
    DataFeeder()

    if runtime_data.parameters["Switches"]["capture_neuron_mp"]:
        with open(runtime_data.parameters['InitData']['connectome_path'] + '/neuron_mp.csv', 'w') as neuron_mp_file:
            neuron_mp_writer = csv.writer(neuron_mp_file, delimiter=',')
            neuron_mp_writer.writerow(('burst_number', 'cortical_layer', 'neuron_id', 'membrane_potential'))

    # Live mode condition
    if runtime_data.parameters["Switches"]["live_mode"] and init_data.live_mode_status == 'idle':
        init_data.live_mode_status = 'learning'
        print(
            settings.Bcolors.RED + "Starting an automated learning process...<> <> <> <>" + settings.Bcolors.ENDC)
        injection_manager(injection_mode="l1", injection_param="")

    while not runtime_data.parameters["Switches"]["ready_to_exit_burst"]:
        burst_start_time = datetime.now()
        # print(datetime.now(), "Burst count = ", init_data.burst_count, file=open("./logs/burst.log", "a"))

        # List of Fire candidates are placed in global variable fire_candidate_list to be passed for next Burst

        # Read FCL from the Multiprocessing Queue
        init_data.fire_candidate_list = fire_list.get()
        init_data.previous_fcl = list(init_data.fire_candidate_list)
        init_data.burst_count += 1

        # Fire all neurons within fire_candidate_list (FCL) or add a delay if FCL is empty
        time_firing_activities = datetime.now()
        if len(init_data.fire_candidate_list) < 1 and not runtime_data.parameters["Auto_injector"]["injector_status"]:
            sleep(runtime_data.parameters["Timers"]["idle_burst_timer"])
            init_data.empty_fcl_counter += 1
            print("FCL is empty!")
        else:
            # brain_neuron_count, brain_synapse_count = stats.brain_total_synapse_cnt(verbose=False)
            # print(settings.Bcolors.YELLOW +
            #       'Burst count = %i  --  Neuron count in FCL is %i  -- Total brain synapse count is %i'
            #       % (init_data.burst_count, len(init_data.fire_candidate_list), brain_synapse_count) +
            # settings.Bcolors.ENDC)

            # Capture cortical activity stats
            for cortical_area in set([i[0] for i in init_data.fire_candidate_list]):
                if cortical_area in runtime_data.activity_stats:
                    cortical_neuron_count = len(set([i[1] for i in
                                                     init_data.fire_candidate_list if i[0] == cortical_area]))
                    runtime_data.activity_stats[cortical_area] = max(runtime_data.activity_stats[cortical_area],
                                                                        cortical_neuron_count)

                    if runtime_data.parameters["Logs"]["print_cortical_activity_counters"]:
                        print(settings.Bcolors.YELLOW + '    %s : %i  '
                              % (cortical_area, cortical_neuron_count)
                              + settings.Bcolors.ENDC)
                else:
                    runtime_data.activity_stats[cortical_area] = \
                        len(set([i[1] for i in init_data.fire_candidate_list if i[0] == cortical_area]))


                # for entry in init_data.fire_candidate_list:
                #     if runtime_data.genome['blueprint'][entry[0]]['group_id'] == 'Memory':
                #         print(settings.Bcolors.YELLOW + entry[0], entry[1] + settings.Bcolors.ENDC)
                    # if runtime_data.genome['blueprint'][cortical_area]['group_id'] == 'Memory' \
                    #         and len(set([i[1] for i in init_data.fire_candidate_list if i[0] == cortical_area])) > 0:
                    #     sleep(runtime_data.parameters["Timers"]["idle_burst_timer"])

            # todo: Look into multi-threading for Neuron neuron_fire and wire_neurons function
            # Firing all neurons in the Fire Candidate List
            # Fire all neurons in FCL
            time_actual_firing_activities = datetime.now()
            now = datetime.now()
            init_data.time_neuron_update = datetime.now() - now
            for x in list(init_data.fire_candidate_list):
                if verbose:
                    print(settings.Bcolors.YELLOW + 'Firing Neuron: ' + x[1] + ' from ' + x[0] + settings.Bcolors.ENDC)
                # if x[0] in ['utf8_out', 'utf8_memory', 'utf8', 'vision_memory']:
                #     print(settings.Bcolors.RED + '<***>', x[0], x[1][27:], 'MP=',
                #           str(runtime_data.brain[x[0]][x[1]]['membrane_potential']) + settings.Bcolors.ENDC)
                neuron_fire(x[0], x[1])

            print("Timing : - Actual firing activities:", datetime.now() - time_actual_firing_activities)
            print("Timing : |___________Neuron updates:", init_data.time_neuron_update)

            if verbose:
                print(settings.Bcolors.YELLOW + 'Current fire_candidate_list is %s'
                      % init_data.fire_candidate_list + settings.Bcolors.ENDC)

            # print_cortical_neuron_mappings('vision_memory', 'utf8_memory')
        print("Timing : Overall firing activities:", datetime.now() - time_firing_activities)


        # todo: need to break down the training function into pieces with one feeding a stream of data
        # Auto-inject if applicable
        if runtime_data.parameters["Auto_injector"]["injector_status"]:
            injection_time = datetime.now()
            auto_injector()
            print("Timing : Injection:", datetime.now() - injection_time)

        # Auto-test if applicable
        if runtime_data.parameters["Auto_tester"]["tester_status"]:
            test_time = datetime.now()
            auto_tester()
            print("Timing : Test:", datetime.now() - test_time)

        # todo: The following is to have a check point to assess the perf of the in-use genome and make on the fly adj.
        # if init_data.burst_count % runtime_data.genome['evolution_burst_count'] == 0:
        #     print('Evolution phase reached...')
        #     genethesizer.generation_assessment()

        # Saving FCL to disk for post-processing and running analytics
        if runtime_data.parameters["Switches"]["save_fcl_to_db"]:
            disk_ops.save_fcl_in_db(init_data.burst_count, init_data.fire_candidate_list, injector_params.num_to_inject)

        # Push back updated fire_candidate_list into FCL from Multiprocessing Queue
        fire_list.put(init_data.fire_candidate_list)

        detected_char = utf_detection_logic(init_data.burst_detection_list)
        comprehension_queue.append(detected_char)
        comprehension_queue.popleft()

        def training_quality_test():
            for entry in list_upstream_neuron_count_for_digits():
                if entry[1] == 0:
                    print(list_upstream_neuron_count_for_digits(), "This entry was zero >", entry)
                    return False

        # Monitor cortical activity levels and terminate brain if not meeting expectations
        time_monitoring_cortical_activity = datetime.now()
        if runtime_data.parameters["Switches"]["evaluation_based_termination"]:
            if runtime_data.parameters["Auto_injector"]["injector_status"] and \
                    init_data.burst_count > runtime_data.parameters["InitData"]["kill_trigger_burst_count"]:
                if 'vision_memory' not in runtime_data.activity_stats:
                    runtime_data.activity_stats['vision_memory'] = 0
                elif runtime_data.activity_stats['vision_memory'] < \
                            runtime_data.parameters["InitData"]["kill_trigger_vision_memory_min"]:
                        print(settings.Bcolors.RED +
                              "\n\n\n\n\n\n!!!!! !! !Terminating the brain due to low performance! !! !!!" +
                              settings.Bcolors.ENDC)
                        print("vision_memory max activation was:", runtime_data.activity_stats['vision_memory'])
                        burst_exit_process()

            # # todo: Need to troubleshoot
            # if runtime_data.parameters["Auto_injector"]["injector_status"] and \
            #             init_data.burst_count > (runtime_data.parameters["Auto_injector"]["exposure_default"] * 11):
            #     if not training_quality_test():
            #         print(settings.Bcolors.RED +
            #               "\n\n\n\n\n\n!!!!! !! !Terminating the brain due to low training capability! !! !!!" +
            #                   settings.Bcolors.ENDC)
            #         burst_exit_process()
        print("Timing : Monitoring cortical activity:", datetime.now()-time_monitoring_cortical_activity)



        # Comprehension check
        time_comprehension_check = datetime.now()
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
                print(settings.Bcolors.HEADER + "UTF8 out was stimulated with the following character: <<< %s  >>>"
                      % runtime_data.parameters["Input"]["comprehended_char"] + settings.Bcolors.ENDC)
                # In the event that the comprehended UTF character is not matching the injected one pain is triggered
                if runtime_data.parameters["Input"]["comprehended_char"] != str(init_data.labeled_image[1]):
                    trigger_pain()
            else:
                if list_length >= 2:
                    runtime_data.parameters["Input"]["comprehended_char"] = ''

        # # # # DEBUGGING
        # print("********************************************************************************************")
        # print("************************************************************************************")
        # print("******************************************************************************")
        # print("\n\nListing PFCL memory entries...")
        # for entry in init_data.previous_fcl:
        #     if entry[0] == 'vision_memory' or entry[0] == 'utf_memory':
        #         print(" >>> PFCL: ", entry[0], entry[1])
        # print("\n\nListing CFCL memory entries...")
        # for entry in init_data.fire_candidate_list:
        #     if entry[0] == 'vision_memory' or entry[0] == 'utf_memory':
        #         print(" >>> CFCL: ", entry[0], entry[1])
        # print("******************************************************************************")
        # print("************************************************************************************")
        # print("********************************************************************************************")
        # # # # END of DEBUGGING


        # Forming memories through creation of cell assemblies
        if runtime_data.parameters["Switches"]["memory_formation"]:
            # memory_formation_start_time = datetime.now()
            form_memories()
            # print("    Memory formation took--",datetime.now()-memory_formation_start_time)
        print("Timing : Comprehension check:", datetime.now() - time_comprehension_check)


        # Listing the number of neurons activating each UTF memory neuron
        upstream_report_time = datetime.now()
        print("list_upstream_neuron_count_for_digits:", list_upstream_neuron_count_for_digits())
        common_neuron_report()
        print("Timing : Upstream + common neuron report:", datetime.now() - upstream_report_time)

        # Resetting burst detection list
        init_data.burst_detection_list = {}

        # # todo: *** Danger *** The following section could cause considerable memory expansion. Need to add limitations.
        # # Condition to save FCL data to disk
        # user_input_processing(user_input, user_input_param)
        # if runtime_data.parameters["Switches"]["capture_brain_activities"]:
        #     init_data.fcl_history[init_data.burst_count] = init_data.fire_candidate_list
        #
        # if runtime_data.parameters["Switches"]["save_fcl_to_disk"]:
        #     with open('./fcl_repo/fcl.json', 'w') as fcl_file:
        #         fcl_file.write(json.dumps(init_data.fire_candidate_list))
        #         fcl_file.truncate()
        #     sleep(0.5)

        # todo: This is the part to capture the neuron membrane potential values in a file, still need to figure how
        if runtime_data.parameters["Switches"]["capture_neuron_mp"]:
            with open(runtime_data.parameters['InitData']['connectome_path'] + '/neuron_mp.csv', 'a') as neuron_mp_file:
                neuron_mp_writer = csv.writer(neuron_mp_file,  delimiter=',')
                new_data = []
                for fcl_item in init_data.fire_candidate_list:
                    new_content = (init_data.burst_count, fcl_item[0], fcl_item[1], runtime_data.brain[fcl_item[0]][fcl_item[1]]["membrane_potential"])
                    new_data.append(new_content)
                neuron_mp_writer.writerows(new_data)


        if runtime_data.parameters["Switches"]["capture_neuron_mp_db"]:
            new_data = []
            for fcl_item in init_data.fire_candidate_list:
                new_content = (init_data.burst_count, fcl_item[0], fcl_item[1],
                               runtime_data.brain[fcl_item[0]][fcl_item[1]]["membrane_potential"])
                new_data.append(new_content)
                mongo.inset_membrane_potentials(new_content)

        burst_duration = datetime.now() - burst_start_time
        if runtime_data.parameters["Logs"]["print_burst_info"]:
            print(settings.Bcolors.YELLOW + ">>> Burst duration: %s %i --- ---- ---- ---- ---- ---- ----" % (burst_duration, init_data.burst_count) + settings.Bcolors.ENDC)


    # Push updated brain data back to the queue
    brain_queue.put(runtime_data.brain)
    block_dic_queue.put(runtime_data.block_dic)
    genome_id_queue.put(runtime_data.genome_id)
    activity_stats_queue.put(runtime_data.activity_stats)
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
            test_params.exit_flag = False
            test_params.burst_skip_flag = False
            test_params.utf_handler = True
            test_params.variation_handler = True
            test_params.variation_counter = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.variation_counter_actual = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.utf_default = runtime_data.parameters["Auto_tester"]["utf_default"]
            test_params.utf_counter_actual = runtime_data.parameters["Auto_tester"]["utf_default"]
            test_params.num_to_inject = test_params.utf_default
            test_params.burst_skip_counter = runtime_data.parameters["Auto_tester"]["tester_burst_skip_counter"]

        elif test_mode == 't2':
            test_params.test_mode = "t2"
            test_params.img_flag = True
            test_params.utf_flag = True
            test_params.exit_flag = False
            test_params.burst_skip_flag = False
            test_params.utf_handler = False
            test_params.variation_handler = True
            test_params.variation_counter = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.variation_counter_actual = runtime_data.parameters["Auto_tester"]["variation_default"]
            test_params.utf_default = -1
            test_params.utf_counter_actual = -1
            test_params.num_to_inject = int(test_param)
            test_params.burst_skip_counter = runtime_data.parameters["Auto_tester"]["tester_burst_skip_counter"]
            print("   <<<   Automatic learning for variations of number << %s >> has been turned ON!   >>>"
                  % test_param)

        else:
            print("Error detecting the test mode...")
            return

    finally:
        toggle_test_mode()
        test_params.test_id = test_id_gen()
        test_params.test_stats["genome_id"] = init_data.genome_id
        print('Genome_id = ', init_data.genome_id)
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


    # Mechanism to skip a number of bursts between each injections to clean-up FCL
    if not test_params.burst_skip_flag:

        print(".... .. .. .. ... New Exposure ... ... ... .. .. ")

        # Injecting test image to the FCL
        if test_params.img_flag:
            data_feeder.img_neuron_list_feeder()

        # Exposure counter
        test_params.exposure_counter_actual -= 1

        print("Exposure counter actual: ", test_params.exposure_counter_actual)
        print("Variation counter actual: ", test_params.variation_counter_actual,
              test_params.variation_handler)
        print("UTF counter actual: ", test_params.utf_counter_actual, test_params.utf_handler)

        if test_params.exposure_counter_actual < 1:
            # Turning on the skip flag to allow FCL to clear
            test_params.burst_skip_flag = True

    else:
        print("Skipping the injection for this round...")
        test_params.burst_skip_counter -= 1
        if test_params.burst_skip_counter <= 0 or len(init_data.fire_candidate_list) < 1:
            test_params.burst_skip_counter = runtime_data.parameters["Auto_tester"]["tester_burst_skip_counter"]
            test_params.burst_skip_flag = False

            # Final phase of a single test instance is to evaluate the comprehension when FCL is cleaned up
            test_comprehension_logic()
            test_params.test_attempt_counter += 1

            print("Number to inject:", test_params.num_to_inject)
            print(test_params.utf_default,
                  test_params.variation_counter,
                  test_params.exposure_default)

            print(test_params.utf_counter_actual,
                  test_params.variation_counter_actual,
                  test_params.exposure_counter_actual)

            # Test stats
            update_test_stats()
            print("stats just got updated")

            print(".... .. .. .. ... .... .. .. . ... ... ... .. .. ")
            print(".... .. .. .. ... New Variation... ... ... .. .. ")
            print(".... .. .. .. ... ... .. .. .  ... ... ... .. .. ")
            test_params.exposure_counter_actual = test_params.exposure_default

            # Variation counter
            test_params.variation_counter_actual -= 1
            print('#-#-# Current test variation counter is ', test_params.variation_counter_actual)
            print("#-#-# Current number to inject is :", test_params.num_to_inject)

            print("Test stats:\n", test_params.test_stats)

            # Counter logic
            if test_params.variation_counter_actual < 1:
                print(".... .. .. .. ... .... .. .. . ... ... ... .. .. ")
                print(".... .. .. .. ... .... .. .. . ... ... ... .. .. ")
                print(".... .. .. .. ... New UTF .. . ... ... ... .. .. ")
                print(".... .. .. .. ... ... .. .. .  ... ... ... .. .. ")
                print(".... .. .. .. ... .... .. .. . ... ... ... .. .. ")
                # Resetting all test counters
                test_params.exposure_counter_actual = test_params.exposure_default
                test_params.variation_counter_actual = test_params.variation_counter
                test_params.test_attempt_counter = 0
                test_params.comprehension_counter = 0
                test_params.no_response_counter = 0
                # UTF counter
                test_params.utf_counter_actual -= 1
                if test_params.utf_counter_actual < 0:
                    print(">> Test exit condition has been met <<")
                    test_params.exit_flag = True
                    test_exit_process()

                if test_params.utf_flag:
                    test_params.num_to_inject -= 1

            if test_params.img_flag and not test_params.exit_flag:
                print('#-#-# Current number that is about to be tested is ', test_params.num_to_inject)
                data_feeder.image_feeder(test_params.num_to_inject)


def update_test_stats():
    global test_params
    # Initialize parameters
    utf_exposed = str(test_params.num_to_inject) + '_exposed'
    utf_comprehended = str(test_params.num_to_inject) + '_comprehended'
    utf_no_response = str(test_params.num_to_inject) + '_no_response'
    if utf_exposed not in test_params.test_stats:
        test_params.test_stats[utf_exposed] = runtime_data.parameters["Auto_tester"]["utf_default"]
    if utf_comprehended not in test_params.test_stats:
        test_params.test_stats[utf_comprehended] = 0
    if utf_no_response not in test_params.test_stats:
        test_params.test_stats[utf_no_response] = 0

    # Add current stats to the list
    test_params.test_stats[utf_exposed] = test_params.test_attempt_counter
    test_params.test_stats[utf_comprehended] = test_params.comprehension_counter
    test_params.test_stats[utf_no_response] = test_params.no_response_counter
    print('no_response_counter: ', test_params.no_response_counter)
    print('comprehension_counter: ', test_params.comprehension_counter)
    print('attempted_counter: ', test_params.test_attempt_counter)

def test_comprehension_logic():
    global test_params
    # Comprehension logic
    print("\n****************************************")
    print("Comprehended char> ", runtime_data.parameters["Input"]["comprehended_char"], "  Injected char> ", test_params.num_to_inject)
    print("****************************************\n")
    if runtime_data.parameters["Input"]["comprehended_char"] == '':
        test_params.no_response_counter += 1
    elif runtime_data.parameters["Input"]["comprehended_char"] == str(test_params.num_to_inject):
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


def test_exit_process():
    global test_params
    global init_data
    
    runtime_data.parameters["Auto_tester"]["tester_status"] = False
    # test_params.exposure_counter_actual = runtime_data.parameters["Auto_tester"]["exposure_default"]
    # test_params.variation_counter_actual = runtime_data.parameters["Auto_tester"]["variation_default"]
    # test_params.utf_counter_actual = runtime_data.parameters["Auto_tester"]["utf_default"]
    test_duration = datetime.now() - test_params.test_start_time
    print("----------------------------All testing rounds has been completed-----------------------------")
    print("Total test duration was: ", test_duration)
    print("-----------------------------------------------------------------------------------------------")
    print("Test statistics are as follows:\n")
    # for test in test_params.test_stats:
    #     print(test, "\n", test_params.test_stats[test])
    print("-----------------------------------------------------------------------------------------------")
    print("-----------------------------------------------------------------------------------------------")

    print('               ', end='')
    for _ in reversed(range(1 + runtime_data.parameters["Auto_tester"]["utf_default"])):
        print(_,'    ', end='')

    print('\nExposed:       ', end='')
    for test in test_params.test_stats:
        if 'exposed' in test:
            print(test_params.test_stats[test], '    ', end='')
    print('\nno_response :  ', end='')
    for test in test_params.test_stats:
        if 'no_response' in test:
            print(test_params.test_stats[test], '    ', end='')
    print('\ncomprehended : ', end='')
    for test in test_params.test_stats:
        if 'comprehended' in test:
            print(test_params.test_stats[test], '    ', end='')

    print("\n-----------------------------------------------------------------------------------------------")
    print("-----------------------------------------------------------------------------------------------")

    print("test_stats:\n", test_params.test_stats)

    test_params.test_attempt_counter = 0
    test_params.comprehension_counter = 0
    test_params.no_response_counter = 0
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
            injector_params.exit_flag = False
            injector_params.burst_skip_flag = False
            injector_params.utf_handler = True
            injector_params.variation_handler = True
            injector_params.variation_counter = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.variation_counter_actual = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.utf_default = runtime_data.parameters["Auto_injector"]["utf_default"]
            injector_params.utf_counter_actual = runtime_data.parameters["Auto_injector"]["utf_default"]
            injector_params.num_to_inject = injector_params.utf_default
            injector_params.burst_skip_counter = runtime_data.parameters["Auto_injector"]["injector_burst_skip_counter"]

        elif injection_mode == 'l2':
            injector_params.injection_mode = "l2"
            injector_params.img_flag = True
            injector_params.utf_flag = True
            injector_params.burst_skip_flag = False
            injector_params.utf_handler = False
            injector_params.variation_handler = True
            injector_params.variation_counter = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.variation_counter_actual = runtime_data.parameters["Auto_injector"]["variation_default"]
            injector_params.utf_default = 1
            injector_params.utf_counter_actual = 1
            injector_params.num_to_inject = int(injection_param)
            injector_params.burst_skip_counter = runtime_data.parameters["Auto_injector"]["injector_burst_skip_counter"]
            print("   <<<   Automatic learning for variations of number << %s >> has been turned ON!   >>>"
                  % injection_param)

        elif injection_mode == 'r':
            injector_params.injection_mode = "r"
            injector_params.variation_handler = False
            injector_params.img_flag = True
            injector_params.utf_flag = False
            injector_params.burst_skip_flag = False
            injector_params.variation_counter = 0
            injector_params.variation_counter_actual = 0
            injector_params.utf_default = -1
            injector_params.utf_counter_actual = -1
            injector_params.num_to_inject = injection_param

        elif injection_mode == 'c':
            injector_params.injection_mode = "c"
            injector_params.variation_handler = False
            injector_params.utf_handler = False
            injector_params.img_flag = False
            injector_params.utf_flag = True
            injector_params.burst_skip_flag = False
            injector_params.utf_to_inject = injection_param
            injector_params.variation_counter = 0
            injector_params.variation_counter_actual = 0
            injector_params.utf_default = -1
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
        data_feeder.image_feeder(injector_params.num_to_inject)

    # Mechanism to skip a number of bursts between each injections to clean-up FCL
    if not injector_params.burst_skip_flag:

        if injector_params.img_flag:
            data_feeder.img_neuron_list_feeder()
        if injector_params.utf_flag:
            data_feeder.utf8_feeder()

        # Exposure counter
        if not injector_params.burst_skip_flag:
            injector_params.exposure_counter_actual -= 1

        print('### ', injector_params.variation_counter_actual, injector_params.utf_counter_actual,
              injector_params.exposure_counter_actual, ' ###')

        # Check if exit condition has been met
        if injection_exit_condition() or injector_params.variation_counter_actual < 1:
            injection_exit_process()

        # Counter logic
        if injector_params.exposure_counter_actual < 1:

            # Effectiveness check
            if runtime_data.parameters["Switches"]["evaluation_based_termination"]:
                print('## ## ###:', list_upstream_neuron_count_for_digits(injector_params.utf_counter_actual))
                if list_upstream_neuron_count_for_digits(injector_params.utf_counter_actual)[0][1] == 0:
                    print(settings.Bcolors.RED +
                          "\n\n\n\n\n\n!!!!! !! !Terminating the brain due to low training capability! !! !!!" +
                          settings.Bcolors.ENDC)
                    burst_exit_process()
                    injector_params.exit_flag = True

            if not injector_params.exit_flag:
                # Resetting exposure counter
                injector_params.exposure_counter_actual = injector_params.exposure_default

                # UTF counter
                injector_params.utf_counter_actual -= 1

                # Turning on the skip flag to allow FCL to clear
                injector_params.burst_skip_flag = True

                if injector_params.utf_counter_actual < 0:
                    # Resetting counters to their default value
                    injector_params.utf_counter_actual = injector_params.utf_default
                    # Variation counter
                    injector_params.variation_counter_actual -= 1

                injector_params.num_to_inject = max(injector_params.utf_counter_actual, 0)
                print("injector_params.num_to_inject: ", injector_params.num_to_inject)
                data_feeder.image_feeder(injector_params.num_to_inject)
                # Saving brain to disk
                # todo: assess the impact of the following disk operation
                if runtime_data.parameters["Switches"]["save_connectome_to_disk"]:
                    for cortical_area in runtime_data.cortical_list:
                        with open(runtime_data.parameters['InitData']['connectome_path'] +
                                  cortical_area + '.json', "r+") as data_file:
                            data = runtime_data.brain[cortical_area]
                            for _ in data:
                                data[_]['activity_history'] = ""
                            data_file.seek(0)  # rewind
                            data_file.write(json.dumps(data, indent=3))
                            data_file.truncate()

    else:
        print("Skipping the injection for this round...")
        injector_params.burst_skip_counter -= 1
        if injector_params.burst_skip_counter <= 0 or len(init_data.fire_candidate_list) < 1:
            injector_params.burst_skip_counter = runtime_data.parameters["Auto_injector"][
                "injector_burst_skip_counter"]
            injector_params.burst_skip_flag = False


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
    injector_params.num_to_inject = ''
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
            print("!!! Image label: ", init_data.labeled_image[1])
        init_data.fire_candidate_list = inject_to_fcl(init_data.training_neuron_list_utf, init_data.fire_candidate_list)
        print("           UTF8 activities has been injected to the FCL                      ^^^^^^^^^^^^^^^^^^^^^^")

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
        mnist = MNIST()
        init_data.labeled_image = mnist.mnist_img_fetcher(num)
        print('+++++ ', num, init_data.labeled_image[1])
        # Convert image to neuron activity
        init_data.training_neuron_list_img = brain.retina(init_data.labeled_image)
        # print("image has been converted to neuronal activities...")


def form_memories():
    # The following handles neuro-plasticity
    global init_data

    pfcl = init_data.previous_fcl
    # print("\nEla joon says pfcl is :                                  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", pfcl)
    cfcl = init_data.fire_candidate_list
    # print("\nPsy joon says cfcl is :                                  ++++++++++++++++++++++++++++++++++", cfcl)

    # The following two sections that are commented out have been implemented as part of neuron fire and update

    # Long Term Potentiation (LTP)
    # for entry in pfcl:
    #     cortical_area = entry[0]
    #     neuron_id = entry[1]
    #     for neighbor_id in runtime_data.brain[cortical_area][neuron_id]["neighbors"]:
    #         neighbor_cortical_area = \
    #             runtime_data.brain[cortical_area][neuron_id]["neighbors"][neighbor_id]['cortical_area']
    #         if [neighbor_cortical_area, neighbor_id] in cfcl and cortical_area != neighbor_cortical_area:
    #             apply_plasticity_ext(src_cortical_area=cortical_area, src_neuron_id=neuron_id,
    #                                  dst_cortical_area=neighbor_cortical_area, dst_neuron_id=neighbor_id,
    #                                  long_term_depression=False)
    #             if runtime_data.parameters["Logs"]["print_plasticity_info"]:
    #                 print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWMWMWM"
    #                                              "...........LTP between %s and %s occurred"
    #                       % (cortical_area, neighbor_cortical_area)
    #                       + settings.Bcolors.ENDC)

    # Long Term Depression
    # for entry in cfcl:
    #     cortical_area = entry[0]
    #     neuron_id = entry[1]
    #     for neighbor_id in runtime_data.brain[cortical_area][neuron_id]["neighbors"]:
    #         neighbor_cortical_area = \
    #             runtime_data.brain[cortical_area][neuron_id]["neighbors"][neighbor_id]['cortical_area']
    #         if [neighbor_cortical_area, neighbor_id] in pfcl and cortical_area != neighbor_cortical_area:
    #             apply_plasticity_ext(src_cortical_area=cortical_area, src_neuron_id=neuron_id,
    #                                  dst_cortical_area=neighbor_cortical_area, dst_neuron_id=neighbor_id,
    #                                  long_term_depression=True)
    #
    #             if runtime_data.parameters["Logs"]["print_plasticity_info"]:
    #                 print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWMWMWM"
    #                                              "...........LTD between %s and %s occurred"
    #                       % (cortical_area, neighbor_cortical_area)
    #                       + settings.Bcolors.ENDC)

    # # Plasticity between T1 and Vision memory
    # # todo: generalize this function
    # # Long Term Potentiation (LTP) between vision_IT and vision_memory
    # for src_neuron in pfcl:
    #     if src_neuron[0] == "vision_IT":
    #         for dst_neuron in cfcl:
    #             if dst_neuron[0] == "vision_memory" and dst_neuron[1] \
    #                     in runtime_data.brain["vision_IT"][src_neuron[1]]["neighbors"]:
    #                 apply_plasticity_ext(src_cortical_area='vision_IT', src_neuron_id=src_neuron[1],
    #                                      dst_cortical_area='vision_memory', dst_neuron_id=dst_neuron[1])
    #                 if runtime_data.parameters["Logs"]["print_plasticity_info"]:
    #                     print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWMWMWM"
    #                                                  "...........LTP between vision_IT and vision_memory occurred "
    #                           + settings.Bcolors.ENDC)
    #
    # # Long Term Depression (LTD) between vision_IT and vision_memory
    # for src_neuron in cfcl:
    #     if src_neuron[0] == "vision_IT":
    #         for dst_neuron in pfcl:
    #             if dst_neuron[0] == "vision_memory" and dst_neuron[1] \
    #                     in runtime_data.brain["vision_IT"][src_neuron[1]]["neighbors"]:
    #                 apply_plasticity_ext(src_cortical_area='vision_IT', src_neuron_id=src_neuron[1],
    #                                      dst_cortical_area='vision_memory', dst_neuron_id=dst_neuron[1],
    #                                      long_term_depression=True)
    #                 if runtime_data.parameters["Logs"]["print_plasticity_info"]:
    #                     print(settings.Bcolors.RED + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWWMWMWMWMWMWMWM"
    #                                                  "...........LTD between vision_IT and vision_memory occurred "
    #                           + settings.Bcolors.ENDC)

    # todo: The following loop is very inefficient___ fix it!!

    # Building the cell assemblies
    for cortical_area in runtime_data.memory_list:
        if runtime_data.genome['blueprint'][cortical_area]['location_generation_type'] == 'random':
            for src_neuron in set([i[1] for i in cfcl if i[0] == cortical_area]):
                for dst_neuron in set([j[1] for j in cfcl if j[0] == cortical_area]):
                    if src_neuron != dst_neuron:
                        apply_plasticity(cortical_area=cortical_area,
                                         src_neuron=src_neuron, dst_neuron=dst_neuron)
                        # print("...")

    # Detecting pain
    pain_flag = False
    for src_neuron in set([i[1] for i in cfcl if i[0] == 'pain']):
        pain_flag = True
        # print('^%@! Pain flag is set!')



    # Wiring Vision memory to UIF-8 memory when there is simultaneous firing of neurons in these regions
    for dst_neuron in cfcl:
        if dst_neuron[0] == "utf8_memory":
            # print(settings.Bcolors.RED + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>                                                 "
            #       "\nMika is cute!!.... .. .. .. .. .. .. .. .. .. .. .. .. " + settings.Bcolors.ENDC, '\n')
            for src_neuron in cfcl:
                if src_neuron[0] == "vision_memory":
                    # print("\n\n\n$ $$ $$$ $$ $ -  Pain flag is \n\n\n", pain_flag)
                    if not pain_flag:
                        apply_plasticity_ext(src_cortical_area='vision_memory', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='utf8_memory', dst_neuron_id=dst_neuron[1])

                        # print("-.-.-")

                        if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                            print(settings.Bcolors.UPDATE + "..........MWMWMWM-----Form memories-----WMWMWMWWMWMWMWMWMWMWM"
                                                         "..........LTP between vision_memory and UTF8_memory occurred "
                                  + settings.Bcolors.ENDC)
                            # print(cfcl)
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

                    if pain_flag:
                        apply_plasticity_ext(src_cortical_area='vision_memory', src_neuron_id=src_neuron[1],
                                             dst_cortical_area='utf8_memory', dst_neuron_id=dst_neuron[1],
                                             long_term_depression=True, impact_multiplier=10)

                        # print("-.-.-")

                        if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                            print(settings.Bcolors.RED + "..........WMWMWMWMW-----Form memories-----WMWWMWM--PAIN---WMWMWMWMWM"
                                                         "..........LTD between vision_memory and UTF8_memory occurred "
                                  + settings.Bcolors.ENDC)
                            # print(cfcl)
                            print("*************________**************")

    # Counting number of active UTF8_memory cells in the fire_candidate_list
    utf_mem_in_fcl = []
    for neuron in cfcl:
        if neuron[0] == 'utf8_memory':
            utf_mem_in_fcl.append(neuron[1])

    # Reducing synaptic strength when one vision memory cell activates more than one UTF cell
    if len(utf_mem_in_fcl) >= 2:
        for src_neuron in set([i[1] for i in pfcl if i[0] == 'vision_memory']):
            synapse_to_utf = 0
            runtime_data.temp_neuron_list = []
            neighbor_list = dict(runtime_data.brain['vision_memory'][src_neuron]['neighbors'])
            print("<><><>")
            for synapse_ in neighbor_list:
                if runtime_data.brain['vision_memory'][src_neuron]['neighbors'][synapse_]['cortical_area'] \
                        == 'utf8_memory':
                    synapse_to_utf += 1
                    runtime_data.temp_neuron_list.append(synapse_)
                if synapse_to_utf >= 2:
                    for dst_neuron in runtime_data.temp_neuron_list:
                        # print("$$$$ : LTD occurred between vision_memory and utf8_memory as over 2 UTF activated:",
                        #       src_neuron, runtime_data.brain['vision_memory'][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"],
                        #       dst_neuron, runtime_data.brain['vision_memory'][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"])
                        apply_plasticity_ext(src_cortical_area='vision_memory', src_neuron_id=src_neuron,
                                             dst_cortical_area='utf8_memory', dst_neuron_id=dst_neuron,
                                             long_term_depression=True, impact_multiplier=4)


                        # print(
                        #     settings.Bcolors.RED + "WMWMWMWMWMW-----Form memories-----MWMWMWMWM  > 2 UTF detected MWMWMWWMWMWMWMWMWMWM"
                        #                            "........LTD between vision_memory and UTF8_memory occurred "
                        #     + settings.Bcolors.ENDC)
                        # if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                        #     print(
                        #         settings.Bcolors.RED + "WMWMWMWMWMW-----Form memories-----MWMWMWMWM  > 2 UTF detected MWMWMWWMWMWMWMWMWMWM"
                        #                                "........LTD between vision_memory and UTF8_memory occurred "
                        #         + settings.Bcolors.ENDC)


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

            elif user_input_value == 'd':
                print('Dumping debug info...')
                print_cortical_neuron_mappings('vision_memory', 'utf8_memory')

        finally:
            runtime_data.parameters["Input"]["user_input"] = ''
            runtime_data.parameters["Input"]["user_input_param"] = ''
            break


def print_cortical_neuron_mappings(src_cortical_area, dst_cortical_area):
    print('Listing neuron mappings between %s and %s' % (src_cortical_area, dst_cortical_area))
    for neuron in runtime_data.brain[src_cortical_area]:
        for neighbor in runtime_data.brain[src_cortical_area][neuron]['neighbors']:
            if runtime_data.brain[src_cortical_area][neuron]['neighbors'][neighbor]['cortical_area'] == \
                    dst_cortical_area:
                print(settings.Bcolors.OKGREEN + '# ', neuron[27:], neighbor[27:],
                      str(runtime_data.brain[src_cortical_area][neuron]
                      ['neighbors'][neighbor]['postsynaptic_current']) + settings.Bcolors.ENDC)


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


def update_upstream_db(src_cortical_area, src_neuron_id, dst_cortical_area, dst_neuron_id):
    if dst_cortical_area not in runtime_data.upstream_neurons:
        runtime_data.upstream_neurons[dst_cortical_area] = {}
    if dst_neuron_id not in runtime_data.upstream_neurons[dst_cortical_area]:
        runtime_data.upstream_neurons[dst_cortical_area][dst_neuron_id] = {}
    if src_cortical_area not in runtime_data.upstream_neurons[dst_cortical_area][dst_neuron_id]:
        runtime_data.upstream_neurons[dst_cortical_area][dst_neuron_id][src_cortical_area] = set()
    if src_neuron_id not in runtime_data.upstream_neurons[dst_cortical_area][dst_neuron_id][src_cortical_area]:
        runtime_data.upstream_neurons[dst_cortical_area][dst_neuron_id][src_cortical_area].add(src_neuron_id)

def activation_function(postsynaptic_current):
    # print("PSC: ", postsynaptic_current)
    return postsynaptic_current

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
    activity_history_span = runtime_data.parameters["InitData"]["activity_history_span"]
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

    # Updating downstream neurons
    update_start_time = datetime.now()
    for dst_neuron_id in neighbor_list:
        if runtime_data.parameters["Verbose"]["neuron_functions-neuron_fire"]:
            print(settings.Bcolors.RED + 'Updating connectome for Neuron ' + dst_neuron_id + settings.Bcolors.ENDC)
        dst_cortical_area = runtime_data.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["cortical_area"]
        # print(".......................", dst_cortical_area, dst_neuron_id)
        # if dst_cortical_area == 'utf8_memory':
        #         print('--==--', dst_cortical_area, dst_neuron_id[27:], 'mp=',
        #               runtime_data.brain[dst_cortical_area][dst_neuron_id]["membrane_potential"])

        postsynaptic_current = runtime_data.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"]

        # # # # Debugging
        # if cortical_area == 'utf8':
        #     print("%%%%% %%%%% %%%%% post synaptic current for the utf neuron is:", postsynaptic_current)
        #     print(runtime_data.brain[cortical_area][neuron_id]["neighbors"])
        #     print("cortical area:", cortical_area)
        #     print("neuron id:", neuron_id)
        #     print("%%%%% %%%%% %%%%%")
        # # # # End of debugging

        neuron_output = activation_function(postsynaptic_current)
        neuron_update(dst_cortical_area, dst_neuron_id,
                      neuron_output,
                      neighbor_count)
        # Time overhead for the following function is about 2ms per each burst cycle
        update_upstream_db(cortical_area, neuron_id, dst_cortical_area, dst_neuron_id)
        # if dst_cortical_area == 'utf8_memory':
        #     print('--=+=--', dst_cortical_area, dst_neuron_id[27:], 'mp=',
        #           runtime_data.brain[dst_cortical_area][dst_neuron_id]["membrane_potential"])


        ### Partial implementation of neuro-plasticity associated with LTD or Long Term Depression
        pfcl = init_data.previous_fcl
        if [dst_cortical_area, dst_neuron_id] in pfcl and dst_cortical_area in ['vision_memory']:
            apply_plasticity_ext(src_cortical_area=cortical_area, src_neuron_id=neuron_id,
                                 dst_cortical_area=dst_cortical_area, dst_neuron_id=dst_neuron_id,
                                 long_term_depression=True)

            if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                print(settings.Bcolors.RED + "WMWMWM-------- Neuron Fire --------MWMWMWMWMWMWMWMWWMWMWMWMWMWMWMWMWM"
                                             "...........LTD between %s and %s occurred"
                      % (cortical_area, dst_cortical_area)
                      + settings.Bcolors.ENDC)

    # Adding up all update times within a burst span
    total_update_time = datetime.now() - update_start_time
    init_data.time_neuron_update = total_update_time + init_data.time_neuron_update

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

    # Removing the fired neuron from the FCL
    init_data.fire_candidate_list.pop(init_data.fire_candidate_list.index([cortical_area, neuron_id]))

    # print("FCL after fire pop: ", len(init_data.fire_candidate_list))
    # np.delete(init_data.fire_candidate_list, init_data.fire_candidate_list.index([cortical_area, neuron_id]))
    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_fire"]:
    #     print(settings.Bcolors.RED + "Fire Function triggered FCL: %s "
    #           % init_data.fire_candidate_list + settings.Bcolors.ENDC)

    # todo: add a check that if the firing neuron is part of OPU to perform an action

    return


def list_upstream_neurons(cortical_area, neuron_id):
    if cortical_area in runtime_data.upstream_neurons:
        if neuron_id in runtime_data.upstream_neurons[cortical_area]:
            return runtime_data.upstream_neurons[cortical_area][neuron_id]
    return {}


def list_top_n_utf_memory_neurons(n):
    neuron_list = []
    counter = ord('0')
    for neuron_id in runtime_data.brain['utf8_memory']:
        if int(runtime_data.brain['utf8_memory'][neuron_id]["location"][2]) == counter:
            neuron_list.append([int(runtime_data.brain['utf8_memory'][neuron_id]["location"][2])-48, neuron_id])
            counter += 1
    return neuron_list


def list_upstream_neuron_count_for_digits(digit='all'):
    function_start_time = datetime.now()
    results = []
    top_n_utf_memory_neurons = list_top_n_utf_memory_neurons(10)
    if digit == 'all':
        # print('top_n_utf_memory_neurons:\n', top_n_utf_memory_neurons, 'end of top_n_utf_memory_neurons')
        # if 'utf8_memory' in runtime_data.upstream_neurons:
        #     print('runtime_data.upstream_neurons:', runtime_data.upstream_neurons['utf8_memory'], 'end of runtime_data.upstream_neurons')
        for _ in range(10):
            # results.append([_, len(list_upstream_neurons('utf8_memory', list_top_n_utf_memory_neurons(10)[_][1]))])
            neuron_id = top_n_utf_memory_neurons[_][1]
            if 'utf8_memory' in runtime_data.upstream_neurons:
                if neuron_id in runtime_data.upstream_neurons['utf8_memory']:
                    if 'vision_memory' in runtime_data.upstream_neurons['utf8_memory'][neuron_id]:
                        results.append([_, len(runtime_data.upstream_neurons['utf8_memory'][neuron_id]['vision_memory'])])
                    else:
                        results.append([_, 0])
                else:
                    results.append([_, 0])
            else:
                results.append([_, 0])
    else:
        neuron_id = top_n_utf_memory_neurons[digit][1]
        if 'utf8_memory' in runtime_data.upstream_neurons:
            if neuron_id in runtime_data.upstream_neurons['utf8_memory']:
                if 'vision_memory' in runtime_data.upstream_neurons['utf8_memory'][neuron_id]:
                    results.append([digit, len(runtime_data.upstream_neurons['utf8_memory'][neuron_id]['vision_memory'])])
                else:
                    results.append([digit, 0])
            else:
                results.append([digit, 0])
        else:
            results.append([digit, 0])
    print("Timing : list_upstream_neuron_count_for_digits:", datetime.now()-function_start_time)
    return results


def list_common_upstream_neurons(neuron_a, neuron_b):
    common_neuron_list = []

    try:
        neuron_a_upstream_neurons = runtime_data.upstream_neurons['utf8_memory'][neuron_a]['vision_memory']
        neuron_b_upstream_neurons = runtime_data.upstream_neurons['utf8_memory'][neuron_b]['vision_memory']
        for neuron in neuron_a_upstream_neurons:
            if neuron in neuron_b_upstream_neurons:
                common_neuron_list.append(neuron)
        return common_neuron_list

    except:
        pass

def utf_neuron_id(n):
    # Returns the neuron id associated with a particular digit
    for neuron_id in runtime_data.brain['utf8_memory']:
        if int(runtime_data.brain['utf8_memory'][neuron_id]["location"][2]) == n+ord('0'):
            return neuron_id


def common_neuron_report():
    digits = range(10)
    number_matrix = []
    for _ in digits:
        for __ in digits:
            if _ != __ and [_, __] not in number_matrix and [__, _] not in number_matrix:
                number_matrix.append([_, __])
    for item in number_matrix:
        neuron_a = utf_neuron_id(item[0])
        neuron_b = utf_neuron_id(item[1])
        common_neuron_list = list_common_upstream_neurons(neuron_a, neuron_b)

        if common_neuron_list:
            overlap_amount = len(common_neuron_list)
            print(item, '> ', overlap_amount)

            if overlap_amount > runtime_data.parameters["InitData"]["overlap_prevention_constant"]:
                # The following action is taken to eliminate the overlap
                for neuron in common_neuron_list:
                    pruner('vision_memory', neuron, 'utf8_memory', neuron_a)
                    pruner('vision_memory', neuron, 'utf8_memory', neuron_b)


def neuron_update(cortical_area, dst_neuron_id, postsynaptic_current, neighbor_count):
    """This function updates the destination parameters upon upstream Neuron firing"""
    global init_data

    # # # # Debugging
    # if cortical_area == 'utf8_memory':
    #     print("* * * * * * * * * * * * * * UTF8 memory neuron is being updated")
    #     print("postsynaptic_current:", postsynaptic_current)
    #     print("neighbor_count:", neighbor_count)
    # # # # End of Debugging

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
    if last_membrane_potential_update < init_data.burst_count:
        leak_coefficient = runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["leak_coefficient"]
        leak_window = init_data.burst_count - last_membrane_potential_update
        leak_value = leak_window * leak_coefficient
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


    runtime_data.brain[cortical_area][dst_neuron_id]["membrane_potential"] += (postsynaptic_current / neighbor_count)

    # print("membrane_potential:", destination,
    #       ":", runtime_data.brain[cortical_area][destination]["membrane_potential"])

    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_update"]:
    #     print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value after update: %s" %
    #           (dst_neuron_id, dst_neuron_obj["membrane_potential"])
    #           + settings.Bcolors.ENDC)

    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # todo: Need to figure how to deal with Activation function and firing threshold (belongs to fire func)
    # The following will evaluate if the destination neuron is ready to fire and if so adds it to fire_candidate_list
    # if cortical_area == 'utf8_memory':
    #     print('&@@@: Testing fire eligibility', dst_neuron_id[27:], 'mp=',
    #           dst_neuron_obj["membrane_potential"], 'fire threshold=', dst_neuron_obj["firing_threshold"])
    if dst_neuron_obj["membrane_potential"] > dst_neuron_obj["firing_threshold"]:
        # # # # Debugging
        # if cortical_area == 'utf8_memory':
        #     print('&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%&^%: Fire condition has been met for', dst_neuron_id[27:])
        # # # # End of Debugging

        # Refractory period check
        if dst_neuron_obj["last_burst_num"] + \
                runtime_data.genome["blueprint"][cortical_area]["neuron_params"]["refractory_period"] <= \
                init_data.burst_count:
            # Inhibitory effect check
            if dst_neuron_obj["snooze_till_burst_num"] <= init_data.burst_count:
                # To prevent duplicate entries
                if init_data.fire_candidate_list.count([cortical_area, dst_neuron_id]) == 0:

                    # Adding neuron to fire candidate list for firing in the next round
                    init_data.fire_candidate_list.append([cortical_area, dst_neuron_id])

                    # # # # Debugging
                    # if cortical_area == 'utf8_memory':
                    #     print("* * * * * * * * * * * * * * >>>> >>> >>> >> >> > UTF8 memory neuron has been added to FCL: ", cortical_area, dst_neuron_id)
                    # # # # End of Debugging


                    ### This is an alternative approach to plasticity with hopefully less overhead
                    ### LTP or Long Term Potentiation occurs here

                    if runtime_data.parameters["Switches"]["plasticity"]:

                        pfcl = init_data.previous_fcl
                        cfcl = init_data.fire_candidate_list
                        upstream_data = list_upstream_neurons(cortical_area, dst_neuron_id)

                        if upstream_data:
                            for src_cortital_area in upstream_data:
                                for src_neuron in upstream_data[src_cortital_area]:
                                    if src_cortital_area != cortical_area and \
                                            [src_cortital_area, src_neuron] in pfcl:
                                        apply_plasticity_ext(src_cortical_area=src_cortital_area,
                                                             src_neuron_id=src_neuron,
                                                             dst_cortical_area=cortical_area,
                                                             dst_neuron_id=dst_neuron_id)
                                        # if runtime_data.parameters["Logs"]["print_plasticity_info"]:
                                        #     print(settings.Bcolors.OKGREEN + "WMWMWMW-------Neuron update----------MWMWMWMWMWMWWMWMWMWMWMWMWMWMWM"
                                        #                                  "...........LTP between %s and %s occurred"
                                        #           % (cortical_area, dst_neuron_id)
                                        #           + settings.Bcolors.ENDC)
                    ### End of plasticity implementation

                    # if cortical_area == 'utf8_memory':
                    #     print('Following neuron being added to FCL:', dst_neuron_id[27:])
                    # if runtime_data.parameters["Verbose"]["neuron_functions-neuron_update"]:
                    #     print(settings.Bcolors.UPDATE +
                    #           "    Update Function triggered FCL: %s " % init_data.fire_candidate_list
                    #           + settings.Bcolors.ENDC)
            # elif cortical_area == 'utf8_memory':
            #     print('SSSS SSS SS S ...  Neuron was prevented from being added to FCL due to Snooze condition')

    # else:
    #     if cortical_area == 'utf8_memory':
    #         print("--------- ----- --- ---- --- Threshold was not met - --- ----- --- - - - - - -")
    #         print("membrane_potential:", dst_neuron_obj["membrane_potential"])
    #         print("firing_threshold:", dst_neuron_obj["firing_threshold"])

    # Resetting last time neuron was updated to the current burst id
    runtime_data.brain[cortical_area][dst_neuron_id]["last_burst_num"] = init_data.burst_count


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
        update_upstream_db(cortical_area, src_neuron, cortical_area, dst_neuron)

    # Every time source and destination neuron is fired at the same time which in case of the code architecture
    # reside in the same burst, the postsynaptic_current will be increased simulating the fire together, wire together.
    # This phenomenon is also considered as long term potentiation or LTP
    runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"] += \
        genome["blueprint"][cortical_area]["plasticity_constant"]

    # Condition to cap the postsynaptic_current and provide prohibitory reaction
    runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"] = \
        min(runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"],
            genome["blueprint"][cortical_area]["postsynaptic_current_max"])

    # print('<*> ', cortical_area, src_neuron[27:], dst_neuron[27:], 'PSC=',
    #       runtime_data.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["postsynaptic_current"])

    # Append a Group ID so Memory clusters can be uniquely identified
    if init_data.event_id:
        if init_data.event_id in runtime_data.brain[cortical_area][src_neuron]["event_id"]:
            runtime_data.brain[cortical_area][src_neuron]["event_id"][init_data.event_id] += 1
        else:
            runtime_data.brain[cortical_area][src_neuron]["event_id"][init_data.event_id] = 1

    return


def apply_plasticity_ext(src_cortical_area, src_neuron_id, dst_cortical_area,
                         dst_neuron_id, long_term_depression=False, impact_multiplier=1):

    genome = runtime_data.genome
    plasticity_constant = genome["blueprint"][src_cortical_area]["plasticity_constant"]

    if long_term_depression:
        # When long term depression flag is set, there will be negative synaptic influence caused
        plasticity_constant = plasticity_constant * (-1) * impact_multiplier
        # plasticity_constant = -20

        # Check if source and destination have an existing synapse if not create one here
    if dst_neuron_id not in runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"]:
        synapse(src_cortical_area, src_neuron_id, dst_cortical_area, dst_neuron_id, max(plasticity_constant, 0))
        update_upstream_db(src_cortical_area, src_neuron_id, dst_cortical_area, dst_neuron_id)

    runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"] += \
        plasticity_constant

    # Condition to cap the postsynaptic_current and provide prohibitory reaction
    runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"] = \
        min(runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"],
            genome["blueprint"][src_cortical_area]["postsynaptic_current_max"])

    # Condition to prevent postsynaptic current to become negative
    # todo: consider setting a postsynaptic_min in genome to be used instead of 0
    runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"] = \
        max(runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"], 0)

    # Condition to prune a synapse if its postsynaptic_current is zero
    if runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"] == 0:
        pruner(cortical_area_src=src_cortical_area, src_neuron_id=src_neuron_id,
               cortical_area_dst=dst_cortical_area , dst_neuron_id=dst_neuron_id)


    # print('<**> ', src_cortical_area, src_neuron_id[27:], dst_cortical_area, dst_neuron_id[27:], 'PSC=',
    #       runtime_data.brain[src_cortical_area][src_neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"])

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

def trigger_pain():

    print("*******************************************************************")
    print("*******************************************************************")
    print("*********************                                 *************")
    print("*******************    Pain -- Pain -- Pain -- Pain     ***********")
    print("*********************                                 *************")
    print("*******************************************************************")
    print("*******************************************************************")

    for neuron in runtime_data.brain['pain']:
        init_data.fire_candidate_list.append(['pain', neuron])


def pruner(cortical_area_src, src_neuron_id, cortical_area_dst, dst_neuron_id):
    """
    Responsible for pruning unused connections between neurons
    """
    runtime_data.brain[cortical_area_src][src_neuron_id]['neighbors'].pop(dst_neuron_id, None)
    runtime_data.upstream_neurons[cortical_area_dst][dst_neuron_id][cortical_area_src].remove(src_neuron_id)
    if dst_neuron_id in runtime_data.temp_neuron_list:
        runtime_data.temp_neuron_list.remove(dst_neuron_id)

