
import json
import datetime
import os.path
import glob
import pickle
from datetime import datetime
from genethesizer import genome_id_gen
import IPU_vision
import settings


global parameters
if 'parameters' not in globals():
    with open("./configuration/parameters.json", "r") as data_file:
        parameters = json.load(data_file)
        print("Parameters has been read from file")

training_neuron_list_utf = []
training_neuron_list_img = []
labeled_image = []

global brain_is_running
brain_is_running = False
brain_run_id = ""


if parameters["Switches"]["capture_brain_activities"]:
    global fcl_history
    fcl_history = {}


class InjectorParams:
    img_flag = False
    utf_flag = False
    injection_has_begun = False
    variation_handler = True
    exposure_handler = True
    utf_handler = True
    variation_counter = parameters["Auto_injector"]["variation_default"]
    exposure_counter = parameters["Auto_injector"]["exposure_default"]
    utf_counter = parameters["Auto_injector"]["utf_default"]
    variation_counter_actual = variation_counter
    exposure_counter_actual = exposure_counter
    utf_counter_actual = utf_counter
    injection_start_time = datetime.now()
    num_to_inject = ''
    utf_to_inject = ''
    injection_mode = ''


class TesterParams:
    img_flag = False
    utf_flag = False
    testing_has_begun = False
    variation_handler = True
    exposure_handler = True
    utf_handler = True
    variation_counter = parameters["Auto_tester"]["variation_default"]
    exposure_counter = parameters["Auto_tester"]["exposure_default"]
    utf_counter = parameters["Auto_tester"]["utf_default"]
    variation_counter_actual = variation_counter
    exposure_counter_actual = exposure_counter
    utf_counter_actual = utf_counter
    test_start_time = datetime.now()
    num_to_inject = ''
    test_mode = ''
    comprehension_counter = 0
    test_attempt_counter = 0
    temp_stats = []
    test_stats = {}
    test_id = ""

    # Load copy of all MNIST training images into mnist_data in form of an iterator. Each object has image label + image


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
        global fig
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
    global genome_stats, genome
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


def toggle_verbose_mode():
    if parameters["Switches"]["verbose"]:
        parameters["Switches"]["verbose"] = False
        print("Verbose mode is Turned OFF!")
    else:
        parameters["Switches"]["verbose"] = True
        print("Verbose mode is Turned On!")


def toggle_visualization_mode():
    if parameters["Switches"]["vis_show"]:
        parameters["Switches"]["vis_show"] = False
        print("Visualization mode is Turned OFF!")
    else:
        parameters["Switches"]["vis_show"] = True
        print("Visualization mode is Turned On!")


def toggle_injection_mode():
    if parameters["Auto_injector"]["injector_status"]:
        parameters["Auto_injector"]["injector_status"] = False
        print("Auto_train mode is Turned OFF!")
    else:
        parameters["Auto_injector"]["injector_status"] = True
        print("Auto_train mode is Turned On!")


def toggle_test_mode():
    if parameters["Auto_tester"]["tester_status"]:
        parameters["Auto_tester"]["tester_status"] = False
        print("Auto_test mode is Turned OFF!")
    else:
        parameters["Auto_tester"]["tester_status"] = True
        print("Auto_test mode is Turned On!")


def toggle_brain_status():
    global brain_is_running
    if brain_is_running:
        brain_is_running = False
        print("Brain is not running!")
    else:
        brain_is_running = True
        print("Brain is now running!!!")


def save_fcl_to_disk():
    global fcl_history
    global brain_run_id
    with open("./fcl_repo/fcl-" + brain_run_id + ".json", 'w') as fcl_file:
        # Saving changes to the connectome
        fcl_file.seek(0)  # rewind
        fcl_file.write(json.dumps(fcl_history, indent=3))
        fcl_file.truncate()

    print("Brain activities has been preserved!")


def load_fcl_in_memory(file_name):
    with open(file_name, 'r') as fcl_file:
        fcl_data = json.load(fcl_file)
    return fcl_data


def latest_fcl_file():
    list_of_files = glob.glob('./fcl_repo/*.json')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def pickler(data, id):
    id = brain_run_id
    with open("./pickle_jar/fcl-" + id + ".pkl", 'wb') as output:
        pickle.dump(data, output)


def unpickler(data_type, id):
    if data_type == 'fcl':
        with open("./pickle_jar/fcl-" + id + ".pkl", 'rb') as input_data:
            data = pickle.load(input_data)
    else:
        print("Error: Type not found!")
    return data


if parameters["Switches"]["vis_show"]:
    if parameters["Switches"]["visualize_latest_file"]:
        fcl_file = latest_fcl_file()
    else:
        fcl_file = parameters["InitData"]["fcl_to_visualize"]

    fcl_burst_data_set = load_fcl_in_memory(fcl_file)


global genome_id
genome_id = ""

global genome
genome = load_genome_in_memory()

global genome_stats
genome_stats = {}

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
