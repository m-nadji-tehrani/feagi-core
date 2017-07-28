
"""
This file contains all the Global settings and parameters used throughout the project
"""
import json
import os.path

def init():

    global Bcolors
    class Bcolors:
        UPDATE = '\033[94m'
        BURST = '\033[93m'
        FIRE = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        HEADER = '\033[95m'
        OKGREEN = '\033[92m'



    # Sleep timer for visualization delay
    global burst_timer
    burst_timer = 0.00001

    # Flag to enable Verbose mode
    global verbose
    verbose = False

    # Flag to show visualizations
    global vis_show
    vis_show = False

    # Flag to show bursts
    global burst_show
    burst_show = False

    # Flag to read all Connectome data from memory instead of File
    global read_data_from_memory
    read_data_from_memory = True

    # connectome_path defines the folder where all connectome files reside
    global connectome_path
    connectome_path = './connectome/'

    # Genome defines the json file name and location which is acting as Human Genome
    global genome_file
    genome_file = './genome.json'

    global brain
    brain = load_brain_in_memory()

    global genome
    genome = load_genome_in_memory()

    global blueprint
    blueprint = cortical_list()

    # >>>>>>>>>>>>   Items below here should not be needed anymore in Settings file    <<<<<<<<<<<<<<<

    # todo: Move this to the Genome
    # A location tolerance factor for Neuron location approximation
    global location_tolerance
    location_tolerance = 0

    # todo: Move this to the Genome
    # A location tolerance factor for Neuron location approximation
    global image_color_intensity_tolerance
    image_color_intensity_tolerance = 250

    # todo: Move this to the Genome
    # Number of Max burst count allowed
    global max_burst_count
    max_burst_count = 100

    global sobel_x, sobel_y
    sobel_x = [[-1, 0, 1], [-2, 0, 1], [-1, 0, 1]]
    sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    # # Neuron locations for the ones participating in a Burst are passed to the visualization function
    # global input_neuron_locations
    # input_neuron_locations = [[10,10,10], [20, 20, 20]]

    # todo: Remove this, should not be needed anymore
    # connectome_file defines the json file name and location which is acting as Neuron database
    global connectome_file
    connectome_file = './connectome/vision_r01.json'

    # todo: Remove this, should not be needed anymore
    # List of neuron ids which will provide the initial input to the system
    global input_neuron_list_1
    input_neuron_list_1 = ["2017-03-13_17:25:50.219808_SELIU9",
                         "2017-03-13_17:25:18.518105_F8UZ7S",
                         "2017-03-13_16:53:44.927756_7YKHO2",
                         "2017-03-13_16:53:44.930625_GORNA5"]

    # todo: Remove this, should not be needed anymore
    global input_neuron_list_2
    input_neuron_list_2 = ["2017-03-13_16:53:44.928501_3EJP3N",
                     "2017-03-13_17:25:18.518105_F8UZ7S",
                     "2017-03-13_16:53:09.239461_FTNL8W",
                     "2017-03-13_16:53:44.930625_GORNA5",
                         "2017-03-13_16:53:44.931493_E0I80R"]


# Reads the list of all Cortical areas defined in Genome
def cortical_list():
    global genome_file
    with open(genome_file, "r") as data_file:
        data = json.load(data_file)
        blueprint = []
        for key in data['blueprint']:
            blueprint.append(key)

    return blueprint


def load_genome_in_memory():
    global genome_file
    with open(genome_file, "r") as data_file:
        genome = json.load(data_file)

    return genome


# Resets the in-memory brain for each cortical area
def reset_brain():
    global brain
    cortical_areas = cortical_list()
    for item in cortical_areas:
        brain[item] = {}
    return brain


def load_brain_in_memory():
    cortical_areas = cortical_list()
    brain = {}
    for item in cortical_areas:
        if os.path.isfile(connectome_path + item + '.json'):
            with open(connectome_path + item + '.json', "r") as data_file:
                data = json.load(data_file)
                brain[item] = data
    print("Brain has been successfully loaded into memory...")
    return brain


def save_brain_to_disk():
    for cortical_area in cortical_list():
        with open(connectome_path+cortical_area+'.json', "r+") as data_file:
            data = brain[cortical_area]

            print("All data related to Cortical area %s is saved in connectome" % cortical_area)

            # Saving changes to the connectome
            data_file.seek(0)  # rewind
            data_file.write(json.dumps(data, indent=3))
            data_file.truncate()

    return


def reset_cumulative_counter_instances():
    """
    To reset the cumulative counter instances
    """

    for cortical_area in brain:
        for neuron in brain[cortical_area]:
            brain[cortical_area][neuron]['cumulative_fire_count_inst'] = 0

    return
