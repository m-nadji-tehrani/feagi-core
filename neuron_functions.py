
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
from multiprocessing.dummy import Pool as ThreadPool

import visualizer
# import IPU_text
import settings
from architect import synapse
import time
import multiprocessing as mp


# Global variables
burst_count = 0


def burst(fire_list):
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
    # Exit condition:
    #     -When Max number of hops has been reached which could be set to 100 simulating the Brain ~100 steps limit.
    #     -When input vector is empty
    # Important:
    #     Need to account for recursive function call which could potentially be infinite.
    # Todo_list:
    #     -Figure the input format. Maybe a JSON

    # Function exit Check on whether number of recursive calls has met or fire_candidate_list is empty.

    # todo: figure burst count in this new model where burst is not limited to a single cortical area

    burst_strt_time = datetime.datetime.now()
    global burst_count
    global fire_candidate_list
    fire_candidate_list = fire_list

    genome = settings.genome

    if settings.verbose:
        print(settings.Bcolors.BURST + 'Current fire_candidate_list is %s' % fire_candidate_list + settings.Bcolors.ENDC)

    # Burst Exit criteria
    # if IPU_text.user_input == 'q':
    #     print(settings.Bcolors.BURST + '>>>   Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
    #     burst_count = 0                 # Shoudnt this be settings.burst_count   ????
    #     settings.save_brain_to_disk()
    #     return

    # if (fire_candidate_list == []) or (burst_count > genome["max_burst_count"]):
    #     print(settings.Bcolors.BURST + '>>>   Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
    #     burst_count = 0
    #     settings.save_brain_to_disk()
    #     return

    if burst_count > genome["max_burst_count"]:
        print(settings.Bcolors.BURST + '>>>   Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
        burst_count = 0
        settings.save_brain_to_disk()
        return



    # List of Fire candidates are placed in global variable fire_candidate_list to be passed for next Burst

    burst_count += 1
    print(settings.Bcolors.BURST + 'Burst count = %i  --  Neuron count in FLC is %i'
          % (burst_count, len(fire_candidate_list)) + settings.Bcolors.ENDC)
    for cortical_area in set([i[0] for i in fire_candidate_list]):
        print(settings.Bcolors.BURST +
              '    %s : %i  ' % (cortical_area, len(set([i[1] for i in fire_candidate_list if i[0] == cortical_area])))
              + settings.Bcolors.ENDC)
    # todo: Look into multithreading for Neuron neuron_fire and wire_neurons function
    for x in list(fire_candidate_list):
        if settings.verbose:
            print(settings.Bcolors.BURST + 'Firing Neuron: ' + x[1] + ' from ' + x[0] + settings.Bcolors.ENDC)
        neuron_fire(x[0], x[1])

    for cortical_area in set([i[0] for i in fire_candidate_list]):
        for src_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
            for dst_neuron in set([i[1] for i in fire_candidate_list if i[0] == cortical_area]):
                if src_neuron != dst_neuron:
                    wire_neurons_together(cortical_area=cortical_area, src_neuron=src_neuron, dst_neuron=dst_neuron)

    # todo: figure how to visualize bursts across various cortical areas
    # If visualization flag is set the visualization function will trigger
    if settings.burst_show:
        visualizer.burst_visualizer(fire_candidate_locations(fire_candidate_list))

    burst_duration = datetime.datetime.now() - burst_strt_time
    print(">>> Burst duration: %s" % burst_duration)

    # Initiate a new Burst
    burst(fire_candidate_list)
    return


#  >>>>>> Review this function against what we had in past
def fire_candidate_locations(fire_candidate_list):
    """Extracts Neuron locations from the fire_candidate_list"""

    print('***')
    # print(fire_candidate_list)

    neuron_locations = []
    for item in fire_candidate_list:
        neuron_locations.append(settings.brain[item[0]][item[1]]["location"])

        #
        # data = settings.brain[fire_candidate_list[fire_candidate_list.index(item)][0]]
        # print(data)
        # for key in data:
        #     neuron_locations.append(data[key]["location"])
        # print(neuron_locations)


    # for item in fire_candidate_list:
    #     if settings.read_data_from_memory:
    #         data = main.brain
    #     else:
    #         with open(settings.connectome_path+fire_candidate_list[item][0]+'.json', "r") as data_file:
    #             data = json.load(data_file)
    #
    #     neuron_locations.append(data[fire_candidate_list[item][0]]["location"])

    return neuron_locations


def neuron_fire(cortical_area, id):
    """This function initiate the firing of Neuron in a given cortical area"""

    data = settings.brain[cortical_area]

    # Setting Destination to the list of Neurons connected to the firing Neuron
    destination = data[id]["neighbors"]
    if settings.verbose:
        print(settings.Bcolors.FIRE + "Firing neuron %s using firing pattern %s"
          % (id, json.dumps(data[id]["firing_pattern_id"], indent=3)) + settings.Bcolors.ENDC)
        print(settings.Bcolors.FIRE + "Neuron %s neighbors are %s" % (id, json.dumps(destination, indent=3)) +
              settings.Bcolors.ENDC)

    # After neuron fires all cumulative counters on Source gets reset
    data[id]["cumulative_intake_sum_since_reset"] = 0
    data[id]["last_timer_reset_time"] = str(datetime.datetime.now())
    data[id]["cumulative_fire_count"] += 1
    data[id]["cumulative_fire_count_inst"] += 1

    # Transferring the signal from firing Neuron's Axon to all connected Neuron Dendrites
    # Firing pattern to be accommodated here     <<<<<<<<<<  *****
    neuron_update_list = []
    for x in destination:
        if settings.verbose:
            print(settings.Bcolors.FIRE + 'Updating connectome for Neuron ' + x + settings.Bcolors.ENDC)
        neuron_update(data[id]["neighbors"][x]["cortical_area"], data[id]["neighbors"][x]["synaptic_strength"], x)
    #     neuron_update_list.append([data[id]["neighbors"][x]["cortical_area"], data[id]["neighbors"][x]["synaptic_strength"], x])
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
    if settings.verbose:
        print(settings.Bcolors.FIRE + "Fire Function triggered FCL: %s " % fire_candidate_list + settings.Bcolors.ENDC)

    # Push changes back to Brain
    settings.brain[cortical_area] = data

    return


def neuron_update(cortical_area, synaptic_strength, destination):
    """This function updates the destination parameters upon upstream Neuron firing"""

    data = settings.brain[cortical_area]

    # update the cumulative_intake_total, cumulative_intake_count and synaptic_strength between source and
    # destination neurons based on XXX algorithm. The source is considered the Axon of the firing neuron and
    # destination is the dendrite of the neighbor.

    if settings.verbose:
        print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value before update: %s"
          % (destination, data[destination]["cumulative_intake_sum_since_reset"]) + settings.Bcolors.ENDC)

    # Check if timer is expired on the destination Neuron and if so reset the counter
    # Todo: Need to tune up the timer as depending on the application performance the timer could be always expired
    if (datetime.datetime.strptime(data[destination]["last_timer_reset_time"], "%Y-%m-%d %H:%M:%S.%f") +
            datetime.timedelta(0, data[destination]["timer_threshold"])) < datetime.datetime.now():
        data[destination]["last_timer_reset_time"] = str(datetime.datetime.now())
        data[destination]["cumulative_intake_sum_since_reset"] = 0  # Might be better to have a reset func.
        if settings.verbose:
            print(settings.Bcolors.UPDATE + 'Cumulative counters for Neuron ' + destination +
                  ' got rest' + settings.Bcolors.ENDC)

    # Increasing the cumulative counter on destination based on the received signal from upstream Axon
    # The following is considered as LTP or Long Term Potentiation of Neurons
    data[destination]["cumulative_intake_sum_since_reset"] += synaptic_strength

    if settings.verbose:
        print(settings.Bcolors.UPDATE + "%s's Cumulative_intake_count value after update: %s"
          % (destination, data[destination]["cumulative_intake_sum_since_reset"]) + settings.Bcolors.ENDC)

    # Add code to start a timer when neuron first receives a signal and reset counters when its expired

    # Need to call the Fire function if the threshold on the destination Neuron is met  <<<<<<<<<<<  ********
    # Need to figure how to deal with Activation function and firing threshold
    # Pass the cumulative_intake_total through the activation function and if pass the condition
    # fire destination neuron

    # The following will evaluate if the destination neuron is ready to fire and if so adds it to
    # fire_candidate_list
    global fire_candidate_list
    if data[destination]["cumulative_intake_sum_since_reset"] > data[destination]["firing_threshold"]:
       if fire_candidate_list.count([cortical_area, destination]) == 0:   # To prevent duplicate entries
            fire_candidate_list.append([cortical_area, destination])
            if settings.verbose:
                print(settings.Bcolors.UPDATE + "    Update Function triggered FCL: %s " % fire_candidate_list + settings.Bcolors.ENDC)

    # Push changes back to Brain
    settings.brain[cortical_area] = data

    return fire_candidate_list


def neuron_prop(cortical_area, id):
    """This function accepts neuron id and returns neuron properties"""

    data = settings.brain[cortical_area]

    if settings.verbose:
        print('Listing Neuron Properties for %s:' % id)
        print(json.dumps(data[id], indent=3))
    return data[id]


def neuron_neighbors(cortical_area, id):
    """This function accepts neuron id and returns the list of Neuron neighbors"""

    data = settings.brain[cortical_area]

    if settings.verbose:
        print('Listing Neuron Neighbors for %s:' % id)
        print(json.dumps(data[id]["neighbors"], indent=3))
    return data[id]["neighbors"]

def wire_neurons_together(cortical_area, src_neuron, dst_neuron):
    """
    This function simulates neuron plasticity in a sense that when facilitates wiring the neurons together. This is 
    done by increasing the synaptic_strength associated with a link between two neuron.
    """
    data = settings.brain[cortical_area]
    genome = settings.genome

    # Build neighbor relationship between the source and destination if its not already in place
    # Check if source and destination have an existing synapse if not create one here
    if dst_neuron not in data[src_neuron]["neighbors"]:
        synapse(cortical_area, src_neuron, cortical_area, dst_neuron,
                genome["blueprint"][cortical_area]["synaptic_strength"])

    # Every time source and destination neuron is fired at the same time which in case of the code architecture
    # reside in the same burst, the synaptic_strength will be increased simulating Fire together, wire together.
    data[src_neuron]["neighbors"][dst_neuron]["synaptic_strength"] += \
        genome["blueprint"][cortical_area]["synaptic_strength_inc"]
    # Append a Group ID so Memory clusters can be uniquely identified
    data[src_neuron]["neighbors"][dst_neuron]["event_id"][settings.event_id] = ''

    return
