
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
from architect import synapse
from PUs import OPU_utf8
import genethesizer
from configuration import settings
from misc import universal_functions as uf, stats, visualizer

if uf.parameters["Switches"]["vis_show"]:
    pass

global burst_count
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
    uf.event_id = event_queue.get()
    uf.brain = brain_queue.get()
    # my_brain = uf.brain
    verbose = uf.parameters["Switches"]["verbose"]

    while not uf.parameters["Switches"]["ready_to_exit_burst"]:
        burst_start_time = datetime.datetime.now()
        global burst_count

        print(datetime.datetime.now(), "Burst count = ", burst_count, file=open("./logs/burst.log", "a"))

        # List of Fire candidates are placed in global variable fire_candidate_list to be passed for next Burst
        global fire_candidate_list

        # Read FCL from the Multiprocessing Queue
        fire_candidate_list = fire_list.get()
        previous_fcl = list(fire_candidate_list)

        # todo: preserve fcl-1 and use that for LTP/LTD between memory and vision_IT

        # Burst Visualization
        if len(fire_candidate_list) > 0 and uf.parameters["Switches"]["vis_show"]:
            visualizer.burst_visualizer(fire_candidate_list)

        # genome = uf.genome

        if verbose:
            print(settings.Bcolors.BURST + 'Current fire_candidate_list is %s'
                  % fire_candidate_list + settings.Bcolors.ENDC)

        burst_count += 1
        # Figure what you were thinking on the following
        if burst_count % uf.genome['evolution_burst_count'] == 0:
            print('Evolution phase reached...')
            genethesizer.generation_assessment()

        brain_neuron_count, brain_synapse_count = stats.brain_total_synapse_cnt(verbose=False)
        print(settings.Bcolors.BURST +
              'Burst count = %i  --  Neuron count in FCL is %i  -- Total brain synapse count is %i'
              % (burst_count, len(fire_candidate_list), brain_synapse_count) + settings.Bcolors.ENDC)

        for cortical_area in set([i[0] for i in fire_candidate_list]):
            print(settings.Bcolors.BURST + '    %s : %i  '
                  % (cortical_area, len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])))
                  + settings.Bcolors.ENDC)
            if uf.genome['blueprint'][cortical_area]['group_id'] == 'Memory' \
                    and len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])) > 0:
                sleep(uf.parameters["Timers"]["idle_burst_timer"])

        # todo: Look into multi-threading for Neuron neuron_fire and wire_neurons function

        for x in list(fire_candidate_list):
            if verbose:
                print(settings.Bcolors.BURST + 'Firing Neuron: ' + x[1] + ' from ' + x[0] + settings.Bcolors.ENDC)
            neuron_fire(x[0], x[1], verbose=verbose)

        # for cortical_area in set([i[0] for i in fire_candidate_list]):
        #     for src_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
        #         for dst_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
        #             if src_neuron != dst_neuron:
        #                 wire_neurons_together(cortical_area=cortical_area,
        #                                       src_neuron=src_neuron, dst_neuron=dst_neuron)
        #

        # ## The following section is related to neuro-plasticity ## #

        print(len(previous_fcl), len(fire_candidate_list))

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

                        print(settings.Bcolors.FIRE + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWM"
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

                        print(settings.Bcolors.FIRE + "WMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWMWM"
                                                      "...........LTD between vision_IT and vision_memory occurred "
                              + settings.Bcolors.ENDC)

        # Building a bidirectional synapse between memory neurons who fire together within a cortical area
        # todo: The following loop is very inefficient___ fix it!!
        # todo: Read the following memory list from Genome
        memory_list = ['utf8_memory', 'vision_memory']
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

                        print(settings.Bcolors.FIRE + "..............................................................."
                                                      "...........A new memory was formed against utf8_memory location "
                              + OPU_utf8.convert_neuron_acticity_to_utf8_char('utf8_memory',
                                                                              dst_neuron[1]) + settings.Bcolors.ENDC)
                        # dst_neuron_id_list = neighbor_finder_ext('utf8_memory', 'utf8_out', _[1], 'rule_3', 0)
                        # for dst_neuron_id in dst_neuron_id_list:
                        #     wire_neurons_together_ext(src_cortical_area='vision_memory', src_neuron=neuron[1],
                        #                               dst_cortical_area='utf8_out', dst_neuron=dst_neuron_id)

        burst_duration = datetime.datetime.now() - burst_start_time
        print(">>> Burst duration: %s" % burst_duration)

        # Push back updated fire_candidate_list into FCL from Multiprocessing Queue
        fire_list.put(fire_candidate_list)

        # Add a delay if fire_candidate_list is empty
        if len(fire_candidate_list) < 1:
            sleep(uf.parameters["Timers"]["idle_burst_timer"])

        while not user_input.empty():
            try:
                user_input_value = user_input.get()
                print("User input value is ", user_input_value)
                if user_input_value == 'x':
                    print(settings.Bcolors.BURST + '>>>Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
                    burst_count = 0
                    uf.parameters["Switches"]["ready_to_exit_burst"] = True
                    uf.parameters["Input"]["user_input"] = ''
                elif user_input_value == 'v':
                    if verbose:
                        uf.parameters["Switches"]["verbose"] = False
                        print("Verbose mode is Turned OFF!")
                        uf.parameters["Input"]["user_input"] = ''
                    else:
                        uf.parameters["Switches"]["verbose"] = True
                        print("Verbose mode is Turned ON!")
                        uf.parameters["Input"]["user_input"] = ''

                elif user_input_value == 'g':
                    if verbose:
                        uf.parameters["Switches"]["vis_show"] = False
                        print("Visualization mode is Turned OFF!")
                        uf.parameters["Input"]["user_input"] = ''
                    else:
                        uf.parameters["Switches"]["vis_show"] = True
                        print("Visualization mode is Turned ON!")
                        uf.parameters["Input"]["user_input"] = ''

            finally:
                break
    # Push updated brain data back to the queue
    brain_queue.put(uf.brain)


#  >>>>>> Review this function against what we had in past
def fire_candidate_locations(fire_cnd_list):
    """Extracts Neuron locations from the fire_candidate_list"""

    print('***')
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


def neuron_fire(cortical_area, neuron_id, verbose=False):
    """This function initiate the firing of Neuron in a given cortical area"""
    if uf.parameters["Switches"]["logging_fire"]:
        print(datetime.datetime.now(), " Firing...", cortical_area, neuron_id, file=open("./logs/fire.log", "a"))

    global burst_count

    # Setting Destination to the list of Neurons connected to the firing Neuron
    neighbor_list = uf.brain[cortical_area][neuron_id]["neighbors"]
    if uf.parameters["Switches"]["logging_fire"]:
        print(datetime.datetime.now(), "      Neighbors...", neighbor_list, file=open("./logs/fire.log", "a"))
    if verbose:
        print(settings.Bcolors.FIRE +
              "Firing neuron %s using firing pattern %s" %
              (neuron_id, json.dumps(uf.brain[cortical_area][neuron_id]["firing_pattern_id"], indent=3)) +
              settings.Bcolors.ENDC)
        print(settings.Bcolors.FIRE + "Neuron %s neighbors are %s" % (neuron_id, json.dumps(neighbor_list, indent=3)) +
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
        if verbose:
            print(settings.Bcolors.FIRE + 'Updating connectome for Neuron ' + dst_neuron_id + settings.Bcolors.ENDC)
        dst_cortical_area = uf.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["cortical_area"]
        neuron_update(dst_cortical_area, dst_neuron_id,
                      uf.brain[cortical_area][neuron_id]["neighbors"][dst_neuron_id]["postsynaptic_current"],
                      verbose=verbose)

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
        print("UTF8 out was stimulated with the following character:    "
              "                            <<<     %s      >>>                 #*#*#*#*#*#*#"
              % uf.parameters["Input"]["comprehended_char"])

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
    if verbose:
        print(settings.Bcolors.FIRE + "Fire Function triggered FCL: %s " % fire_candidate_list + settings.Bcolors.ENDC)

    # todo: add a check that if the firing neuron is part of OPU to perform an action

    return


def neuron_update(cortical_area, dst_neuron_id, postsynaptic_current, verbose=False):
    """This function updates the destination parameters upon upstream Neuron firing"""

    dst_neuron_obj = uf.brain[cortical_area][dst_neuron_id]

    # update the cumulative_intake_total, cumulative_intake_count and postsynaptic_current between source and
    # destination neurons based on XXX algorithm. The source is considered the Axon of the firing neuron and
    # destination is the dendrite of the neighbor.

    if verbose:
        print("Update request has been processed for: ", cortical_area, dst_neuron_id, " >>>>>>>>> >>>>>>> >>>>>>>>>>")
        print(settings.Bcolors.UPDATE +
              "%s's Cumulative_intake_count value before update: %s" %
              (dst_neuron_id, dst_neuron_obj["membrane_potential"])
              + settings.Bcolors.ENDC)

    # todo: Need to tune up the timer as depending on the application performance the timer could be always expired
    # Check if timer is expired on the destination Neuron and if so reset the counter - Leaky behavior
    # todo: Given time is quantized in this implementation, instead of absolute time need to consider using burst cnt.
    # todo: in rare cases the date conversion format is running into exception
    # if (datetime.datetime.strptime(uf.brain[cortical_area]
    #                                        [dst_neuron_id]["last_membrane_potential_reset_time"], "%Y-%m-%d %H:%M:%S.%f")
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
        if verbose:
            print(settings.Bcolors.UPDATE + 'Cumulative counters for Neuron ' + dst_neuron_id +
                  ' got rest' + settings.Bcolors.ENDC)

    # Increasing the cumulative counter on destination based on the received signal from upstream Axon
    # The following is considered as LTP or Long Term Potentiation of Neurons
    uf.brain[cortical_area][dst_neuron_id]["membrane_potential"] += postsynaptic_current

    # print("membrane_potential:", destination,
    #       ":", uf.brain[cortical_area][destination]["membrane_potential"])

    if verbose:
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
                if verbose:
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
        neuron_update(src_cortical_area, src_neuron_id, plasticity_constant, verbose=False)

    return


def snooze_till(cortical_area, neuron_id, burst_id):
    """ Acting as an inhibitory neurotransmitter to suppress firing of neuron till a later burst

    *** This function instead of inhibitory behavior is more inline with Neuron Refractory period

    """
    uf.brain[cortical_area][neuron_id]["snooze_till_burst_num"] \
        = burst_id + uf.genome["blueprint"][cortical_area]["neuron_params"]["snooze_length"]
    # print("%s : %s has been snoozed!" % (cortical_area, neuron_id))
    return
