
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


def build_synapse(brain, key):
    # Read Genome data
    genome = universal_functions.genome

    timer = datetime.datetime.now()
    synapse_count, universal_functions.brain = \
        architect.neighbor_builder(brain=brain, brain_gen=True, cortical_area=key,
                                   rule_id=genome["blueprint"][key]["neighbor_locator_rule_id"],
                                   rule_param=genome["neighbor_locator_rule"][genome["blueprint"][key]
                                                                                    ["neighbor_locator_rule_id"]]
                                                                             [genome["blueprint"][key]
                                                                                    ["neighbor_locator_rule_param_id"]],
                                   postsynaptic_current=genome["blueprint"][key]["postsynaptic_current"])
    print("Synapse creation for Cortical area %s is now complete. Count: %i  Duration: %s"
          % (key, synapse_count, datetime.datetime.now() - timer))
    universal_functions.save_brain_to_disk(key)
    return


def build_synapse_ext(brain, key):
    # Read Genome data
    genome = universal_functions.genome
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
        print("Completed Synapse Creation between Cortical area %s and %s. Count: %i  Duration: %s"
              % (key, mapped_cortical_area, synapse_count, datetime.datetime.now() - timer))
    universal_functions.save_brain_to_disk(key)
    return


def main():

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

    # Read Genome data, reset connectome and build it up
    genome_data = universal_functions.genome
    blueprint = universal_functions.cortical_list()

    print("Here is the list of all defined cortical areas: %s " % blueprint)

    # # Reset Connectume
    for key in blueprint:
        file_name = 'connectome/'+key+'.json'
        with open(file_name, "w") as connectome:
            connectome.write(json.dumps({}))
            connectome.truncate()
        print(settings.Bcolors.YELLOW + "Cortical area %s is has been cleared." % key
              + settings.Bcolors.ENDC)

    # Develop Neurons for various cortical areas defined in Genome
    for cortical_area in blueprint:
        timer = datetime.datetime.now()
        neuron_count = architect.three_dim_growth(cortical_area)
        print("Neuron Creation for Cortical area %s is now complete. Count: %i  Duration: %s"
              % (cortical_area, neuron_count, datetime.datetime.now() - timer))

    # Build Synapses within all Cortical areas
    func1 = partial(build_synapse, universal_functions.brain)
    pool1 = Pool(processes=8)
    synapse_creation_candidates = []
    for key in blueprint:
        if genome_data["blueprint"][key]["init_synapse_needed"]:
            synapse_creation_candidates.append(key)
        else:
            print("Synapse creation for Cortical area %s has been skipped." % key)

    universal_functions.save_brain_to_disk()

    pool1.map(func1, synapse_creation_candidates)
    pool1.close()
    pool1.join()

    stats.brain_total_synapse_cnt()

    # universal_functions.init_data()
    # Build Synapses across various Cortical areas
    func2 = partial(build_synapse_ext, universal_functions.brain)
    pool2 = Pool(processes=7)
    pool2.map(func2, blueprint)
    pool2.close()
    pool2.join()
    print("Neuronal mapping across all Cortical areas has been completed!!")

    print("Total brain synapse count is: ", stats.brain_total_synapse_cnt())

    # universal_functions.save_brain_to_disk()
