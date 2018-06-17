
import json
import datetime
import os.path
from datetime import datetime
from genethesizer import genome_id_gen
import IPU_vision


global parameters
if 'parameters' not in globals():
    with open("./configuration/parameters.json", "r") as data_file:
        parameters = json.load(data_file)
        print("Parameters has been read from file")


number_to_train = 0
training_neuron_list = []
training_counter = parameters["InitData"]["training_counter_default"]
training_rounds = parameters["InitData"]["training_rounds_default"]
training_start_time = datetime.now()
training_has_begun = False
training_mode = ""
labeled_image = []


# Load a copy of all MNIST training images into mnist_data in form of an iterator. Each object has image label + image
mnist_iterator = IPU_vision.read_mnist_raw()
mnist_array = []
for _ in mnist_iterator:
    mnist_array.append(_)
print(len(mnist_array))


if parameters["Switches"]["vis_show"]:
    import matplotlib as mpl
    mpl.use('TkAgg')
    import matplotlib.pyplot as plt


def init_burst_visualization():
    # global burst_figure
    # burst_figure = plt.figure(figsize=plt.figaspect(.15))
    # plt.thismanager = plt.get_current_fig_manager()
    # plt.thismanager.window.wm_geometry("+80+800")

    input_figure = plt.figure(figsize=(2, 3))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+20+600")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    vision_figure = plt.figure(figsize=(6, 10))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+300+20")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=.98, wspace=0.2, hspace=0)

    memory_figure = plt.figure(figsize=(2, 6))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+920+300")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    output_figure = plt.figure(figsize=(2, 3))
    plt.thismanager = plt.get_current_fig_manager()
    plt.thismanager.window.wm_geometry("+1200+600")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


def vis_init():
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d

    # plt.ion()
    print("Initializing plot...")
    # global Arrow3D

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
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 30)
        ax.set_zlim(0, 30)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        fig.suptitle("Main plot")

    parameters["Switches"]["vis_init_status"] = True


# Reads the list of all Cortical areas defined in Genome
def cortical_list():
    blueprint = genome["blueprint"]
    cortical_list = []
    for key in blueprint:
        cortical_list.append(key)
    return cortical_list


def cortical_group_members(group):
    members = []
    for item in cortical_list():
        if genome['blueprint'][item]['group_id'] == group:
            members.append(item)
    return members


def cortical_sub_group_members(group):
    members = []
    for item in cortical_list():
        if genome['blueprint'][item]['sub_group_id'] == group:
            members.append(item)
    return members


def load_genome_metadata_in_memory():
    with open(parameters["InitData"]["genome_file"], "r") as data_file:
        genome_db = json.load(data_file)
        genome_metadata = genome_db["genome_metadata"]
    return genome_metadata


global genome_metadata
genome_metadata = load_genome_metadata_in_memory()


def load_genome_in_memory():
    from genethesizer import genome_selector
    genome_id = genome_selector()
    with open(parameters["InitData"]["genome_file"], "r") as data_file:
        genome_db = json.load(data_file)
        genome = genome_db[genome_id]["properties"]
        # genome_stats = genome_db[gene_id]["stats"]
    return genome


# Resets the in-memory brain for each cortical area
def reset_brain():
    cortical_areas = cortical_list()
    for item in cortical_areas:
        brain[item] = {}
    return brain


def load_rules_in_memory():
    with open(parameters["InitData"]["rules_path"], "r") as data_file:
        rules = json.load(data_file)
    # print("Rules has been successfully loaded into memory...")
    return rules


def load_brain_in_memory():
    cortical_areas = cortical_list()
    brain = {}
    for item in cortical_areas:
        if os.path.isfile(parameters["InitData"]["connectome_path"] + item + '.json'):
            with open(parameters["InitData"]["connectome_path"] + item + '.json', "r") as data_file:
                data = json.load(data_file)
                brain[item] = data
    # print("Brain has been successfully loaded into memory...")
    return brain


def save_brain_to_disk(cortical_area='all'):
    if cortical_area != 'all':
        with open(parameters["InitData"]["connectome_path"]+cortical_area+'.json', "r+") as data_file:
            data = brain[cortical_area]

            # print("...All data related to Cortical area %s is saved in connectome\n" % cortical_area)
            # Saving changes to the connectome
            data_file.seek(0)  # rewind
            data_file.write(json.dumps(data, indent=3))
            data_file.truncate()
    else:
        for cortical_area in cortical_list():
            with open(parameters["InitData"]["connectome_path"]+cortical_area+'.json', "r+") as data_file:
                data = brain[cortical_area]
                print(">>> >>> All data related to Cortical area %s is saved in connectome" % cortical_area)
                # Saving changes to the connectome
                data_file.seek(0)  # rewind
                data_file.write(json.dumps(data, indent=3))
                data_file.truncate()
    return


def save_genome_to_disk():
    with open(parameters["InitData"]["genome_file"], "r+") as data_file:
        genome_db = json.load(data_file)

        new_genome_id = genome_id_gen()

        genome_db[new_genome_id] = {}
        genome_db[new_genome_id]["generation_date"] = str(datetime.now())
        genome_db[new_genome_id]["properties"] = genome
        genome_db[new_genome_id]["stats"] = genome_stats
        genome_db["genome_metadata"]["most_recent_genome_id"] = new_genome_id

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
    for cortical_area in brain:
        for neuron in brain[cortical_area]:
            brain[cortical_area][neuron]['cumulative_fire_count_inst'] = 0
    return


global genome
genome = load_genome_in_memory()

global genome_id
genome_id = ""

global genome_stats
genome_stats = {"test_stats": {}, "performance_stats": {}}

global blueprint
blueprint = cortical_list()

global brain
brain = load_brain_in_memory()

global event_id
event_id = '_'

global cortical_areas
cortical_areas = cortical_list()

global rules
rules = load_rules_in_memory()