"""
set of algorithms designed to generate neurons and update the connectome

Architect will accept the following information as input:
        1. Growth boundaries: Driving the limits of Neuron creation
        2. Neuron Density:    Driving number of Neurons per unit of space
        3. Growth pattern:    Driving Neighbor relations and shape of connectivity
"""

import datetime
import string
import random
from math import sqrt, ceil, floor
from misc import universal_functions


def neuron_id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    """
    This function generates a unique id which will be associated with each neuron
    :param size:
    :param chars:
    :return:
    """
    # Rand gen source partially from:
    # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return str(datetime.datetime.now()).replace(' ', '_')+'_'+(''.join(random.choice(chars) for _ in range(size)))+'_N'


def event_id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    """
    This function generates a unique id which will be associated with each neuron
    :param size:
    :param chars:
    :return:
    """
    # Rand gen source partially from:
    # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return str(datetime.datetime.now()).replace(' ', '_')+'_'+(''.join(random.choice(chars) for _ in range(size)))+'_E'


def neuro_genesis(cortical_area, loc_blk):
    """
    Responsible for adding a Neuron to connectome

    """

    genome = universal_functions.genome

    id = neuron_id_gen()

    universal_functions.brain[cortical_area][id] = {}
    universal_functions.brain[cortical_area][id]["neighbors"] = {}
    universal_functions.brain[cortical_area][id]["event_id"] = {}
    universal_functions.brain[cortical_area][id]["membrane_potential"] = 0
    universal_functions.brain[cortical_area][id]["cumulative_fire_count"] = 0
    universal_functions.brain[cortical_area][id]["cumulative_fire_count_inst"] = 0
    universal_functions.brain[cortical_area][id]["cumulative_intake_total"] = 0
    universal_functions.brain[cortical_area][id]["cumulative_intake_count"] = 0
    universal_functions.brain[cortical_area][id]["consecutive_fire_cnt"] = 0
    universal_functions.brain[cortical_area][id]["snooze_till_burst_num"] = 0
    universal_functions.brain[cortical_area][id]["last_burst_num"] = 0

    universal_functions.brain[cortical_area][id]["location"] = loc_blk[0]
    universal_functions.brain[cortical_area][id]["block"] = loc_blk[1]
    universal_functions.brain[cortical_area][id]["status"] = "Passive"
    universal_functions.brain[cortical_area][id]["last_membrane_potential_reset_time"] = str(datetime.datetime.now())
    universal_functions.brain[cortical_area][id]["last_membrane_potential_reset_burst"] = 0


    #   universal_functions.brain[cortical_area][id]["group_id"] = ""           # consider using the group name part of Genome instead
    universal_functions.brain[cortical_area][id]["firing_pattern_id"] = \
        genome['blueprint'][cortical_area]['neuron_params']['firing_pattern_id']
    universal_functions.brain[cortical_area][id]["activation_function_id"] = \
        genome['blueprint'][cortical_area]['neuron_params']['activation_function_id']
    universal_functions.brain[cortical_area][id]["depolarization_threshold"] = \
        genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold']
    universal_functions.brain[cortical_area][id]["firing_threshold"] = \
        genome['blueprint'][cortical_area]['neuron_params']['firing_threshold']

    return


def synapse(src_cortical_area, src_id, dst_cortical_area, dst_id, postsynaptic_current):
    """
    Function responsible for creating a synapse between a neuron and another one. In reality a single neuron can have
    many synapses with another individual neuron. Here we use synaptic strength to simulate the same
    Note: Synapse association is captured on the Source Neuron side within Connectome
    
    # Input: The id for source and destination Neuron plus the parameter defining connection strength
    # Source provides the Axon and connects to Destination Dendrite
    # postsynaptic_current is intended to provide the level of synaptic strength
    """

    # Check to see if the source and destination ids are valid if not exit the function
    if src_id not in universal_functions.brain[src_cortical_area]:
        print("Source or Destination neuron not found")
        return

    universal_functions.brain[src_cortical_area][src_id]["neighbors"][dst_id] = \
        {"cortical_area": dst_cortical_area, "postsynaptic_current": postsynaptic_current}

    return


def random_location_generator(x1, y1, z1, x2, y2, z2):
    """
    Function responsible to generate a pseudo-random location for a Neuron given some constraints

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

    genome = universal_functions.genome

    if genome["blueprint"].get(cortical_area) is None:
        print("Cortical area %s not found!" % cortical_area)
        return

    neuron_loc_list = []

    if genome["blueprint"][cortical_area]["location_generation_type"] == "random":
        for _ in range(0, genome["blueprint"][cortical_area]["cortical_neuron_count"]):
            neuron_loc_list.append(random_location_generator(
                genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0],
                genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0],
                genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0],
                genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1],
                genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1],
                genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1]))
    else:
        x_lenght = (genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1] -
                    genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0])
        y_lenght = (genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1] -
                    genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0])
        z_lenght = (genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1] -
                    genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0])

        # Following formula calculates the proper distance between neurons to be used to have n number of them
        # evenly distributed within the given cortical area

        none_zero_axis = list(filter(lambda axis_width: axis_width > 1, [x_lenght, y_lenght, z_lenght]))

        dimension = len(none_zero_axis)

        neuron_count = genome["blueprint"][cortical_area]["cortical_neuron_count"]

        area = 1
        for _ in none_zero_axis:
            area = area * _

        neuron_gap = (area / neuron_count) ** (1 / dimension)

        # Number of neurons in each axis
        xn = int(x_lenght / neuron_gap)
        yn = int(y_lenght / neuron_gap)
        zn = int(z_lenght / neuron_gap)

        if xn == 0: xn = 1
        if yn == 0: yn = 1
        if zn == 0: zn = 1

        x_coordinate = genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0]
        y_coordinate = genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0]
        z_coordinate = genome["blueprint"][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0]

        for i in range(xn):
            for ii in range(yn):
                for iii in range(zn):
                    neuron_loc_list.append([x_coordinate, y_coordinate, z_coordinate])
                    z_coordinate += neuron_gap
                y_coordinate += neuron_gap
            x_coordinate += neuron_gap

    return neuron_loc_list


def three_dim_growth(cortical_area):
    """
    Function responsible for creating Neurons using the blueprint
    """
    # This code segment creates a new Neuron per every location in neuron_loc_list
    neuron_loc_list = location_collector(cortical_area)
    neuron_blk_list = []
    cortical_area_dim = []
    geometric_boundaries = universal_functions.genome['blueprint'][cortical_area]['neuron_params']['geometric_boundaries']
    for coordinate in geometric_boundaries:
        cortical_area_dim.append(geometric_boundaries[coordinate][1]-geometric_boundaries[coordinate][0])

    for _ in neuron_loc_list:
        # neuron_blk_list.append(block_id_gen(_[0], _[1], _[2]))
        neuron_blk_list.append(block_id_gen2(_, space_dimensions=cortical_area_dim))

    neuron_loc_blk = zip(neuron_loc_list, neuron_blk_list)

    neuron_count = 0
    for __ in neuron_loc_blk:
        neuro_genesis(cortical_area, __)        # Create a new Neuron in target destination
        neuron_count += 1

    return neuron_count


def neighbor_finder(cortical_area, neuron_id, rule, rule_param):
    """
    A set of math functions allowing to detect the eligibility of a Neuron to become neighbor
    :param neuron_id:
    :param rule:
    :param rule_param:
    :param cortical_area
    :return:
    """
    if cortical_area == 'utf8_memory':
        print('rule=', rule)
    # Input: neuron id of which we desire to find all candidate neurons for
    neighbor_candidates = []

    # Narrow down the search scope to only few blocks
    neighbors_in_block = neurons_in_block_neighborhood(cortical_area, neuron_id, kernel_size=3)

    for dst_neuron_id in neighbors_in_block:
        if rule_matcher(rule_id=rule,
                        rule_param=rule_param,
                        cortical_area_src=cortical_area,
                        cortical_area_dst=cortical_area,
                        src_neuron_id=neuron_id,
                        dst_neuron_id=dst_neuron_id):
            neighbor_candidates.append(dst_neuron_id)

    return neighbor_candidates


def neighbor_builder(brain, brain_gen, cortical_area, rule_id, rule_param, postsynaptic_current):
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

    # todo: Warning: Need to watch for the side effects on this line to make sure its not overwriting values
    if brain_gen:
        universal_functions.brain = brain

    synapse_count = 0
    for src_id in universal_functions.brain[cortical_area]:
        # Cycle thru the neighbor_candidate_list and establish Synapses
        neighbor_candidates = neighbor_finder(cortical_area, src_id, rule_id, rule_param)
        for dst_id in neighbor_candidates:
            synapse(cortical_area, src_id, cortical_area, dst_id, postsynaptic_current)
            synapse_count += 1
            # print("Made a Synapse between %s and %s" % (src_id, dst_id))

    if brain_gen:
        brain = universal_functions.brain

        synapse_count2 = 0
        for area in brain:
            for neuron in brain[area]:
                for connection in brain[area][neuron]['neighbors']:
                    synapse_count2 += 1
    else:
        brain = {}
    return synapse_count, brain


def dst_projection_center(cortical_area_src, neuron_id, cortical_area_dst):
    """
    Returns the coordinates of a neuron projected into a target Cortical layer
    """

    # Find relative coordinates on the source and destination side
    src_lengths = cortical_area_lengths(cortical_area_src)
    dst_lengths = cortical_area_lengths(cortical_area_dst)
    coordinate_scales = [a/b for a, b in zip(dst_lengths, src_lengths)]

    x_coordinate_src = universal_functions.brain[cortical_area_src][neuron_id]["location"][0]
    y_coordinate_src = universal_functions.brain[cortical_area_src][neuron_id]["location"][1]
    z_coordinate_src = universal_functions.brain[cortical_area_src][neuron_id]["location"][2]

    dst_projection_center = list()
    dst_projection_center.append(x_coordinate_src * coordinate_scales[0])
    dst_projection_center.append(y_coordinate_src * coordinate_scales[1])
    dst_projection_center.append(z_coordinate_src * coordinate_scales[2])

    return dst_projection_center


def neighbor_finder_ext(cortical_area_src, cortical_area_dst, src_neuron_id, rule, rule_param):
    """
    Finds a list of candidate Neurons from another Cortical area to build Synapse with for a given Neuron
    """

    # Input: neuron id of which we desire to find all candidate neurons for from another cortical region
    dst_data = universal_functions.brain[cortical_area_dst]
    neighbor_candidates = []

    if universal_functions.genome['blueprint'][cortical_area_dst]['location_generation_type'] == 'sequential':
        for dst_neuron_id in dst_data:
            if rule_matcher(rule_id=rule, rule_param=rule_param, cortical_area_src=cortical_area_src,
                            cortical_area_dst=cortical_area_dst, dst_neuron_id=dst_neuron_id, src_neuron_id=src_neuron_id):
                neighbor_candidates.append(dst_neuron_id)
    else:
        # todo: Need to bring here concept of the projection center and find neurons around the block there
        projection_coord = dst_projection_center(cortical_area_src, src_neuron_id, cortical_area_dst)

        # todo: move the block size and kernel size below to settings
        proj_block_id = block_id_gen(projection_coord[0], projection_coord[1], projection_coord[2], block_size=10)
        neuron_list = neurons_in_block_neighborhood_2(cortical_area_dst, proj_block_id, kernel_size=3)
        for dst_neuron_id in neuron_list:
            if rule_matcher(rule_id=rule, rule_param=rule_param, cortical_area_src=cortical_area_src,
                            cortical_area_dst=cortical_area_dst, dst_neuron_id=dst_neuron_id, src_neuron_id=src_neuron_id):
                neighbor_candidates.append(dst_neuron_id)

    return neighbor_candidates


def neighbor_builder_ext(brain, brain_gen, cortical_area_src, cortical_area_dst, rule, rule_param, postsynaptic_current=1):
    """
    Crawls thru a Cortical area and builds Synapses with External Cortical Areas
    """

    if brain_gen:
        universal_functions.brain = brain

    synapse_count = 0
    for src_id in universal_functions.brain[cortical_area_src]:
        # Cycle thru the neighbor_candidate_list and establish Synapses
        neighbor_candidates = neighbor_finder_ext(cortical_area_src, cortical_area_dst, src_id, rule, rule_param)
        for dst_id in neighbor_candidates:
            # Through a dice to decide for synapse creation. This is to limit the amount of synapses.
            if random.randrange(1, 100) < universal_functions.genome['blueprint'][cortical_area_dst]['synapse_attractivity']:
                # Connect the source and destination neuron via creating a synapse
                synapse(cortical_area_src, src_id, cortical_area_dst, dst_id, postsynaptic_current)
                synapse_count += 1
                # print("Made a Synapse between %s and %s" % (src_id, dst_id))

    if brain_gen:
        brain = universal_functions.brain
    else:
        brain = {}
    return synapse_count, brain


def field_set(cortical_area, field_name, field_value):
    """
    This function changes a field value in connectome 
    
    *** Incomplete ***
    
    """
    # universal_functions.brain[cortical_area] = universal_functions.brain[cortical_area]
    # for key in universal_functions.brain[cortical_area]:
    #     universal_functions.brain[cortical_area][key][field_name] = field_value
    #

    return


def neighbor_reset(cortical_area):
    """
    This function deletes all the neighbor relationships in the connectome
    """

    for key in universal_functions.brain[cortical_area]:
        universal_functions.brain[cortical_area][key]["neighbors"] = {}

    return


def neuron_finder(cortical_area, location, radius):
    """
    Queries a given cortical area and returns a listed of Neuron IDs matching search criteria
    """

    neuron_list = []

    for key in universal_functions.brain[cortical_area]:
        x = universal_functions.brain[cortical_area][key]['location'][0]
        y = universal_functions.brain[cortical_area][key]['location'][1]
        z = universal_functions.brain[cortical_area][key]['location'][2]

        # Searching only the XY plane for candidate neurons         ????
        if sqrt((x-location[0]) ** 2 + (y-location[1]) ** 2) <= (radius ** 2):
            if neuron_list.count(key) == 0:
                neuron_list.append(key)

    return neuron_list


def neuron_finder2(cortical_area, location, radius):

    cortical_area_dims = cortical_area_lengths(cortical_area)
    block_id = block_id_gen2(location, cortical_area_dims)

    neuron_list = neurons_in_the_block(cortical_area, block_id)

    return neuron_list


def connectome_location_data(cortical_area):
    """
    Extracts Neuron locations and neighbor relatioships from the connectome
    """

    neuron_locations = []
    for key in universal_functions.brain[cortical_area]:
        location_data = universal_functions.brain[cortical_area][key]["location"]
        location_data.append(universal_functions.brain[cortical_area][key]["cumulative_fire_count"])
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


def cortical_area_lengths(cortical_area):
    lenght = []
    coordinates = ['x', 'y', 'z']
    for _ in coordinates:
        lenght.append(
            universal_functions.genome['blueprint'][cortical_area]['neuron_params']['geometric_boundaries'][_][1] -
            universal_functions.genome['blueprint'][cortical_area]['neuron_params']['geometric_boundaries'][_][0])

    return lenght


def rule_matcher(rule_id, rule_param, cortical_area_src, cortical_area_dst, dst_neuron_id, src_neuron_id):

    src_data = universal_functions.brain[cortical_area_src]
    dst_data = universal_functions.brain[cortical_area_dst]

    if cortical_area_dst == 'vision_v2' and cortical_area_src == 'vision_v1-1':
        1 == 1

    # Find relative coordinates on the source and destination side
    src_lenghts = cortical_area_lengths(cortical_area_src)
    dest_lenghts = cortical_area_lengths(cortical_area_dst)
    coordinate_scales = [a/b for a, b in zip(dest_lenghts, src_lenghts)]

    if cortical_area_src == cortical_area_dst:
        x_coordinate_key = src_data[dst_neuron_id]["location"][0]
        x_coordinate_target = src_data[src_neuron_id]["location"][0]
        y_coordinate_key = src_data[dst_neuron_id]["location"][1]
        y_coordinate_target = src_data[src_neuron_id]["location"][1]
        z_coordinate_key = src_data[dst_neuron_id]["location"][2]
        z_coordinate_target = src_data[src_neuron_id]["location"][2]
    else:
        x_coordinate_key = src_data[src_neuron_id]["location"][0]
        y_coordinate_key = src_data[src_neuron_id]["location"][1]
        z_coordinate_key = src_data[src_neuron_id]["location"][2]
        x_coordinate_target_dst = dst_data[dst_neuron_id]["location"][0]
        y_coordinate_target_dst = dst_data[dst_neuron_id]["location"][1]
        z_coordinate_target_dst = dst_data[dst_neuron_id]["location"][2]

    dest_projection_center = list()
    dest_projection_center.append(x_coordinate_key * coordinate_scales[0])
    dest_projection_center.append(y_coordinate_key * coordinate_scales[1])
    dest_projection_center.append(z_coordinate_key * coordinate_scales[2])

    is_candidate = False

    # Rule 0: Selects all neurons within rule_param radius
    if rule_id == 'rule_0':
        radius = sqrt(((x_coordinate_key - x_coordinate_target) ** 2) +
                      ((y_coordinate_key - y_coordinate_target) ** 2) +
                      ((z_coordinate_key - z_coordinate_target) ** 2))
        if radius < rule_param:
            print("This is the neuron id you were looking for:", src_neuron_id)
            is_candidate = True

    # Rule 1: Selects only neurons within rule_param unit limits forward of source Neuron in z direction
    if rule_id == 'rule_1':
        if (z_coordinate_key > z_coordinate_target) and \
                sqrt(((x_coordinate_key - x_coordinate_target) ** 2)
                             + ((y_coordinate_key - y_coordinate_target) ** 2)) < rule_param:
            is_candidate = True

    # Rule 2: Selects neurons from the destination cortical region
    if rule_id == 'rule_2':
        if sqrt(((x_coordinate_key - x_coordinate_target_dst) ** 2) +
                ((y_coordinate_key - y_coordinate_target_dst) ** 2)) < rule_param:
            is_candidate = True

    # Rule 3: Specific for narrow cortical regions specially built for computer interface
    if rule_id == 'rule_3':
        if abs(z_coordinate_key - z_coordinate_target_dst) == rule_param:
            is_candidate = True

    # Rule 4: Maps entire layer to another. Expands the xy plane and ignores the z location
    if rule_id == 'rule_4':
        if sqrt(((dest_projection_center[0] - x_coordinate_target_dst) ** 2) +
                ((dest_projection_center[1] - y_coordinate_target_dst) ** 2)) < rule_param:
            is_candidate = True

    # Rule 5: Helps mapping multiple layers to a single layer
    if rule_id == 'rule_5':
        src_layer_index = universal_functions.genome['blueprint'][cortical_area_src]['layer_index']
        src_total_layer_count = universal_functions.genome['blueprint'][cortical_area_src]['total_layer_count']
        dest_layer_height = dest_lenghts[2] / src_total_layer_count
        if (sqrt(((dest_projection_center[0] - x_coordinate_target_dst) ** 2) +
                ((dest_projection_center[1] - y_coordinate_target_dst) ** 2)) < rule_param):

                # and \
                # (z_coordinate_target_dst > src_layer_index * dest_layer_height) and \
                # (z_coordinate_target_dst < ((src_layer_index + 1) * dest_layer_height)):
            is_candidate = True

    # Rule 6: Maps XY blocks from one layer to another
    if rule_id == 'rule_6':
        src_blk_x = universal_functions.brain[cortical_area_src][src_neuron_id]["block"][0]
        src_blk_y = universal_functions.brain[cortical_area_src][src_neuron_id]["block"][1]
        dst_blk_x = universal_functions.brain[cortical_area_dst][dst_neuron_id]["block"][0]
        dst_blk_y = universal_functions.brain[cortical_area_dst][dst_neuron_id]["block"][1]
        # print(src_blk_x, dst_blk_x, "---", src_blk_y, dst_blk_y)
        if abs(src_blk_x - dst_blk_x) < 8 and abs(src_blk_y - dst_blk_y) < 8:
            is_candidate = True

    return is_candidate


def block_id_gen(x, y, z, block_size=28):
    """
    Generating a block id so it can be used for faster neighbor detection
    """
    bx = ceil(x / block_size)
    by = ceil(y / block_size)
    bz = ceil(z / block_size)
    return [bx, by, bz]


def block_id_gen2(coordinate, space_dimensions, block_size=28):
    """
    Generating a block id so it can be used for faster neighbor detection
    """
    block_id = []
    index = 0
    for location in coordinate:
        block_id.append(ceil(location / ceil(space_dimensions[index] / block_size)))
        index += 1
    return block_id


def neurons_in_same_block(cortical_area, neuron_id):
    """
    Generates a list of Neurons in the same block as the given one
    """
    neuron_list = []
    for _ in universal_functions.brain[cortical_area]:
        if universal_functions.brain[cortical_area][_]['block'] == \
                universal_functions.brain[cortical_area][neuron_id]['block']:
            if _ != neuron_id:
                neuron_list.append(_)
    return neuron_list


def neurons_in_the_block(cortical_area, block_id):
    """
    Generates a list of Neurons in the given block
    block_id to be entered as [x,y,z]
    """
    neuron_list = []
    for neuron_id in universal_functions.brain[cortical_area]:
        if universal_functions.brain[cortical_area][neuron_id]['block'] == block_id:
            neuron_list.append(neuron_id)
    return neuron_list


def neighboring_blocks(block_id, kernel_size):
    """
    Returns the list of block ids who are neighbor of the given one
    Block_id is in form of [x,y,z]
    """

    block_list = list()

    kernel_half = floor(kernel_size / 2)
    seed_id = [block_id[0] - kernel_half, block_id[1] - kernel_half, block_id[2] - kernel_half]

    for i in range(0, kernel_size):
        for ii in range(0, kernel_size):
            for iii in range(0, kernel_size):
                neighbor_block_id = [seed_id[0] + i, seed_id[1] + ii, seed_id[2] + iii]
                if neighbor_block_id != block_id and \
                        neighbor_block_id[0] > 0 and \
                        neighbor_block_id[1] > 0 and \
                        neighbor_block_id[2] > 0:
                    block_list.append(neighbor_block_id)

    return block_list


def neurons_in_block_neighborhood(cortical_area, neuron_id, kernel_size=3):
    """
    Provides the list of all neurons within the surrounding blocks given the kernel size with default being 3
    """
    neuron_list = list()
    neuron_block_id = universal_functions.brain[cortical_area][neuron_id]['block']
    block_list = neighboring_blocks(neuron_block_id, kernel_size)
    for _ in block_list:
        neurons_in_block = neurons_in_the_block(cortical_area, _)
        for __ in neurons_in_block:
            neuron_list.append(__)
    return neuron_list


def neurons_in_block_neighborhood_2(cortical_area, block_id, kernel_size=3):
    """
    Provides the list of all neurons within the surrounding blocks given the kernel size with default being 3
    """
    neuron_list = list()
    block_list = neighboring_blocks(block_id, kernel_size)
    for _ in block_list:
        neurons_in_block = neurons_in_the_block(cortical_area, _)
        for __ in neurons_in_block:
            neuron_list.append(__)
    return neuron_list
