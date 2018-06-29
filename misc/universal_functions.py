

from datetime import datetime
from configuration.runtime_data import parameters as runtime_parameters
from configuration.runtime_data import genome as runtime_genome
from configuration.runtime_data import brain as runtime_brain


# live_mode_status can have modes of idle, learning, testing, tbd
live_mode_status = 'idle'


training_neuron_list_utf = []
training_neuron_list_img = []
labeled_image = []

global brain_is_running
brain_is_running = False


class InjectorParams:
    img_flag = False
    utf_flag = False
    injection_has_begun = False
    variation_handler = True
    exposure_handler = True
    utf_handler = True
    variation_counter = runtime_parameters["Auto_injector"]["variation_default"]
    exposure_counter = runtime_parameters["Auto_injector"]["exposure_default"]
    utf_counter = runtime_parameters["Auto_injector"]["utf_default"]
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
    variation_counter = runtime_parameters["Auto_tester"]["variation_default"]
    exposure_counter = runtime_parameters["Auto_tester"]["exposure_default"]
    utf_counter = runtime_parameters["Auto_tester"]["utf_default"]
    variation_counter_actual = variation_counter
    exposure_counter_actual = exposure_counter
    utf_counter_actual = utf_counter
    test_start_time = datetime.now()
    num_to_inject = ''
    test_mode = ''
    comprehension_counter = 0
    test_attempt_counter = 0
    # temp_stats = []
    test_stats = {}
    test_id = ""

    # Load copy of all MNIST training images into mnist_data in form of an iterator. Each object has image label + image



def cortical_group_members(group):
    members = []
    for item in cortical_list():
        if runtime_genome['blueprint'][item]['group_id'] == group:
            members.append(item)
    return members


def reset_cumulative_counter_instances():
    """
    To reset the cumulative counter instances
    """
    for cortical_area in runtime_brain:
        for neuron in runtime_brain[cortical_area]:
            runtime_brain[cortical_area][neuron]['cumulative_fire_count_inst'] = 0
    return


def toggle_verbose_mode():
    if runtime_parameters["Switches"]["verbose"]:
        runtime_parameters["Switches"]["verbose"] = False
        print("Verbose mode is Turned OFF!")
    else:
        runtime_parameters["Switches"]["verbose"] = True
        print("Verbose mode is Turned On!")


def toggle_injection_mode():
    if runtime_parameters["Auto_injector"]["injector_status"]:
        runtime_parameters["Auto_injector"]["injector_status"] = False
        print("Auto_train mode is Turned OFF!")
    else:
        runtime_parameters["Auto_injector"]["injector_status"] = True
        print("Auto_train mode is Turned On!")


def toggle_test_mode():
    if runtime_parameters["Auto_tester"]["tester_status"]:
        runtime_parameters["Auto_tester"]["tester_status"] = False
        print("Auto_test mode is Turned OFF!")
    else:
        runtime_parameters["Auto_tester"]["tester_status"] = True
        print("Auto_test mode is Turned On!")


def toggle_brain_status():
    global brain_is_running
    if brain_is_running:
        brain_is_running = False
        print("Brain is not running!")
    else:
        brain_is_running = True
        print("Brain is now running!!!")


global genome_id
genome_id = ""


global event_id
event_id = '_'

global blueprint
blueprint = ""

# global rules
# rules = ""

