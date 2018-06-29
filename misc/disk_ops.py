
# import random
# import string
import datetime
import os.path
import json
from misc import db_handler
from evolutionary.genethesizer import genome_id_gen
from configuration import runtime_data


# Reads the list of all Cortical areas defined in Genome
def cortical_list():
    blueprint = runtime_data.genome["blueprint"]
    cortical_list_ = []
    for key in blueprint:
        cortical_list_.append(key)
    return cortical_list_


def load_parameters_in_memory():
    with open("./configuration/parameters.json", "r") as data_file:
        runtime_data.parameters = json.load(data_file)
        # print("Parameters has been read from file")


def load_genome_in_memory(connectome_path):
    with open(connectome_path+'genome_tmp.json', "r") as genome_tmp_file:
        genome_data = json.load(genome_tmp_file)
        runtime_data.genome = genome_data
        # print("Genome has been loaded into memory...")


def save_genome_to_disk():
    from evolutionary.genethesizer import calculate_fitness
    mongo = db_handler.MongoManagement()
    global genome_test_stats, genome

    genome_id = ""

    if runtime_data.parameters["InitData"]["regenerate_brain"]:
        genome_id = genome_id_gen()
        print("this is the new genome id:", genome_id)

    print(genome_test_stats)

    updated_genome_test_stats = []
    for item in genome_test_stats:
        item["genome_id"] = genome_id
        updated_genome_test_stats.append(item)

    print(updated_genome_test_stats)

    genome_db = {}
    genome_db["genome_id"] = genome_id
    genome_db["generation_date"] = str(datetime.now())
    genome_db["properties"] = genome

    brain_fitness = calculate_fitness(genome_test_stats)
    genome_db["fitness"] = brain_fitness

    print("Brain fitness factor was evaluated as: ", brain_fitness)

    mongo.insert_genome(genome_db)

    for stat in genome_test_stats:
        stat_to_save = stat
        mongo.insert_test_stats(stat_to_save)

    print("Genome has been preserved for future generations!")

    return


def stage_genome(connectome_path):
    from evolutionary.genethesizer import select_a_genome
    genome_data = select_a_genome()
    with open(connectome_path+'genome_tmp.json', "w") as staged_genome:
        # Saving changes to the connectome
        staged_genome.seek(0)  # rewind
        staged_genome.write(json.dumps(genome_data, indent=3))
        staged_genome.truncate()

    print("<< << Genome has been staged in runtime repo >> >>")


def load_brain_in_memory():
    # todo: Need error handling added so if there is a corruption in brain data it can regenerate
    connectome_path = runtime_data.parameters["InitData"]["connectome_path"]
    brain = {}
    for item in runtime_data.cortical_list:
        if os.path.isfile(connectome_path + item + '.json'):
            with open(connectome_path + item + '.json', "r") as data_file:
                data = json.load(data_file)
                brain[item] = data
    # print("Brain has been successfully loaded into memory...")
    return brain


def save_brain_to_disk(cortical_area='all', brain=runtime_data.brain, parameters=runtime_data.parameters):
    connectome_path = parameters["InitData"]["connectome_path"]
    if brain == {}:
        print(">> >> Error: Could not save the brain contents to disk as brain was empty!")
        return
    if cortical_area != 'all':
        with open(connectome_path+cortical_area+'.json', "r+") as data_file:
            data = brain[cortical_area]
            # print("...All data related to Cortical area %s is saved in connectome\n" % cortical_area)
            # Saving changes to the connectome
            data_file.seek(0)  # rewind
            data_file.write(json.dumps(data, indent=3))
            data_file.truncate()
    else:
        for cortical_area in runtime_data.cortical_list:
            with open(connectome_path+cortical_area+'.json', "r+") as data_file:
                data = brain[cortical_area]
                if runtime_data.parameters["Logs"]["print_brain_gen_activities"]:
                    print(">>> >>> All data related to Cortical area %s is saved in connectome" % cortical_area)
                # Saving changes to the connectome
                data_file.seek(0)  # rewind
                data_file.write(json.dumps(data, indent=3))
                data_file.truncate()
    return


def load_rules_in_memory():
    with open(runtime_data.parameters["InitData"]["rules_path"], "r") as data_file:
        rules = json.load(data_file)
    # print("Rules has been successfully loaded into memory...")
    return rules


