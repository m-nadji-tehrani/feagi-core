
"""
This script is responsible for the creation of The Brain from scratch using Genome data
"""

import json
import shutil
import errno
import datetime
import multiprocessing
from multiprocessing import Pool, Process


import architect
import visualizer
import settings


def build_synapse(key):
    # Read Genome data
    genome = settings.genome

    timer = datetime.datetime.now()
    synapse_count = architect.neighbor_builder(cortical_area=key,
                                               rule_id=genome["blueprint"][key]["neighbor_locator_rule_id"],
                                               rule_param=genome["neighbor_locator_rule"][genome["blueprint"][key]
                                               ["neighbor_locator_rule_id"]][genome["blueprint"][key]
                                               ["neighbor_locator_rule_param_id"]],
                                               synaptic_strength=genome["blueprint"][key]["synaptic_strength"])
    print("Synapse creation for Cortical area %s is now complete. Count: %i  Duration: %s"
          % (key, synapse_count, datetime.datetime.now() - timer))
    return


def build_synapse_ext(key):
    # Read Genome data
    genome = settings.genome
    for mapped_cortical_area in genome["blueprint"][key]["cortical_mapping_dst"]:
        timer = datetime.datetime.now()
        synapse_count = architect.neighbor_builder_ext(cortical_area_src=key,
                                       cortical_area_dst=mapped_cortical_area,
                                       rule=genome["blueprint"][key]["cortical_mapping_dst"][mapped_cortical_area]
                                       ["neighbor_locator_rule_id"],
                                       rule_param=genome["neighbor_locator_rule"][genome["blueprint"][key]
                                       ["cortical_mapping_dst"][mapped_cortical_area]
                                       ["neighbor_locator_rule_id"]][genome["blueprint"][key]["cortical_mapping_dst"]
                                       [mapped_cortical_area]["neighbor_locator_rule_param_id"]],
                                       synaptic_strength=genome["blueprint"][key]["synaptic_strength"])
        print("Completed Synapse Creation between Cortical area %s and %s. Count: %i  Duration: %s"
              % (key, mapped_cortical_area, synapse_count, datetime.datetime.now() - timer))
    return


def main():

    # Backup the old brain
    def copyanything(src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise

    # Backup the current folder
    # copyanything('../Metis', '../Metis_archive/Metis_'+str(datetime.datetime.now()).replace(' ', '_'))


    # Reset in-memory brain data
    settings.reset_brain()

    # Read Genome data, reset connectome and build it up
    data = settings.genome
    blueprint = settings.cortical_list()

    print("Here is the list of all defined cortical areas: %s " % blueprint)

    # # Reset Connectume
    for key in blueprint:
        file_name = 'connectome/'+key+'.json'
        with open(file_name, "w") as connectome:
            connectome.write(json.dumps({}))
            connectome.truncate()
        print("Cortical area %s is has been cleared." % key)

    # Develop Neurons for various cortical areas defined in Genome
    for key in blueprint:
        timer = datetime.datetime.now()
        neuron_count = architect.three_dim_growth(key)
        print("Neuron Creation for Cortical area %s is now complete. Count: %i  Duration: %s"
              % (key, neuron_count, datetime.datetime.now() - timer))

    # Build Synapses within all Cortical areas
    pool1 = Pool(processes=7)
    synapse_creation_candidates = []
    for key in blueprint:
        if data["blueprint"][key]["init_synapse_needed"] == "True":
            synapse_creation_candidates.append(key)
        else:
            print("Synapse creation for Cortical area %s has been skipped." % key)
    pool1.map(build_synapse, synapse_creation_candidates)
    pool1.close()
    pool1.join()

    # Build Synapses across various Cortical areas
    pool2 = Pool(processes=7)
    pool2.map(build_synapse_ext, blueprint)
    pool2.close()
    pool2.join()
    print("Neuronal mapping across all Cortical areas has been completed!!")

    # # Visualize Neurons and Synapses
    # if settings.vis_show:
    #     for key in blueprint:
    #         visualizer.connectome_visualizer(cortical_area=key, neighbor_show='true')

    settings.save_brain_to_disk()
