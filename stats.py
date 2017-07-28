
"""
Provides functions performing statistical analysis on the Connectome and Cortical behavior
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json


import settings


plt.style.use('ggplot')

blueprint = settings.cortical_list()


def connectome_neuron_count(cortical_area):
    """
    Returns number of Neurons in the connectome
    """
    data = settings.brain[cortical_area]
    neuron_count = 0
    for key in data:
        neuron_count += 1
    return neuron_count


def connectome_total_synapse_cnt(cortical_area):
    """
    Returns average number of Synapses for all Neurons in the connectome
    """
    data = settings.brain[cortical_area]
    total_synapse_count = 0
    for neuron in data:
        for synapse in data[neuron]['neighbors']:
            total_synapse_count += 1
    return total_synapse_count





global raw
raw = []


def connectome_neighbor_histogram(cortical_area):
    """
    Plots a Histogram of count of neighbor relationships per Neuron in a Cortical area
    """
    data = settings.brain[cortical_area]
    for key in data:
        count = 0
        for y in data[key]['neighbors']:
            count += 1
        raw.append([cortical_area, count])

    return


def print_cortical_stats():
    for cortical_area in settings.cortical_list():
        print("%s total Neuron count: %i" % (cortical_area, connectome_neuron_count(cortical_area)))
        print("%s average synapse count per Neuron: %i" % (cortical_area, connectome_total_synapse_cnt(cortical_area)/connectome_neuron_count(cortical_area)))
    return


# def tbd():
#     for key in blueprint:
#         connectome_neighbor_histogram(key)
#
#     df = pd.DataFrame(raw)
#     print(df)
#     print(df[1])
#     # df.plot(kind='hist', stacked=True, bins=20)
#
#     plt.show()
#
#     return


# def cortical_synaptic_strengths(cortical_area):
#     """
#     list Neurons along with destination neuron and Synaptic strenght associated with them.
#
#     :param cortical_area:
#     :return:
#     """
#     synaptic_strengths = []
#     data = settings.brain[cortical_area]
#     for key in data:
#         for neighbor in data[key]["neighbors"]:
#
#
#
#     return synaptic_strengths



