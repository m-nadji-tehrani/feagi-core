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

    genome = settings.genome
    data = settings.brain[cortical_area]

    id = id_gen()

    data[id] = {}
    data[id]["neighbors"] = {}
    data[id]["cumulative_intake_sum_since_reset"] = 0
    data[id]["cumulative_fire_count"] = 0
    data[id]["cumulative_fire_count_inst"] = 0
    data[id]["cumulative_intake_total"] = 0
    data[id]["cumulative_intake_count"] = 0

    data[id]["location"] = location
    data[id]["status"] = "Passive"
    data[id]["last_timer_reset_time"] = str(datetime.datetime.now())


#   data[id]["group_id"] = ""                   # consider using the group name part of Genome instead
    data[id]["firing_pattern_id"] = genome['blueprint'][cortical_area]['neuron_params']['firing_pattern_id']
    data[id]["activation_function_id"] = genome['blueprint'][cortical_area]['neuron_params']['activation_function_id']
    data[id]["timer_threshold"] = genome['blueprint'][cortical_area]['neuron_params']['timer_threshold']
    data[id]["firing_threshold"] = genome['blueprint'][cortical_area]['neuron_params']['firing_threshold']

    return


# todo: Need to update Synapse function to include both Source and Destination Cortical area
def synapse(src_cortical_area, src_id, dst_cortical_area, dst_id, synaptic_strength):
    """
    Function responsible for detecting a Neuron's neighbors and creating synaptic connections
    Note: Synapse association is captured on the Source Neuron side within Connectome
    :param source:
    :param destination:
    :param synaptic_strength:
    :return:
    """
    # Input: The id for source and destination Neuron plus the parameter defining connection strength
    # Source provides the Axon and connects to Destination Dendrite
    # synaptic_strength is intended to provide the level of synaptic strength

    data = settings.brain[src_cortical_area]

    # Check to see if the source and destination ids are valid if not exit the function
    if src_id not in data:
        print("Source or Destination neuron not found")
        return

    data[src_id]["neighbors"][dst_id] = {"cortical_area": dst_cortical_area,
                                         "synaptic_strength": synaptic_strength}

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

    genome = settings.genome

    if genome["blueprint"].get(cortical_area) is None:
        print("Cortical area %s not found!" % cortical_area)
        return

    neuron_loc_list = []
    for x in range(0, genome["blueprint"][cortical_area]["neuron_density"]):
        neuron_loc_list.append(location_generator(
            genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0],
            genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0],
            genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0],
            genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1],
            genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1],
            genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1]))

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
    :param cortical_area
    :return:
    """
    # Input: neuron id of which we desire to find all candidate neurons for
    data = settings.brain[cortical_area]
    neighbor_candidates = []

    for key in data:
        if rule_matcher(rule_id=rule, rule_param=rule_param,
                        cortical_area_src=cortical_area, cortical_area_dst=cortical_area, neuron_id=neuron_id, key=key):
            neighbor_candidates.append(key)

    return neighbor_candidates


def neighbor_builder(cortical_area, rule_id, rule_param, synaptic_strength):
    """
    Function responsible for crawling through Neurons and deciding where to build Synapses
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
            synapse(cortical_area, src_id, cortical_area, dst_id, synaptic_strength)
            # print("Made a Synapse between %s and %s" % (src_id, dst_id))

    return


def neighbor_finder_ext(cortical_area_src, cortical_area_dst, src_neuron_id, rule, rule_param):
    """
    Finds a list of candidate Neurons from another Cortical area to build Synapse with for a given Neuron
    """

    # Input: neuron id of which we desire to find all candidate neurons for from another cortical region
    dst_data = settings.brain[cortical_area_dst]
    neighbor_candidates = []

    for key in dst_data:
        if rule_matcher(rule_id=rule, rule_param=rule_param, cortical_area_src=cortical_area_src,
                        cortical_area_dst=cortical_area_dst, key=key, neuron_id=src_neuron_id):
            neighbor_candidates.append(key)

    return neighbor_candidates


def neighbor_builder_ext(cortical_area_src, cortical_area_dst, rule, rule_param, synaptic_strength=1):
    """
    Crawls thru a Cortical area and builds Synapses with External Cortical Areas
    """
    data = settings.brain[cortical_area_src]
    for src_id in data:
        # Cycle thru the neighbor_candidate_list and establish Synapses
        neighbor_candidates = neighbor_finder_ext(cortical_area_src, cortical_area_dst, src_id, rule, rule_param)
        for dst_id in neighbor_candidates:
            synapse(cortical_area_src, src_id, cortical_area_dst, dst_id, synaptic_strength)
            # print("Made a Synapse between %s and %s" % (src_id, dst_id))

    return


def field_set(cortical_area, field_name, field_value):
    """
    This function changes a field value in connectome 
    
    *** Incomplete ***
    
    """
    # data = settings.brain[cortical_area]
    # for key in data:
    #     data[key][field_name] = field_value
    #
    # settings.brain[cortical_area] = data

    return


def neighbor_reset(cortical_area):
    """
    This function deletes all the neighbor relationships in the connectome
    """

    data = settings.brain[cortical_area]
    for key in data:
        data[key]["neighbors"] = {}

    return


def neuron_finder(cortical_area, location, radius):
    """
    Queries a given cortical area and returns a listed of Neuron IDs matching search criteria
    """

    neuron_list = []
    data = settings.brain[cortical_area]
    for key in data:
        x = data[key]['location'][0]
        y = data[key]['location'][1]
        z = data[key]['location'][2]

        # Searching only the XY plane for candidate neurons
        if sqrt((x-location[0]) ** 2 + (y-location[1]) ** 2) <= (radius ** 2):
            if neuron_list.count(key) == 0:
                neuron_list.append(key)

    return neuron_list


def connectome_location_data(cortical_area):
    """
    Extracts Neuron locations and neighbor relatioships from the connectome
    """
    data = settings.brain[cortical_area]

    neuron_locations = []
    for key in data:
        location_data = data[key]["location"]
        location_data.append(data[key]["cumulative_fire_count"])
        neuron_locations.append(location_data)

    return neuron_locations


def pruner():
    """
    Responsible for pruning unused connections between neurons
    """
    return


def neuron_eliminator():
    """
    Responsible for programmed neuron's death
    """
    return


def rule_matcher(rule_id, rule_param, cortical_area_src, cortical_area_dst, key, neuron_id):

    src_data = settings.brain[cortical_area_src]
    dst_data = settings.brain[cortical_area_dst]

    if cortical_area_src == cortical_area_dst:
        x_coordinate_key = src_data[key]["location"][0]
        x_coordinate_target = src_data[neuron_id]["location"][0]
        y_coordinate_key = src_data[key]["location"][1]
        y_coordinate_target = src_data[neuron_id]["location"][1]
        z_coordinate_key = src_data[key]["location"][2]
        z_coordinate_target = src_data[neuron_id]["location"][2]
    else:
        x_coordinate_key = src_data[neuron_id]["location"][0]
        y_coordinate_key = src_data[neuron_id]["location"][1]
        z_coordinate_key = src_data[neuron_id]["location"][2]
        x_coordinate_target_dst = dst_data[key]["location"][0]
        y_coordinate_target_dst = dst_data[key]["location"][1]
        z_coordinate_target_dst = dst_data[key]["location"][2]

    is_candidate = False

    # Rule 0: Selects all neurons within rule_param radius
    if rule_id == 'rule_0':
        radius = sqrt(((x_coordinate_key - x_coordinate_target) ** 2) +
                      ((y_coordinate_key - y_coordinate_target) ** 2) +
                      ((z_coordinate_key - z_coordinate_target) ** 2))
        if radius < rule_param:
            is_candidate = True

    # Rule 1: Selects only neurons within rule_param unit limits forward of source Neuron in z direction
    if rule_id == 'rule_1':
        if (z_coordinate_key > z_coordinate_target) and \
                sqrt(((x_coordinate_key - x_coordinate_target) ** 2)
                             + ((y_coordinate_key - y_coordinate_target) ** 2)) < rule_param:
            is_candidate = True

    # Rule 2: Selects neurons from the destination cortical region
    if rule_id == 'rule_2':
        if sqrt(((x_coordinate_key - x_coordinate_target_dst) ** 2)
                        + ((y_coordinate_key - y_coordinate_target_dst) ** 2)) < rule_param:
            is_candidate = True

    return is_candidate
