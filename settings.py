
"""
This file contains all the Global settings and parameters used throughout the project
"""
import json
import os.path
import matplotlib.pyplot as plt
from stats import cortical_xyz_range

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
    burst_timer = 1e-17

    global idle_burst_timer
    idle_burst_timer = 2

    # Flag to enable Verbose mode
    global verbose
    verbose = False

    # Variable containing user input to train and control the Brain
    global user_input
    user_input = ''

    global user_input_param
    user_input = ''

    # Flag to show visualizations
    global vis_show
    vis_show = True

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

    global event_id
    event_id = '_'

    global ready_to_exit_burst
    ready_to_exit_burst = False

    global vis_init_status
    vis_init_status = False

    global cortical_areas
    cortical_areas = cortical_list()

    global max_xyz_range
    max_xyz_range = cortical_xyz_range()


    # >>>>>>>>>>>>   Items below here should not be needed anymore in Settings file    <<<<<<<<<<<<<<<

    # # todo: Move this to the Genome
    # # A location tolerance factor for Neuron location approximation
    # global image_color_intensity_tolerance
    # image_color_intensity_tolerance = 250


    global sobel_x, sobel_y
    sobel_x = [[-1, 0, 1], [-2, 0, 1], [-1, 0, 1]]
    sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]


def vis_init():
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d
    from mpl_toolkits.mplot3d import axes3d
    import matplotlib.patches as patches

    plt.ion()
    print("Initializing plot...")
    global Arrow3D
    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)

        # plt.ion()
        fig = plt.figure()
        global ax
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 30)
        ax.set_zlim(0, 30)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        fig.suptitle("Main plot")

        global figure
        figure = plt.figure(figsize=plt.figaspect(.15))

    global vis_init_status
    vis_init_status = True


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
