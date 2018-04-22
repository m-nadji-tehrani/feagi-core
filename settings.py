
"""
This file contains all the Global settings and parameters used throughout the project
"""
import json
import datetime
import os.path
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from stats import cortical_xyz_range
from genethesizer import genome_id_gen

# print("Settings has been initialized!")


def init_timers():
    # Sleep timer for visualization delay
    global burst_timer
    burst_timer = 1e-17

    global idle_burst_timer
    idle_burst_timer = 2

    global auto_train_delay
    auto_train_delay = 3

    global auto_train_delay2
    auto_train_delay2 = 50

    global auto_test_delay
    auto_test_delay = 3

    global block_size
    block_size = 10


def init_messaging():
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

    # Flag to enable Verbose mode
    global verbose
    verbose = False


def init_user_interactions():
    # Variable containing user input to train and control the Brain
    global user_input
    user_input = ''

    global previous_user_input
    previous_user_input = ''

    global user_input_param
    user_input_param = ''

    global previous_user_input_param
    previous_user_input_param = ''

    global opu_char
    opu_char = 'X'

    global comprehended_char
    comprehended_char = ''

def init_visualization():
    # Flag to show visualizations
    global vis_show
    vis_show = False
    if vis_show:
        init_burst_visualization()

    global vis_init_status
    vis_init_status = False


def init_data():
    # Flag to read all Connectome data from memory instead of File
    global read_data_from_memory
    read_data_from_memory = True

    global regenerate_brain
    regenerate_brain = True

    # connectome_path defines the folder where all connectome files reside
    global connectome_path
    connectome_path = './connectome/'


    # rules_path defines the folder where all connectome files reside
    global rules_path
    rules_path = './reproduction/rules.json'


    # Genome defines the json file name and location which is acting as Human Genome
    global genome_file
    genome_file = './reproduction/genome.json'

    global brain
    brain = load_brain_in_memory()

    global genome
    genome = load_genome_in_memory()

    global genome_id
    genome_id = ""

    global genome_stats
    genome_stats = {}

    global blueprint
    blueprint = cortical_list()

    global event_id
    event_id = '_'

    global cortical_areas
    cortical_areas = cortical_list()

    global rules
    rules = load_rules_in_memory()

    # global max_xyz_range
    # max_xyz_range = cortical_xyz_range()


def init_settings():
    global auto_train
    auto_train = True

    global ready_to_exit_burst
    ready_to_exit_burst = False




    # >>>>>>>>>>>>   Items below here should not be needed anymore in Settings file    <<<<<<<<<<<<<<<

    # # todo: Move this to the Genome
    # # A location tolerance factor for Neuron location approximation
    # global image_color_intensity_tolerance
    # image_color_intensity_tolerance = 250

    # global sobel_x, sobel_y
    # sobel_x = [[-1, 0, 1], [-2, 0, 1], [-1, 0, 1]]
    # sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]


def init_burst_visualization():
    # global burst_figure
    # burst_figure = plt.figure(figsize=plt.figaspect(.15))
    # plt.thismanager = plt.get_current_fig_manager()
    # plt.thismanager.window.wm_geometry("+80+800")

    global input_figure
    input_figure = plt.figure(figsize=(2, 3))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+20+600")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    global vision_figure
    vision_figure = plt.figure(figsize=(6, 10))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+300+20")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=.98, wspace=0.2, hspace=0)

    global memory_figure
    memory_figure = plt.figure(figsize=(2, 6))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+920+300")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    global output_figure
    output_figure = plt.figure(figsize=(2, 3))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+1200+600")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


def vis_init():
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d
    from mpl_toolkits.mplot3d import axes3d
    import matplotlib.patches as patches

    # plt.ion()
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

    global vis_init_status
    vis_init_status = True


# Reads the list of all Cortical areas defined in Genome
def cortical_list():
    blueprint = load_genome_in_memory()["blueprint"]

    cortical_list = []
    for key in blueprint:
        cortical_list.append(key)

    return cortical_list


def genome_selector():
    """ Need to add logics to this function to chose Genome using Genetic Algorithm"""
    genome_id = "genome_id_ABCD"
    return genome_id


def load_genome_in_memory():
    global genome_id
    genome_id = genome_selector()
    global genome_file
    with open(genome_file, "r") as data_file:
        genome_db = json.load(data_file)
        genome = genome_db[genome_id]["properties"]
        # genome_stats = genome_db[gene_id]["stats"]
    return genome


# Resets the in-memory brain for each cortical area
def reset_brain():
    global brain
    cortical_areas = cortical_list()
    for item in cortical_areas:
        brain[item] = {}
    return brain


def load_rules_in_memory():
    global rules_path
    with open(rules_path, "r") as data_file:
        rules = json.load(data_file)
    # print("Rules has been successfully loaded into memory...")
    return rules


def load_brain_in_memory():
    cortical_areas = cortical_list()
    brain = {}
    for item in cortical_areas:
        if os.path.isfile(connectome_path + item + '.json'):
            with open(connectome_path + item + '.json', "r") as data_file:
                data = json.load(data_file)
                brain[item] = data
    # print("Brain has been successfully loaded into memory...")
    return brain


def save_brain_to_disk(cortical_area='all'):
    if cortical_area != 'all':
        with open(connectome_path+cortical_area+'.json', "r+") as data_file:
            data = brain[cortical_area]

            # print("...All data related to Cortical area %s is saved in connectome\n" % cortical_area)
            # Saving changes to the connectome
            data_file.seek(0)  # rewind
            data_file.write(json.dumps(data, indent=3))
            data_file.truncate()
    else:
        for cortical_area in cortical_list():
            with open(connectome_path+cortical_area+'.json', "r+") as data_file:
                data = brain[cortical_area]

                print(">>> >>> All data related to Cortical area %s is saved in connectome\n" % cortical_area)

                # Saving changes to the connectome
                data_file.seek(0)  # rewind
                data_file.write(json.dumps(data, indent=3))
                data_file.truncate()
    return


def save_genome_to_disk():
    with open(genome_file, "r+") as data_file:
        genome_db = json.load(data_file)

        new_genome_id = genome_id_gen()

        genome_db[new_genome_id] = {}
        genome_db[new_genome_id]["generation_date"] = str(datetime.datetime.now())
        genome_db[new_genome_id]["properties"] = genome
        genome_db[new_genome_id]["stats"] = genome_stats

        # Saving changes to the connectome
        data_file.seek(0)  # rewind
        data_file.write(json.dumps(genome_db, indent=3))
        data_file.truncate()

        print("Genome has been preserved for future generations!")
    return


def reset_cumulative_counter_instances():
    """
    To reset the cumulative counter instances
    """
    global brain
    for cortical_area in brain:
        for neuron in brain[cortical_area]:
            brain[cortical_area][neuron]['cumulative_fire_count_inst'] = 0
    return
