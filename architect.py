"""
set of algorithms designed to generate neurons and update the connectome

Architect will accept the following information as input:
        1. Growth boundaries: Driving the limits of Neuron creation
        2. Neuron Density:    Driving number of Neurons per unit of space
        3. Growth pattern:    Driving Neighbor relations and shape of connectivity
Architect output would be the json file defined in settings as connectome_file
"""

import json
import datetime
import string
import random
from math import sqrt

import settings



def id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    """
    This function generates a unique id which will be associated with each neuron
    :param size:
    :param chars:
    :return:
    """
    # Rand gen source partially from:
    # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return str(datetime.datetime.now()).replace(' ', '_')+'_'+(''.join(random.choice(chars) for _ in range(size)))


def neuro_genesis(cortical_area, location):
    """
    Responsible for adding a Neuron to connectome
    :param location:
    :return:
    """
    # todo: Need to update the following to use the Genome data instead of hardcoded values

    data = settings.brain[cortical_area]
    id = id_gen()
    data[id] = {}
    data[id]["neighbors"] = {}
    data[id]["status"] = "Passive"
    data[id]["activation_function_id"] = ""
    data[id]["timer_threshold"] = 500
    data[id]["firing_threshold"] = 5
    data[id]["cumulative_intake_sum_since_reset"] = 0
    data[id]["last_timer_reset_time"] = str(datetime.datetime.now())
    data[id]["cumulative_fire_count"] = 0
    data[id]["cumulative_intake_total"] = 0
    data[id]["cumulative_intake_count"] = 0
#       data[id]["group_id"] = ""           # consider using the group name part of Genome instead
    data[id]["firing_pattern_id"] = ""
    data[id]["location"] = location

    return


# todo: Need to update Synapse function to include both Source and Destination Cortical area
def synapse(src_cortical_area, src_id, dst_cortical_area, dst_id, connection_resistance):
    """
    Function responsible for detecting a Neuron's neighbors and creating synaptic connections
    Note: Synapse association is captured on the Source Neuron side within Connectome
    :param source:
    :param destination:
    :param connection_resistance:
    :return:
    """
    # Input: The id for source and destination Neuron plus the parameter defining connection strength
    # Source provides the Axon and connects to Destination Dendrite
    # connection_resistance is intended to provide the level of synaptic strength

    data = settings.brain[src_cortical_area]

    # Check to see if the source and destination ids are valid if not exit the function
    if src_id not in data:
        print("Source or Destination neuron not found")
        return

    data[src_id]["neighbors"][dst_id] = {"cortical_area": dst_cortical_area,
                                         "connection_resistance": connection_resistance}

    return


def location_generator(x1, y1, z1, x2, y2, z2):
    """
    Function responsible to generate a pseudo-random location for a Neuron given some constraints
    :param x1:
    :param y1:
    :param z1:
    :param x2:
    :param y2:
    :param z2:
    :return:
    """
    # todo: update to leverage the Genome template
    # todo: Would it be better to use relative locations in each cortical region instead?
    neuron_location = [random.randrange(x1, x2, 1), random.randrange(y1, y2, 1), random.randrange(z1, z2, 1)]
    return neuron_location


def location_collector(cortical_area):
    """
    Function responsible to generate a list of locations to be used for Neuron creation
    :return:
    """

#   neighbor_count = 9999
#   global max_density      # TBD: This value needs to be defied in a config file of some sort
#   while neighbor_count < max_density:
        # Above condition will be met when enough neighbors has been created with following criteria
        #     1. Density requirements has been met
        #     2. TBD
        # TBD:  Need to figure a way to pass in a 3d object formula and use that to contain neuronal growth
        # Need to come up with an algorithm to populate the space within the object with random neurons given density
        # Output is expected to be a N x 3 matrix containing dimensions for N neurons to be created

    data = settings.genome

    if data["blueprint"].get(cortical_area) is None:
        print("Cortical area %s not found!" % cortical_area)
        return

    neuron_loc_list = []
    for x in range(0, data["blueprint"][cortical_area]["neuron_density"]):
        neuron_loc_list.append(location_generator(
            data["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0],
            data["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0],
            data["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0],
            data["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1],
            data["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1],
            data["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1]))

    return neuron_loc_list


def three_dim_growth(cortical_area):
    """
    Function responsible for creating Neurons using the blueprint
    """
    # This code segment creates a new Neuron per every location in neuron_loc_list
    neuron_loc_list = location_collector(cortical_area)

    for x in neuron_loc_list:
        neuro_genesis(cortical_area, x)        # Create a new Neuron in target destination

    return


def neighbor_finder(cortical_area, neuron_id, rule, rule_param):
    """
    A set of math functions allowing to detect the eligibility of a Neuron to become neighbor
    :param neuron_id:
    :param rule:
    :param rule_param:
    :return:
    """
    # Input: neuron id of which we desire to find all candidate neurons for
    data = settings.brain[cortical_area]
    neighbor_candidates = []

    for key in data:
        # The following if statements define various rules to help select candidate neurons

        # Rule 0: Selects all neurons within rule_param radius
        if rule == 'rule_0':
            radius = sqrt(data[key]["location"][0] ** 2 + data[neuron_id]["location"][0] ** 2 )
            if radius < rule_param:
                neighbor_candidates.append(key)

        # Rule 1: Selects only neurons within rule_param unit limits forward of source Neuron
        if rule == 'rule_1':
            if (data[key]["location"][0] > data[neuron_id]["location"][0]) and \
                    (data[key]["location"][0] < data[neuron_id]["location"][0]+rule_param):
                neighbor_candidates.append(key)


    return neighbor_candidates


def neighbor_builder(cortical_area, rule_id, rule_param, connection_resistance):
    """
    Function responsible for crawling through Neurons and deciding where to build Synapses
    :param rule:
    :param rule_param:
    :param connection_resistance:
    :return:
    """
    # Need to figure how to build a Neighbor relationship between Neurons
    #    1. Should it be based on the proximity?
    #    2. Should it be manually set? It wont be scalable
    #    3. How can it be based on a Guide function?
    # This function will utilize the Synapse function and based on an algorithm will create the relationships

    # Algorithm:
    #    1. Ask for a direction
    #    2. For each neuron in path find a list of eligible candidates
    #    3. Update connectome to the candidates become neighbors of the source neuron

    data = settings.brain[cortical_area]
    for src_id in data:
        # Cycle thru the neighbor_candidate_list and establish Synapses
        neighbor_candidates = neighbor_finder(cortical_area, src_id, rule_id, rule_param)
        for dst_id in neighbor_candidates:
            synapse(cortical_area, src_id, cortical_area, dst_id, connection_resistance)
            # print("Made a Synapse between %s and %s" % (src_id, dst_id))

    return


# todo: Need a new set of Neighbor building and finding functions to handle cross cortical scenarios


def neighbor_finder_ext(cortical_area_src, cortical_area_dst, neuron_id, rule, rule_param):
    """
    Finds a list of candidate Neurons from another Cortical area to build Synapse with for a given Neuron
    :param cortical_area_src:
    :param cortical_area_dst:
    :param neuron_id:
    :param rule:
    :param rule_param:
    :return:
    """

    # Input: neuron id of which we desire to find all candidate neurons for
    src_data = settings.brain[cortical_area_src]
    dst_data = settings.brain[cortical_area_dst]
    neighbor_candidates = []

    # The following if statements define various rules to help select candidate neurons from external source
    # todo: Figure a way to move the rules to genome
    # Rule 2: Selects only neurons within rule_param unit limits forward of source Neuron
    if rule == 'rule_2':
        for key in dst_data:
            if (dst_data[key]["location"][0] > src_data[neuron_id]["location"][0]) and \
                    (dst_data[key]["location"][0] < src_data[neuron_id]["location"][0]+rule_param) and \
                    (dst_data[key]["location"][1] > src_data[neuron_id]["location"][1]) and \
                    (dst_data[key]["location"][1] < src_data[neuron_id]["location"][1]+rule_param):
                neighbor_candidates.append(key)

    return neighbor_candidates


def neighbor_builder_ext(cortical_area_src, cortical_area_dst, rule, rule_param, connection_resistance=1):
    """
    Crawls thru a Cortical area and builds Synapses with External Cortical Areas
    :param cortical_area_src:
    :param cortical_area_dst:
    :param rule:
    :param rule_param:
    :param connection_resistance:
    :return:
    """
    data = settings.brain[cortical_area_src]
    for src_id in data:
        # Cycle thru the neighbor_candidate_list and establish Synapses
        neighbor_candidates = neighbor_finder_ext(cortical_area_src, cortical_area_dst, src_id, rule, rule_param)
        for dst_id in neighbor_candidates:
            synapse(cortical_area_src, src_id, cortical_area_dst, dst_id, connection_resistance)
            # print("Made a Synapse between %s and %s" % (src_id, dst_id))

    return


def field_set(cortical_area, field_name, field_value):
    """
    This function deletes all the neighbor relationships in the connectome
    :param field_name:
    :param field_value:
    :return:
    """
    data = settings.brain[cortical_area]
    for key in data:
        data[key][field_name] = field_value

    return


def neighbor_reset(cortical_area):
    """
    This function deletes all the neighbor relationships in the connectome
    :return:
    """

    data = settings.brain[cortical_area]
    for key in data:
        data[key]["neighbors"] = {}

    return


def neuron_finder(cortical_area, location, radius):
    """
    Queries a given cortical area and returns a listed of Neuron IDs matching search criteria
    :param cortical_area:
    :param location:
    :param radius:
    :return:
    """

    neuron_list = []
    # todo: figure a way to map the cortical_area to a given connectome file
    data = settings.brain[cortical_area]
    for key in data:
        x = data[key]['location'][0]
        y = data[key]['location'][1]
        z = data[key]['location'][2]

        if ((x-location[0]) ** 2 + (y-location[1]) ** 2 + (z-location[2]) ** 2) <= (radius ** 2):
            if neuron_list.count(key) == 0:
                neuron_list.append(key)

    return neuron_list


def connectome_location_data(cortical_area):
    """
    Extracts Neuron locations and neighbor relatioships from the connectome
    :return:
    """
    data = settings.brain[cortical_area]

    neuron_locations = []
    for key in data:
        neuron_locations.append(data[key]["location"])

    return neuron_locations


def pruner():
    """
    Responsible for pruning unused connections between neurons
    :return:
    """
    return



def neuron_eliminator():
    """
    Responsible for programmed cell death
    """
    return


