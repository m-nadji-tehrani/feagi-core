""" This module contains functions capable of modifying and shaping the Genome"""

import settings


class GeneModifier:
    def change_cortical_neuron_count(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron density aka Cortical Neuron Count in a given cortical area"""
        settings.genome['blueprint'][cortical_area]['cortical_neuron_count'] += \
            settings.genome['blueprint'][cortical_area]['cortical_neuron_count'] * change_percentage
        return

    def change_firing_threshold(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron firing threshold in a given cortical area"""
        settings.genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] += \
            settings.genome['blueprint'][cortical_area]['neuron_params']['firing_threshold'] * change_percentage
        return

    def change_timer_threshold(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron timer threshold in a given cortical area"""
        settings.genome['blueprint'][cortical_area]['neuron_params']['timer_threshold'] += \
            settings.genome['blueprint'][cortical_area]['neuron_params']['timer_threshold'] * change_percentage
        return

    def change_consecutive_fire_cnt_max(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron consecutive_fire_cnt_max in a given cortical area"""
        settings.genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] += \
            settings.genome['blueprint'][cortical_area]['neuron_params']['consecutive_fire_cnt_max'] * change_percentage
        return

    def change_snooze_length(self, cortical_area, change_percentage):
        """ Function to increase or decrease the neuron snooze_length in a given cortical area"""
        settings.genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] += \
            settings.genome['blueprint'][cortical_area]['neuron_params']['snooze_length'] * change_percentage
        return


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

# print(genethesize())