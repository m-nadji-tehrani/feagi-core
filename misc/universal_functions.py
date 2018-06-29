


from configuration import runtime_data


# live_mode_status can have modes of idle, learning, testing, tbd
live_mode_status = 'idle'


training_neuron_list_utf = []
training_neuron_list_img = []
labeled_image = []

global brain_is_running
brain_is_running = False



def cortical_group_members(group):
    members = []
    for item in runtime_data.cortical_list:
        if runtime_data.genome['blueprint'][item]['group_id'] == group:
            members.append(item)
    return members


def reset_cumulative_counter_instances():
    """
    To reset the cumulative counter instances
    """
    for cortical_area in runtime_data.brain:
        for neuron in runtime_data.brain[cortical_area]:
            runtime_data.brain[cortical_area][neuron]['cumulative_fire_count_inst'] = 0
    return


def toggle_verbose_mode():
    if runtime_data.parameters["Switches"]["verbose"]:
        runtime_data.parameters["Switches"]["verbose"] = False
        print("Verbose mode is Turned OFF!")
    else:
        runtime_data.parameters["Switches"]["verbose"] = True
        print("Verbose mode is Turned On!")


def toggle_injection_mode():
    if runtime_data.parameters["Auto_injector"]["injector_status"]:
        runtime_data.parameters["Auto_injector"]["injector_status"] = False
        print("Auto_train mode is Turned OFF!")
    else:
        runtime_data.parameters["Auto_injector"]["injector_status"] = True
        print("Auto_train mode is Turned On!")


def toggle_test_mode():
    if runtime_data.parameters["Auto_tester"]["tester_status"]:
        runtime_data.parameters["Auto_tester"]["tester_status"] = False
        print("Auto_test mode is Turned OFF!")
    else:
        runtime_data.parameters["Auto_tester"]["tester_status"] = True
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

