
# import random
# import string
from datetime import datetime
import os.path
import json
from misc import db_handler, alerts, stats
from configuration import runtime_data, settings


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


def load_genome_in_memory(connectome_path, static=False):
    if not static:
        print("Genome from local connectome folder was chosen: ", connectome_path)
        with open(connectome_path+'genome_tmp.json', "r") as genome_file:
            genome_data = json.load(genome_file)
            runtime_data.genome = genome_data
    else:
        print("Static genome from the following file was loaded in memory: ",
              runtime_data.parameters["InitData"]["static_genome_path"])
        with open(runtime_data.parameters["InitData"]["static_genome_path"], "r") as genome_file:
            genome_data = json.load(genome_file)
            runtime_data.genome = genome_data


def save_genome_to_disk():
    from evolutionary.genethesizer import calculate_brain_cognitive_fitness
    mongo = db_handler.MongoManagement()
    genome = runtime_data.genome
    genome_id = runtime_data.genome_id

    updated_genome_test_stats = []
    for item in runtime_data.genome_test_stats:
        item["genome_id"] = genome_id
        updated_genome_test_stats.append(item)

    # print(updated_genome_test_stats)
    # print("*** @@@ *** @@@ *** \n ", genome_id)

    genome_db = {}
    genome_db["genome_id"] = genome_id
    genome_db["generation_date"] = str(datetime.now())
    genome_db["properties"] = genome

    brain_fitness = calculate_brain_cognitive_fitness(runtime_data.genome_test_stats)
    genome_db["fitness"] = brain_fitness

    print("Brain fitness factor was evaluated as: ", brain_fitness)

    # print("*** @@@ *** @@@ *** \n ", genome_db)

    mongo.insert_genome(genome_db)

    mail_body = "Genome " + str(genome_id) + " has been evaluated to have a fitness of " + str(brain_fitness)

    # Sending out email
    # if brain_fitness > runtime_data.parameters["Alerts"]["email_fitness_threshold"]:
    #     alerts.send_email(mail_body)

    for stat in runtime_data.genome_test_stats:
        stat_to_save = stat
        mongo.insert_test_stats(stat_to_save)

    print("Genome %s has been preserved for future generations!" % genome_id)
    stats.print_fcl_stats(genome_id)

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
    print("Brain has been successfully loaded into memory...")
    return brain


def genome_handler(connectome_path):
    # Calling function to regenerate the Brain from the Genome
    if runtime_data.parameters["InitData"]["regenerate_brain"]:
        print("use_static_genome:", runtime_data.parameters["Switches"]["use_static_genome"])
        if runtime_data.parameters["Switches"]["use_static_genome"]:
            print("** ** ** ** ** ** ** ** **")
            load_genome_in_memory(connectome_path, static=True)
            print(settings.Bcolors.RED + ">> >> >> A static genome was used to generate the brain."
                  + settings.Bcolors.ENDC)
        else:
            stage_genome(connectome_path)
            load_genome_in_memory(connectome_path)
    else:
        # Using the existing genome previously staged in the connectome_path
        load_genome_in_memory(connectome_path)


def serialize_brain_data(brain):
    for cortical_area in brain:
        for neuron_id in brain[cortical_area]:
            runtime_data.brain[cortical_area][neuron_id]["activity_history"] = \
                list(runtime_data.brain[cortical_area][neuron_id]["activity_history"])
    return brain


def load_block_dic_in_memory():
    # todo: Need error handling added so if there is a corruption in block_dic data it can regenerate
    connectome_path = runtime_data.parameters["InitData"]["connectome_path"]
    block_dic = {}
    for item in runtime_data.cortical_list:
        if os.path.isfile(connectome_path + item + '_blk_dic.json'):
            with open(connectome_path + item + '_blk_dic.json', "r") as data_file:
                data = json.load(data_file)
                block_dic[item] = data
    return block_dic


def save_block_dic_to_disk(cortical_area='all', block_dic=runtime_data.block_dic,
                           parameters=runtime_data.parameters, backup=False):
    connectome_path = parameters["InitData"]["connectome_path"]
    if block_dic == {}:
        print(">> >> Error: Could not save the brain contents to disk as >> block_dic << was empty!")
        return

    if cortical_area != 'all':
        with open(connectome_path+cortical_area+'_blk_dic.json', "w") as data_file:
            data = block_dic[cortical_area]
            data_file.seek(0)  # rewind
            data_file.write(json.dumps(data, indent=3))
            data_file.truncate()
    elif backup:
        for cortical_area in runtime_data.cortical_list:
            with open(connectome_path+cortical_area+'_backup_blk_dic.json', "w") as data_file:
                data = block_dic[cortical_area]
                data_file.seek(0)  # rewind
                data_file.write(json.dumps(data, indent=3))
                data_file.truncate()
    else:
        for cortical_area in runtime_data.cortical_list:
            with open(connectome_path+cortical_area+'_blk_dic.json', "w") as data_file:
                data = block_dic[cortical_area]
                data_file.seek(0)  # rewind
                data_file.write(json.dumps(data, indent=3))
                data_file.truncate()
    return


def save_brain_to_disk(cortical_area='all', brain=runtime_data.brain, parameters=runtime_data.parameters, backup=False):
    connectome_path = parameters["InitData"]["connectome_path"]
    if brain == {}:
        print(">> >> Error: Could not save the brain contents to disk as brain was empty!")
        return
    brain = serialize_brain_data(brain)
    if cortical_area != 'all':
        with open(connectome_path+cortical_area+'.json', "r+") as data_file:
            data = brain[cortical_area]
            # print("...All data related to Cortical area %s is saved in connectome\n" % cortical_area)
            # Saving changes to the connectome
            data_file.seek(0)  # rewind
            data_file.write(json.dumps(data, indent=3))
            data_file.truncate()
    elif backup:
        for cortical_area in runtime_data.cortical_list:
            with open(connectome_path+cortical_area+'_backup.json', "w") as data_file:
                data = brain[cortical_area]
                # if runtime_data.parameters["Logs"]["print_brain_gen_activities"]:
                    # print(">>> >>> All data related to Cortical area %s is saved in connectome" % cortical_area)
                # Saving changes to the connectome
                data_file.seek(0)  # rewind
                data_file.write(json.dumps(data, indent=3))
                data_file.truncate()
    else:
        for cortical_area in runtime_data.cortical_list:
            with open(connectome_path+cortical_area+'.json', "r+") as data_file:
                data = brain[cortical_area]
                # if runtime_data.parameters["Logs"]["print_brain_gen_activities"]:
                    # print(">>> >>> All data related to Cortical area %s is saved in connectome" % cortical_area)
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


def save_fcl_in_db(burst_number, fire_candidate_list, number_under_training):
    mongo = db_handler.MongoManagement()
    fcl_data = {}
    fcl_data['genome_id'] = runtime_data.genome_id
    fcl_data['burst_id'] = burst_number
    fcl_data['number_under_training'] = number_under_training
    fcl_data['fcl_data'] = fire_candidate_list
    mongo.insert_neuron_activity(fcl_data=fcl_data)
