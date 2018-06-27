""" This module contains functions capable of modifying and shaping the Genome"""

import datetime
import random
import string
from misc import db_handler
from math import floor


def select_a_genome():
    """
    This function randomly selects a genetic operation from following options to produce a genome:
    1. Crossover two randomly selected genomes
    2. Random selection from available genomes
    3. Latest genome
    4. Best fitness ever
    5. Mutate genome with highest fitness
    6. TBD
    """
    random_selector = random.randrange(1, 6, 1)

    if random_selector == 1:
        print("Crossover is happening...")
        genome = crossover()

    elif random_selector == 2:
        print("A random genome is being selected...")
        genome = random_genome()

    elif random_selector == 3:
        print("Most recent genome is being selected...")
        genome = latest_genome()

    elif random_selector == 4:
        print("The genome with highest fitness so far has been selected...")
        genome = highest_fitness_genome()

    elif random_selector == 5:
        print("Gene mutation has occurred...")
        genome = mutate(highest_fitness_genome())

    # elif random_selector == 6:
    #     genome =

    return genome


class GeneModifier:
    @staticmethod
    def change_cortical_neuron_count(genome, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron density aka Cortical Neuron Count in a given cortical area"""
        genome['blueprint'][cortical_area]['cortical_neuron_count'] += \
            floor(genome['blueprint'][cortical_area]['cortical_neuron_count'] * change_percentage)
        if genome['blueprint'][cortical_area]['cortical_neuron_count'] < 0:
            genome['blueprint'][cortical_area]['cortical_neuron_count'] = 0
        return genome

    @staticmethod
    def change_firing_threshold(genome, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron firing threshold in a given cortical area"""
        genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] += \
            genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] * change_percentage
        if genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] < 0:
            genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] = 0
        return genome

    @staticmethod
    def change_depolarization_timer_threshold(genome, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron timer threshold in a given cortical area"""
        genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold'] += \
            genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold'] * change_percentage
        if genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold'] < 0:
            genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold'] = 0
        return genome

    @staticmethod
    def change_consecutive_fire_cnt_max(genome, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron consecutive_fire_cnt_max in a given cortical area"""
        genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] += \
            floor(genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] * change_percentage)
        if genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] < 0:
            genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] = 0
        return genome

    @staticmethod
    def change_snooze_length(genome, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron snooze_length in a given cortical area"""
        genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] += \
            genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] * change_percentage
        if genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] < 0:
            genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] = 0
        return genome


def genome_id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    """
    This function generates a unique id which will be associated with each GEnome

    """
    # Rand gen source partially from:
    # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return (str(datetime.datetime.now()).replace(' ', '_')).replace('.', '_')+'_'+(''.join(random.choice(chars) for _ in range(size)))+'_G'


def generation_assessment():
    """ A collection of assessments to evaluate the performance of the Genome"""
    return


def genethesize():
    """ Responsible for generating a complete set of Genome"""

    genome = {}
    genome["firing_patterns"] = {
      "A": {
         "frequency": "100",
         "magnitude": "80"
      },
      "B": {
         "frequency": "20",
         "magnitude": "100"
      }
   }
    genome["neighbor_locator_rule"] = {
      "rule_0": {
         "param_1": 5,
         "param_2": 0
      },
      "rule_1": {
         "param_1": 5,
         "param_2": 5
      },
      "rule_2": {
         "param_1": 5,
         "param_2": 5,
         "param_3": 10
      },
      "rule_3": {
         "param_1": 0,
         "param_2": 0
      }
   }
    return genome


def mutate(genome):
    factor_1 = random.randrange(-30, 30, 1) / 100
    factor_2 = random.randrange(-30, 30, 1) / 100
    factor_3 = random.randrange(-30, 30, 1) / 100
    factor_4 = random.randrange(-30, 30, 1) / 100
    factor_5 = random.randrange(-30, 30, 1) / 100

    blueprint = genome["blueprint"]
    cortical_list = []
    for key in blueprint:
        cortical_list.append(key)

    for cortical_area in cortical_list:
        genome = GeneModifier.change_consecutive_fire_cnt_max(genome, cortical_area, factor_1)
        genome = GeneModifier.change_cortical_neuron_count(genome, cortical_area, factor_2)
        genome = GeneModifier.change_depolarization_timer_threshold(genome, cortical_area, factor_3)
        genome = GeneModifier.change_firing_threshold(genome, cortical_area, factor_4)
        genome = GeneModifier.change_snooze_length(genome, cortical_area, factor_5)

    return genome


def get_genome_candidate():
    """ Scans genome db for a high performing genome and returns one from top 10% by random """
    genome = db_handler.MongoManagement.top_n_genome(1)
    return genome


def crossover():
    """
    To corssover genome 1 and 2, first list of keys from one genome is read and the content of that key
    is swapped with the other genome.
    """
    db = db_handler.MongoManagement()
    # todo: Need ability to cross over a part of blueprint
    genome_1, genome_2 = db.id_list_2_genome_list(db.random_m_from_top_n(2, 5))

    genome_1 = genome_1["properties"]
    genome_2 = genome_2["properties"]

    genome_1_keys = []
    for key in genome_1.keys():
        genome_1_keys.append(key)

    # Select a random key
    random_key = genome_1_keys[random.randrange(len(genome_1_keys))]

    print("Crossing over: ", random_key)

    genome_1_rnd_segment = genome_1[random_key]

    genome_2_orig = genome_2

    # Cross over
    genome_2[random_key] = genome_1_rnd_segment

    print("--- Gene crossover has occurred ---")

    return genome_2


def random_genome():
    db = db_handler.MongoManagement()
    genomes = db.id_list_2_genome_list(db.random_m_from_top_n(1, 5))
    for item in genomes:
        genome = item
    # print("this is the random genome", genome)
    return genome['properties']


def latest_genome():
    db = db_handler.MongoManagement()
    genome = db.latest_genome()
    return genome['properties']


def highest_fitness_genome():
    db = db_handler.MongoManagement()
    genome = db.highest_fitness_genome()
    return genome['properties']


def translate_genotype2phenotype():
    return


def calculate_fitness(test_stats):
    """
    Calculate the effectiveness of a given genome:
    1. Fitness value will be a number between 0 and 100 with 100 the highest fitness possible (how can there be limit?)
    2. Brain activeness should be considered as a factor. Brain that only guessed one number and that one correctly
          should not be considered better than a brain that guessed 100s of numbers 95% correct.
    3. Number of guess attempts vs. number of correct guesses is a factor

    Fitness calculation formula:

    TE = Total number of times brain has been exposed to a character
    TC = Total number of times brain has comprehended a number correctly
    AF = Activity factor that is measured by a threshold.
        - < 10 exposures leads to 0
        - > 10 & < 50 exposures leads to n / 50 factor
        - > 50 exposures leads to 1

    TC / TE = Percentage of correct comprehensions

    Genome fitness factor = AF * TC / TE

    """
    total_exposure, total_comprehended = genome_stats_analytics(test_stats)

    if total_exposure < 10:
        activity_factor = 0
    elif 10 <= total_exposure <= 50:
        activity_factor = total_exposure / 50
    else:
        activity_factor = 1

    if total_exposure == 0:
        fitness = 0
    else:
        fitness = activity_factor * total_comprehended / total_exposure

    return fitness


def genome_stats_analytics(test_stats):
    exposure_total = 0
    comprehended_total = 0
    for test in test_stats:
        for key in test:
            if "exposed" in key:
                exposure_total += test[key]
            if "comprehended" in key:
                comprehended_total += test[key]

    return exposure_total, comprehended_total


def calculate_survival_prob():
    return


def compare_genomes():
    return


def synthesize_new_gen():
    return


def selection():
    return


def spin_new_generation():
    return


if __name__ == "__main__":
    # print(genethesize())


    # genome_1 = {"a": 3, "b": {"name": "mohammad", "last": "nadji"}, "c": 5}
    # genome_2 = {"a": 1, "b": {"name": "jafar", "last": "gholi"}, "c": 6}
    #
    # print(crossover(genome_1, genome_2))

    # a = crossover()
    # for _ in a:
    #     print(_)
    # print(calculate_fitness())

    genome_data = {
         "generation_date": "2018-06-24 00:28:49_410237",
         "properties": {
              "firing_patterns": {
                 "A": {
                    "frequency": "100",
                    "magnitude": "80"
                 },
                 "B": {
                    "frequency": "20",
                    "magnitude": "100"
                 }
              },
              "neighbor_locator_rule": {
                 "rule_0": {
                    "param_1": 1,
                    "param_2": 0
                 },
                 "rule_1": {
                    "param_1": 2,
                    "param_2": 1
                 },
                 "rule_2": {
                    "param_1": 5,
                    "param_2": 5,
                    "param_3": 10
                 },
                 "rule_3": {
                    "param_1": 0,
                    "param_2": 0
                 },
                 "rule_4": {
                    "param_1": 25,
                    "param_2": 100
                 },
                 "rule_5": {
                    "param_1": 700,
                    "param_2": 700,
                    "param_3": 700,
                    "param_4": 700,
                    "param_5": 700,
                    "param_6": 700,
                    "param_7": 700
                 },
                 "rule_6": {
                    "param_1": 0,
                    "param_2": 0
                 }
              },
              "IPU_vision_filters": {
                 "3": {
                    "-": [
                       [
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "|": [
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ]
                    ],
                    " ": [
                       [
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0
                       ]
                    ],
                    "o": [
                       [
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          4,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "/": [
                       [
                          -1,
                          -1,
                          1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          1,
                          -1,
                          -1
                       ]
                    ],
                    "\\": [
                       [
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1
                       ]
                    ]
                 },
                 "5": {
                    "-": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          1,
                          1,
                          1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    " ": [
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0
                       ]
                    ],
                    "|": [
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ]
                    ],
                    "o": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "/": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "\\": [
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ]
                    ]
                 },
                 "7": {
                    "-": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          1,
                          1,
                          1,
                          1,
                          1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    " ": [
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ],
                       [
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0
                       ]
                    ],
                    "I": [
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "i": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "o": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "/": [
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ]
                    ],
                    "\\": [
                       [
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1,
                          -1
                       ],
                       [
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          -1,
                          1
                       ]
                    ]
                 }
              },
              "location_tolerance": 2,
              "image_color_intensity_tolerance": 250,
              "max_burst_count": 3,
              "evolution_burst_count": 100,
              "performance_stats": {
                 "mnist_view_cnt": 0,
                 "mnist_correct_detection_cnt": 0
              },
              "blueprint": {
                 "vision_v1-1": {
                    "growth_path": "",
                    "direction_sensitivity": "/",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 1,
                    "layer_index": 1,
                    "total_layer_count": 7,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_1"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             5
                          ]
                       }
                    }
                 },
                 "vision_v1-2": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 4,
                    "layer_index": 2,
                    "total_layer_count": 7,
                    "direction_sensitivity": "\\",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 750,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             5
                          ]
                       }
                    }
                 },
                 "vision_v1-3": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 7,
                    "layer_index": 3,
                    "total_layer_count": 7,
                    "direction_sensitivity": "|",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 501,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_3"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-4": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 10,
                    "layer_index": 4,
                    "total_layer_count": 7,
                    "direction_sensitivity": "-",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_4"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-5": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 13,
                    "layer_index": 5,
                    "total_layer_count": 7,
                    "direction_sensitivity": "I",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_5"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-6": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 16,
                    "layer_index": 6,
                    "total_layer_count": 7,
                    "direction_sensitivity": "o",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_6"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v1-7": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v1",
                    "plot_index": 19,
                    "layer_index": 7,
                    "total_layer_count": 7,
                    "direction_sensitivity": " ",
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 500,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "vision_v2": {
                          "neighbor_locator_rule_id": "rule_5",
                          "neighbor_locator_rule_param_id": "param_7"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "orientation_selectivity_id": "",
                       "firing_threshold": 3,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             28
                          ],
                          "y": [
                             0,
                             28
                          ],
                          "z": [
                             0,
                             10
                          ]
                       }
                    }
                 },
                 "vision_v2": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_v2",
                    "plot_index": 2,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 3,
                    "cortical_neuron_count": 1000,
                    "location_generation_type": "random",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 0.5,
                    "postsynaptic_current_max": 2,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_2",
                    "cortical_mapping_dst": {
                       "vision_IT": {
                          "neighbor_locator_rule_id": "rule_6",
                          "neighbor_locator_rule_param_id": "param_1"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "orientation_selectivity_id": "",
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             500
                          ],
                          "y": [
                             0,
                             500
                          ],
                          "z": [
                             0,
                             200
                          ]
                       }
                    }
                 },
                 "vision_IT": {
                    "growth_path": "",
                    "group_id": "vision",
                    "sub_group_id": "vision_IT",
                    "plot_index": 3,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 1000,
                    "location_generation_type": "random",
                    "synapse_attractivity": 80,
                    "init_synapse_needed": True,
                    "postsynaptic_current": 1,
                    "plasticity_constant": 0.5,
                    "postsynaptic_current_max": 2,
                    "neighbor_locator_rule_id": "rule_1",
                    "neighbor_locator_rule_param_id": "param_2",
                    "cortical_mapping_dst": {
                       "vision_memory": {
                          "neighbor_locator_rule_id": "rule_4",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 0.5,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             500
                          ],
                          "y": [
                             0,
                             500
                          ],
                          "z": [
                             0,
                             250
                          ]
                       }
                    }
                 },
                 "vision_memory": {
                    "growth_path": "",
                    "group_id": "Memory",
                    "sub_group_id": "vision",
                    "plot_index": 1,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 2000,
                    "location_generation_type": "random",
                    "synapse_attractivity": 10,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 0.5,
                    "plasticity_constant": 0.12,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {},
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 2,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 2,
                       "snooze_length": 4,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             300
                          ],
                          "y": [
                             0,
                             300
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 },
                 "utf8": {
                    "growth_path": "",
                    "group_id": "IPU",
                    "sub_group_id": "IPU_utf8",
                    "plot_index": 1,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 300,
                    "location_generation_type": "sequential",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 1.1,
                    "plasticity_constant": 0.05,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "utf8_memory": {
                          "neighbor_locator_rule_id": "rule_3",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 5,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 3,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             1
                          ],
                          "y": [
                             0,
                             1
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 },
                 "utf8_memory": {
                    "growth_path": "",
                    "group_id": "Memory",
                    "sub_group_id": "utf8",
                    "plot_index": 2,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 300,
                    "location_generation_type": "sequential",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 2,
                    "plasticity_constant": 1,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {
                       "utf8_out": {
                          "neighbor_locator_rule_id": "rule_3",
                          "neighbor_locator_rule_param_id": "param_2"
                       }
                    },
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 20,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 10,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             1
                          ],
                          "y": [
                             0,
                             1
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 },
                 "utf8_out": {
                    "growth_path": "",
                    "group_id": "OPU",
                    "sub_group_id": "OPU_utf8",
                    "plot_index": 1,
                    "orientation_selectivity_pattern": "",
                    "location": "",
                    "kernel_size": 7,
                    "cortical_neuron_count": 300,
                    "location_generation_type": "sequential",
                    "synapse_attractivity": 100,
                    "init_synapse_needed": False,
                    "postsynaptic_current": 0.51,
                    "plasticity_constant": 0.05,
                    "postsynaptic_current_max": 1,
                    "neighbor_locator_rule_id": "rule_0",
                    "neighbor_locator_rule_param_id": "param_1",
                    "cortical_mapping_dst": {},
                    "neuron_params": {
                       "activation_function_id": "",
                       "orientation_selectivity_id": "",
                       "depolarization_threshold": 20,
                       "firing_threshold": 1,
                       "firing_pattern_id": "",
                       "refractory_period": 0,
                       "axon_avg_length": "",
                       "axon_avg_connections": "",
                       "axon_orientation function": "",
                       "consecutive_fire_cnt_max": 1,
                       "snooze_length": 2,
                       "geometric_boundaries": {
                          "x": [
                             0,
                             1
                          ],
                          "y": [
                             0,
                             1
                          ],
                          "z": [
                             0,
                             300
                          ]
                       }
                    }
                 }
              }
           },
         }

    new_genome = mutate(genome_data["properties"])

    print(new_genome)
