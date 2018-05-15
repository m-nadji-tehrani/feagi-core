
"""
This Library contains various functions simulating human cortical behaviors
Function list:
neuron:           This function is triggered as a Neuron instance and stays up for period of time
                  till Neuron is fired
neuron_prop:      Returns the properties for a given neuron
neuron_neighbors: Reruns the list of neighbors for a given neuron
"""

import json
import datetime
from time import sleep
# import multiprocessing as mp
# import subprocess

import universal_functions

if universal_functions.parameters["Switches"]["vis_show"]:
    import visualizer

from architect import synapse, neighbor_finder_ext
import OPU_utf8
import genethesizer
import settings

burst_count = 0


def burst(user_input, fire_list, brain_queue, event_queue):
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
    universal_functions.event_id = event_queue.get()
    universal_functions.brain = brain_queue.get()

    while not universal_functions.parameters["Switches"]["ready_to_exit_burst"]:
        burst_strt_time = datetime.datetime.now()
        global burst_count

        # List of Fire candidates are placed in global variable fire_candidate_list to be passed for next Burst
        global fire_candidate_list

        # Read FCL from the Multiprocessing Queue
        fire_candidate_list = fire_list.get()

        # Burst Visualization
        if len(fire_candidate_list) > 0 and universal_functions.parameters["Switches"]["vis_show"]:
            visualizer.burst_visualizer(fire_candidate_list)

        genome = universal_functions.genome

        if universal_functions.parameters["Switches"]["verbose"]:
            print(settings.Bcolors.BURST + 'Current fire_candidate_list is %s'
                  % fire_candidate_list + settings.Bcolors.ENDC)

        burst_count += 1
        # Figure what you were thiking on the following
        if burst_count % universal_functions.genome['evolution_burst_count'] == 0:
            print('Evolution phase reached...')
            genethesizer.generation_assessment()

        print(settings.Bcolors.BURST + 'Burst count = %i  --  Neuron count in FCL is %i'
              % (burst_count, len(fire_candidate_list)) + settings.Bcolors.ENDC)

        for cortical_area in set([i[0] for i in fire_candidate_list]):
            print(settings.Bcolors.BURST + '    %s : %i  '
                  % (cortical_area, len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])))
                  + settings.Bcolors.ENDC)
            if universal_functions.genome['blueprint'][cortical_area]['group_id'] == 'Memory' and \
                            len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])) > 0:
                sleep(universal_functions.parameters["Timers"]["idle_burst_timer"])

        # todo: Look into multi-threading for Neuron neuron_fire and wire_neurons function

        for x in list(fire_candidate_list):
            if universal_functions.parameters["Switches"]["verbose"]:
                print(settings.Bcolors.BURST + 'Firing Neuron: ' + x[1] + ' from ' + x[0] + settings.Bcolors.ENDC)
            neuron_fire(x[0], x[1])

        # for cortical_area in set([i[0] for i in fire_candidate_list]):
        #     for src_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
        #         for dst_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
        #             if src_neuron != dst_neuron:
        #                 wire_neurons_together(cortical_area=cortical_area,
        #                                       src_neuron=src_neuron, dst_neuron=dst_neuron)
        #

        # Building a bidirectional synapse between memory neurons who fire together within a cortical area
        # todo: Read the following memory list from Genome
        memory_list = ['utf8_memory', 'vision_memory']
        for cortical_area in memory_list:
            if universal_functions.genome['blueprint'][cortical_area]['location_generation_type'] == 'random':
                for src_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
                    for dst_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
                        if src_neuron != dst_neuron:
                            wire_neurons_together(cortical_area=cortical_area, src_neuron=src_neuron, dst_neuron=dst_neuron)

        # Wiring Vision memory to UIF-8 memory
        for _ in fire_candidate_list:
            if _[0] == "utf8_memory":
                for neuron in fire_candidate_list:
                    if neuron[0] == "vision_memory":
                        wire_neurons_together_ext(src_cortical_area='vision_memory', src_neuron=neuron[1],
                                                  dst_cortical_area='utf8_memory', dst_neuron=_[1])

                        print(settings.Bcolors.FIRE + "..........................................................................A new memory was formed against utf8_memory location "
                              + OPU_utf8.convert_neuron_acticity_to_utf8_char('utf8_memory', _[1]) + settings.Bcolors.ENDC)
                        # dst_neuron_id_list = neighbor_finder_ext('utf8_memory', 'utf8_out', _[1], 'rule_3', 0)
                        # for dst_neuron_id in dst_neuron_id_list:
                        #     wire_neurons_together_ext(src_cortical_area='vision_memory', src_neuron=neuron[1],
                        #                               dst_cortical_area='utf8_out', dst_neuron=dst_neuron_id)

        burst_duration = datetime.datetime.now() - burst_strt_time
        print(">>> Burst duration: %s" % burst_duration)

        # Push back updated fire_candidate_list into FCL from Multiprocessing Queue
        fire_list.put(fire_candidate_list)

        # Add a delay if fire_candidate_list is empty
        if len(fire_candidate_list) < 1:
            sleep(universal_functions.parameters["Timers"]["idle_burst_timer"])

        while not user_input.empty():
            try:
                user_input_value = user_input.get()
                print("User input value is ", user_input_value)
                if user_input_value == 'x':
                    print(settings.Bcolors.BURST + '>>>Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
                    burst_count = 0
                    universal_functions.parameters["Switches"]["ready_to_exit_burst"] = True
                    universal_functions.parameters["Input"]["user_input"] = ''
                elif user_input_value == 'v':
                    if universal_functions.parameters["Switches"]["verbose"]:
                        universal_functions.parameters["Switches"]["verbose"] = False
                        print("Verbose mode is Turned OFF!")
                        universal_functions.parameters["Input"]["user_input"] = ''
                    else:
                        universal_functions.parameters["Switches"]["verbose"] = True
                        print("Verbose mode is Turned ON!")
                        universal_functions.parameters["Input"]["user_input"] = ''

                elif user_input_value == 'g':
                    if universal_functions.parameters["Switches"]["verbose"]:
                        universal_functions.parameters["Switches"]["vis_show"] = False
                        print("Visualization mode is Turned OFF!")
                        universal_functions.parameters["Input"]["user_input"] = ''
                    else:
                        universal_functions.parameters["Switches"]["vis_show"] = True
                        print("Visualization mode is Turned ON!")
                        universal_functions.parameters["Input"]["user_input"] = ''

            finally:
                break
    # Push updated brain data back to the queue
    brain_queue.put(universal_functions.brain)


#  >>>>>> Review this function against what we had in past
def fire_candidate_locations(fire_candidate_list):
    """Extracts Neuron locations from the fire_candidate_list"""

    print('***')
    # print(fire_candidate_list)

    neuron_locations = {}
    # Generate a dictionary of cortical areas in the fire_candidate_list
    for item in universal_functions.cortical_areas:
        neuron_locations[item] = []

    # Add neuron locations under each cortical area
    for item in fire_candidate_list:
        neuron_locations[item[0]].append([universal_functions.brain[item[0]][item[1]]["location"][0],
                                                universal_functions.brain[item[0]][item[1]]["location"][1],
                                                universal_functions.brain[item[0]][item[1]]["location"][2]])

    return neuron_locations


def neuron_fire(cortical_area, id):
    """This function initiate the firing of Neuron in a given cortical area"""

    global burst_count

    mybrain = universal_functions.brain

    # Setting Destination to the list of Neurons connected to the firing Neuron
    destination = universal_functions.brain[cortical_area][id]["neighbors"]
    if universal_functions.parameters["Switches"]["verbose"]:
        print(settings.Bcolors.FIRE + "Firing neuron %s using firing pattern %s"
          % (id, json.dumps(universal_functions.brain[cortical_area][id]["firing_pattern_id"], indent=3)) + settings.Bcolors.ENDC)
        print(settings.Bcolors.FIRE + "Neuron %s neighbors are %s" % (id, json.dumps(destination, indent=3)) +
              settings.Bcolors.ENDC)

    # After neuron fires all cumulative counters on Source gets reset
    universal_functions.brain[cortical_area][id]["cumulative_intake_sum_since_reset"] = 0
    universal_functions.brain[cortical_area][id]["last_timer_reset_time"] = str(datetime.datetime.now())
    universal_functions.brain[cortical_area][id]["cumulative_fire_count"] += 1
    universal_functions.brain[cortical_area][id]["cumulative_fire_count_inst"] += 1

    # Transferring the signal from firing Neuron's Axon to all connected Neuron Dendrites
    # Firing pattern to be accommodated here     <<<<<<<<<<  *****
    neuron_update_list = []
    for x in destination:
        # if universal_functions.parameters["Switches"]["verbose"]:
        print(settings.Bcolors.FIRE + 'Updating connectome for Neuron ' + x + settings.Bcolors.ENDC)
        neuron_update(universal_functions.brain[cortical_area][id]["neighbors"][x]["cortical_area"],
                      universal_functions.brain[cortical_area][id]["neighbors"][x]["synaptic_strength"], x)

    # Placeholder for refractory period
    # todo: Implement refractory period logic

    # Condition to snooze the neuron if consecutive fire count reaches threshold
    if universal_functions.brain[cortical_area][id]["consecutive_fire_cnt"] > \
            universal_functions.genome["blueprint"][cortical_area]["neuron_params"]["consecutive_fire_cnt_max"]:
        snooze_till(cortical_area, id, burst_count +
                    universal_functions.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"])

    # Condition to increase the consecutive fire count
    if burst_count == universal_functions.brain[cortical_area][id]["last_burst_num"] + 1:
        universal_functions.brain[cortical_area][id]["consecutive_fire_cnt"] += 1

    universal_functions.brain[cortical_area][id]["last_burst_num"] = burst_count

    # Condition to translate activity in utf8_out region as a character comprehension
    if cortical_area == 'utf8_out':
        universal_functions.parameters["Input"]["comprehended_char"] = OPU_utf8.convert_neuron_acticity_to_utf8_char(cortical_area, id)
        print("Comprehended character is:                 <<<     %s      >>>                 #*#*#*#*#*#*#"
              % universal_functions.parameters["Input"]["comprehended_char"])

    #     neuron_update_list.append([universal_functions.brain[cortical_area][id]["neighbors"][x]["cortical_area"],
        # universal_functions.brain[cortical_area][id]["neighbors"][x]["synaptic_strength"], x])
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
    fire_candidate_list.pop(fire_candidate_list.index([cortical_area, id]))
    # np.delete(fire_candidate_list, fire_candidate_list.index([cortical_area, id]))
    if universal_functions.parameters["Switches"]["verbose"]:
        print(settings.Bcolors.FIRE + "Fire Function triggered FCL: %s " % fire_candidate_list + settings.Bcolors.ENDC)

    # todo: add a check that if the firing neuron is part of OPU to perform an action

    return


def neuron_update(cortical_area, synaptic_strength, destination):
    """This function updates the destination parameters upon upstream Neuron firing"""

    # update the cumulative_intake_total, cumulative_intake_count and synaptic_strength between source and
    # destination neurons based on XXX algorithm. The source is considered the Axon of the firing neuron and
    # destination is the dendrite of the neighbor.

    print("Update request has been processed for: ", cortical_area, destination, " >>>>>>>>> >>>>>>> >>>>>>>>>>")

    if universal_functions.parameters["Switches"]["verbose"]:
        print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value before update: %s"
          % (destination, universal_functions.brain[cortical_area][destination]["cumulative_intake_sum_since_reset"])
              + settings.Bcolors.ENDC)

    # todo: Need to tune up the timer as depending on the application performance the timer could be always expired
    # Check if timer is expired on the destination Neuron and if so reset the counter
    # todo: in rare cases the date conversion format is running into exception
    if (datetime.datetime.strptime(universal_functions.brain[cortical_area][destination]["last_timer_reset_time"],
                                   "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(0,
                                                                                universal_functions.brain[cortical_area][destination]["depolarization_timer_threshold"])) < datetime.datetime.now():
        universal_functions.brain[cortical_area][destination]["last_timer_reset_time"] = str(datetime.datetime.now())
        universal_functions.brain[cortical_area][destination]["cumulative_intake_sum_since_reset"] = 0  # Might be better to have a reset func.
        if universal_functions.parameters["Switches"]["verbose"]:
            print(settings.Bcolors.UPDATE + 'Cumulative counters for Neuron ' + destination +
                  ' got rest' + settings.Bcolors.ENDC)

    # Increasing the cumulative counter on destination based on the received signal from upstream Axon
    # The following is considered as LTP or Long Term Potentiation of Neurons
    universal_functions.brain[cortical_area][destination]["cumulative_intake_sum_since_reset"] += synaptic_strength

    # print("cumulative_intake_sum_since_reset:", destination,
    #       ":", universal_functions.brain[cortical_area][destination]["cumulative_intake_sum_since_reset"])

    if universal_functions.parameters["Switches"]["verbose"]:
        print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value after update: %s"
          % (destination, universal_functions.brain[cortical_area][destination]["cumulative_intake_sum_since_reset"])
              + settings.Bcolors.ENDC)

    # Add code to start a timer when neuron first receives a signal and reset counters when its expired

    # Need to call the Fire function if the threshold on the destination Neuron is met  <<<<<<<<<<<  ********
    # Need to figure how to deal with Activation function and firing threshold
    # Pass the cumulative_intake_total through the activation function and if pass the condition
    # fire destination neuron

    # The following will evaluate if the destination neuron is ready to fire and if so adds it to
    # fire_candidate_list
    global fire_candidate_list
    global burst_count
    if universal_functions.brain[cortical_area][destination]["cumulative_intake_sum_since_reset"] > \
            universal_functions.brain[cortical_area][destination]["firing_threshold"]:
        if universal_functions.brain[cortical_area][destination]["snooze_till_burst_num"] <= burst_count:
           if fire_candidate_list.count([cortical_area, destination]) == 0:   # To prevent duplicate entries
                fire_candidate_list.append([cortical_area, destination])
                if universal_functions.parameters["Switches"]["verbose"]:
                    print(settings.Bcolors.UPDATE + "    Update Function triggered FCL: %s " % fire_candidate_list
                          + settings.Bcolors.ENDC)

    return fire_candidate_list


def neuron_prop(cortical_area, id):
    """This function accepts neuron id and returns neuron properties"""

    data = universal_functions.brain[cortical_area]

    if universal_functions.parameters["Switches"]["verbose"]:
        print('Listing Neuron Properties for %s:' % id)
        print(json.dumps(data[id], indent=3))
    return data[id]


def neuron_neighbors(cortical_area, id):
    """This function accepts neuron id and returns the list of Neuron neighbors"""

    data = universal_functions.brain[cortical_area]

    if universal_functions.parameters["Switches"]["verbose"]:
        print('Listing Neuron Neighbors for %s:' % id)
        print(json.dumps(data[id]["neighbors"], indent=3))
    return data[id]["neighbors"]


def wire_neurons_together(cortical_area, src_neuron, dst_neuron):
    """
    This function simulates neuron plasticity in a sense that when neurons in a given cortical area fire in the 
     same burst they wire together. This is done by increasing the synaptic_strength associated with a link between 
     two neuron. Additionally an event id is associated to the neurons who have fired together.
    """

    genome = universal_functions.genome

    # Since this function only targets Memory regions and neurons in memory regions do not have neighbor relationship
    # by default hence here we first need to synapse the source and destination together
    # Build neighbor relationship between the source and destination if its not already in place
    # Check if source and destination have an existing synapse if not create one here
    if dst_neuron not in universal_functions.brain[cortical_area][src_neuron]["neighbors"]:
        synapse(cortical_area, src_neuron, cortical_area, dst_neuron,
                genome["blueprint"][cortical_area]["synaptic_strength"])

    # Every time source and destination neuron is fired at the same time which in case of the code architecture
    # reside in the same burst, the synaptic_strength will be increased simulating Fire together, wire together.
    universal_functions.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["synaptic_strength"] += \
        genome["blueprint"][cortical_area]["synaptic_strength_inc"]

    # Condition to cap the synaptic_strength and provide prohibitory reaction (Serotonin)
    universal_functions.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["synaptic_strength"] = \
        min(universal_functions.brain[cortical_area][src_neuron]["neighbors"][dst_neuron]["synaptic_strength"],
            genome["blueprint"][cortical_area]["synaptic_strength_max"])

    # Append a Group ID so Memory clusters can be uniquely identified
    if universal_functions.event_id:
        if universal_functions.event_id in universal_functions.brain[cortical_area][src_neuron]["event_id"]:
            universal_functions.brain[cortical_area][src_neuron]["event_id"][universal_functions.event_id] +=1
        else:
            universal_functions.brain[cortical_area][src_neuron]["event_id"][universal_functions.event_id] = 1

    return


def wire_neurons_together_ext(src_cortical_area, src_neuron, dst_cortical_area, dst_neuron):

    genome = universal_functions.genome

    synapse(src_cortical_area, src_neuron, dst_cortical_area, dst_neuron,
            genome["blueprint"][src_cortical_area]["synaptic_strength_inc"])

    return


def snooze_till(cortical_area, neuron_id, burst_id):
    """ Acting as an inhibitory neurotransmitter to suppress firing of neuron till a later burst

    *** This function instead of inhibitory behavior is more inline with Neuron Refractory period

    """
    universal_functions.brain[cortical_area][neuron_id]["snooze_till_burst_num"] \
        = burst_id + universal_functions.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"]
    # print("%s : %s has been snoozed!" % (cortical_area, neuron_id))
    return
