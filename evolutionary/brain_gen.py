
"""
This script is responsible for the creation of The Brain from scratch using Genome data
"""

import json
import shutil
import errno
import datetime
from functools import partial
from multiprocessing import Pool

from . import architect
from misc import universal_functions, stats
from configuration import settings


def build_synapse(brain, connectome_path, key):
    # Read Genome data
    genome = universal_functions.load_genome_in_memory()

    timer = datetime.datetime.now()
    synapse_count, universal_functions.brain = \
        architect.neighbor_builder(brain=brain, brain_gen=True, cortical_area=key,
                                   rule_id=genome["blueprint"][key]["neighbor_locator_rule_id"],
                                   rule_param=genome["neighbor_locator_rule"][genome["blueprint"][key]
                                                                                    ["neighbor_locator_rule_id"]]
                                                                             [genome["blueprint"][key]
                                                                                    ["neighbor_locator_rule_param_id"]],
                                   postsynaptic_current=genome["blueprint"][key]["postsynaptic_current"])
    if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
        print("Synapse creation for Cortical area %s is now complete. Count: %i  Duration: %s"
              % (key, synapse_count, datetime.datetime.now() - timer))
    universal_functions.save_brain_to_disk(key, connectome_path=connectome_path)
    return


def build_synapse_ext(brain, connectome_path, key):
    # Read Genome data
    genome = universal_functions.load_genome_in_memory()
    for mapped_cortical_area in genome["blueprint"][key]["cortical_mapping_dst"]:
        timer = datetime.datetime.now()
        synapse_count, universal_functions.brain = \
            architect.neighbor_builder_ext(brain=brain, brain_gen=True, cortical_area_src=key,
                                           cortical_area_dst=mapped_cortical_area,
                                           rule=genome["blueprint"][key]["cortical_mapping_dst"][mapped_cortical_area]
                                           ["neighbor_locator_rule_id"],
                                           rule_param=genome["neighbor_locator_rule"]
                                                            [genome["blueprint"][key]
                                                                   ["cortical_mapping_dst"][mapped_cortical_area]
                                                                   ["neighbor_locator_rule_id"]]
                                                            [genome["blueprint"][key]
                                                                   ["cortical_mapping_dst"]
                                                                   [mapped_cortical_area]
                                                                   ["neighbor_locator_rule_param_id"]],
                                           postsynaptic_current=genome["blueprint"][key]["postsynaptic_current"])
        if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
            print("Completed Synapse Creation between Cortical area %s and %s. Count: %i  Duration: %s"
                  % (key, mapped_cortical_area, synapse_count, datetime.datetime.now() - timer))
    universal_functions.save_brain_to_disk(key, connectome_path=connectome_path)
    return


def main():
    genome = universal_functions.load_genome_in_memory()

    # Backup the old brain
    def folder_backup(src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise

    if universal_functions.parameters["Switches"]["folder_backup"]:
        # Backup the current folder
        folder_backup('../Metis', '../Metis_archive/Metis_'+str(datetime.datetime.now()).replace(' ', '_'))

    # Reset in-memory brain data
    universal_functions.reset_brain()

    # print("Current brain: >>> >>> >> >>\n", universal_functions.brain)

    # Read Genome data, reset connectome and build it up
    blueprint = universal_functions.cortical_list()
    # print("Current blueprint: >>> >>> >> >>\n", blueprint)

    if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
        print("Here is the list of all defined cortical areas: %s " % blueprint)

    print("::::: connectome path is:", universal_functions.parameters["InitData"]["connectome_path"])

    # # Reset Connectume
    for key in blueprint:
        file_name = universal_functions.parameters["InitData"]["connectome_path"]+key+'.json'
        with open(file_name, "w") as connectome:
            connectome.write(json.dumps({}))
            connectome.truncate()
        if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
            print(settings.Bcolors.YELLOW + "Cortical area %s is has been cleared." % key
                  + settings.Bcolors.ENDC)

    # Develop Neurons for various cortical areas defined in Genome
    for cortical_area in blueprint:
        timer = datetime.datetime.now()
        neuron_count = architect.three_dim_growth(cortical_area)
        if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
            print("Neuron Creation for Cortical area %s is now complete. Count: %i  Duration: %s"
                  % (cortical_area, neuron_count, datetime.datetime.now() - timer))

    universal_functions.save_brain_to_disk()

    # Build Synapses within all Cortical areas
    func1 = partial(build_synapse, universal_functions.brain,
                    universal_functions.parameters['InitData']['connectome_path'])
    pool1 = Pool(processes=8)

    synapse_creation_candidates = []
    for key in blueprint:
        if genome["blueprint"][key]["init_synapse_needed"]:
            synapse_creation_candidates.append(key)
        else:
            if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
                print("Synapse creation for Cortical area %s has been skipped." % key)

    pool1.map(func1, synapse_creation_candidates)
    pool1.close()
    pool1.join()

    stats.brain_total_synapse_cnt()

    # Build Synapses across various Cortical areas
    func2 = partial(build_synapse_ext, universal_functions.brain,
                    universal_functions.parameters['InitData']['connectome_path'])
    pool2 = Pool(processes=7)

    pool2.map(func2, blueprint)
    pool2.close()
    pool2.join()

    if universal_functions.parameters["Logs"]["print_brain_gen_activities"]:
        print("Neuronal mapping across all Cortical areas has been completed!!")

    print("Total brain synapse count is: ", stats.brain_total_synapse_cnt())

    # universal_functions.save_brain_to_disk()
