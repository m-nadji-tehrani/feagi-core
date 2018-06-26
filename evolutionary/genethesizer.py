""" This module contains functions capable of modifying and shaping the Genome"""

from misc import universal_functions
import datetime
import random
import string
import db_handler


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
    random_selector = random.randrange(1, 4, 1)

    if random_selector == 1:
        print("Crossover is happening...")
        genome = crossover()
        # print("mohammad aghaye ghandi:", genome)
    elif random_selector == 2:
        print("A random genome is being selected...")
        genome = random_genome()
        # print("mohammad aghaye ghandi:", genome)
    elif random_selector == 3:
        print("The latest genome is being selected...")
        genome = latest_genome()
        # print("mohammad aghaye ghandi:", genome)
    # elif random_selector == 4:
    #     genome =
    # elif random_selector == 5:
    #     genome =
    # elif random_selector == 6:
    #     genome =

    return genome


class GeneModifier:
    def change_cortical_neuron_count(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron density aka Cortical Neuron Count in a given cortical area"""
        universal_functions.genome['blueprint'][cortical_area]['cortical_neuron_count'] += \
            universal_functions.genome['blueprint'][cortical_area]['cortical_neuron_count'] * change_percentage
        return

    def change_firing_threshold(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron firing threshold in a given cortical area"""
        universal_functions.genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] += \
            universal_functions.genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] * change_percentage
        return

    def change_depolarization_timer_threshold(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron timer threshold in a given cortical area"""
        universal_functions.genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold'] += \
            universal_functions.genome['blueprint'][cortical_area]['neuron_params']['depolarization_threshold'] * change_percentage
        return

    def change_consecutive_fire_cnt_max(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron consecutive_fire_cnt_max in a given cortical area"""
        universal_functions.genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] += \
            universal_functions.genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] * change_percentage
        return

    def change_snooze_length(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron snooze_length in a given cortical area"""
        universal_functions.genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] += \
            universal_functions.genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] * change_percentage
        return


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


def genome_selector():
    genome_id = universal_functions.genome_metadata["most_recent_genome_id"]
    return genome_id


def mutate(genome):
    factor_1 = random(1,50,1)
    factor_2 = random(1,50,1)
    factor_3 = random(1,50,1)
    factor_4 = random(1,50,1)
    factor_5 = random(1,50,1)

    for cortical_area in universal_functions.cortical_list():
        GeneModifier.change_consecutive_fire_cnt_max(cortical_area, factor_1)
        GeneModifier.change_cortical_neuron_count(cortical_area, factor_2)
        GeneModifier.change_depolarization_timer_threshold(cortical_area, factor_3)
        GeneModifier.change_firing_threshold(cortical_area, factor_4)
        GeneModifier.change_snooze_length(cortical_area, factor_5)
    return genome


def crossover():
    """
    To corssover genome 1 and 2, first list of keys from one genome is read and the content of that key
    is swapped with the other genome.
    """
    # todo: Need ability to cross over a part of blueprint
    db = db_handler.MongoManagement()
    genome_1, genome_2 = db.random_genome(n=2)

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
    genomes = db.random_genome(n=1)
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

    print("9")
    # genome_1 = {"a": 3, "b": {"name": "mohammad", "last": "nadji"}, "c": 5}
    # genome_2 = {"a": 1, "b": {"name": "jafar", "last": "gholi"}, "c": 6}
    #
    # print(crossover(genome_1, genome_2))

    # a = crossover()
    # for _ in a:
    #     print(_)
    print(calculate_fitness())