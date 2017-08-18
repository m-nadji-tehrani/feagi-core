
"""
This file contains all of the Visualization functions
"""

import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from mpl_toolkits.mplot3d import proj3d


import settings
import architect
import neuron_functions


def connectome_visualizer(cortical_area, neighbor_show='false', threshold=0):
    """Visualizes the Neurons in the connectome"""
    if not settings.vis_init_status:
        settings.vis_init()
    neuron_locations = architect.connectome_location_data(cortical_area)

    settings.ax.set_xlim(settings.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0],
                 settings.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1])
    settings.ax.set_ylim(settings.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0],
                 settings.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1])
    settings.ax.set_zlim(settings.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0],
                 settings.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1])

    for location in neuron_locations:
        settings.ax.scatter(location[0], location[1], location[2], c='b', marker='.')

    # Displays the Axon-Dendrite connections when True is set
    if neighbor_show == 'true':
        data = settings.brain[cortical_area]

        # The following code scans thru connectome and extract locations for source and destination neurons
        for key in data:
            if data[key]["neighbors"].keys():
                source_location = data[key]["location"]
                for subkey in data[key]["neighbors"]:
                    if (data[key]['neighbors'][subkey]['cortical_area'] == cortical_area) and (data[key]['neighbors']
                                [subkey]['synaptic_strength'] > threshold):
                        destination_location = data[subkey]["location"]
                        a = settings.Arrow3D([source_location[0], destination_location[0]], [source_location[1],
                                    destination_location[1]], [source_location[2], destination_location[2]],
                                    mutation_scale=10, lw=1, arrowstyle="->", color="r")
                        settings.ax.add_artist(a)
    settings.plt.show()
    settings.plt.pause(settings.burst_timer)
    return


def burst_visualizer(fire_candidate_list):

    neuron_locations = neuron_functions.fire_candidate_locations(fire_candidate_list)

    index = 0
    indexed_cortical_list = []
    for key in settings.cortical_areas:
        indexed_cortical_list.append([index, key])
        index += 1

    # Toggle the visual appearance of the Neuron to resemble firing action
    for entry in indexed_cortical_list:
        axx = settings.burst_figure.add_subplot(1, len(indexed_cortical_list), entry[0] + 1, projection='3d')
        axx.set_title(entry[1])
        axx.set_xlim(settings.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                     settings.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
        axx.set_ylim(settings.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                     settings.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
        axx.set_zlim(settings.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                     settings.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
        axx.set_xlabel('X Label')
        axx.set_ylabel('Y Label')
        axx.set_zlabel('Z Label')

        for location in neuron_locations[entry[1]]:
            axx.scatter(location[0], location[1], location[2], c='r', marker='^')

    settings.plt.draw()
    settings.plt.pause(settings.burst_timer)
    settings.plt.clf()
    axx.cla()

    return


def cortical_activity_visualizer(cortical_areas, x=30, y=30, z=30):
    """Visualizes the extent of Neuron activities"""
    if not settings.vis_init_status:
        settings.vis_init()

    # fig = settings.plt.figure()
    fig = settings.plt.figure(figsize=settings.plt.figaspect(.2))
    fig.suptitle('Cortical Activities\n')

    for cortical_area in cortical_areas:
        neuron_locations = architect.connectome_location_data(cortical_area)
        aa = fig.add_subplot(1, len(cortical_areas)+1, cortical_areas.index(cortical_area)+1)
        aa.set_title(cortical_area)
        aa.set_xlim(0, x)
        aa.set_ylim(0, y)
        # aa.set_zlim(0, z)
        for location in neuron_locations:
            # aa.scatter(location[0], location[1], location[2], s=location[3])
            aa.scatter(location[0], location[1], s=location[3])
    settings.plt.show()
    settings.plt.pause(1)
    return


def cortical_heatmap(IPU_input, cortical_areas):
    """
    Create a 2D heatmap for the requested Cortical area based on the level of Neuronal activity
    :param cortical_area:
    :return:
    """
    # if not settings.vis_init_status:
    #     settings.vis_init()
    settings.plt.ion()

    cortical_arrays = []
    cortical_arrays.append(["IPU_Vision", IPU_input])
    # for cortical_area in cortical_areas:
    #     genome = settings.genome
    #     x1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0]
    #     x2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1]
    #     y1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0]
    #     y2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1]
    #
    #     # Convert Cortical data to a numpy array
    #     data = settings.brain[cortical_area]
    #     cortical_array = np.zeros((x2-x1, y2-y1))
    #     for key in data:
    #         xx = data[key]['location'][0]
    #         yy = data[key]['location'][1]
    #         cortical_array[xx, yy] = data[key]['cumulative_fire_count_inst']
    #     cortical_arrays.append([cortical_area, cortical_array])

    # print(cortical_arrays)
    # print(cortical_arrays[0][1])

    fig2 = settings.plt.figure(num=None, figsize=(8, 8), dpi=28, facecolor='w', edgecolor='k')

    pylab.thismanager = pylab.get_current_fig_manager()
    pylab.thismanager.window.wm_geometry("+10+800")

    for i in range(1, len(cortical_areas)+2):
        aa = fig2.add_subplot(1, len(cortical_areas)+1, i)
        aa.set_title(cortical_arrays[i-1][0])
        aa.imshow(cortical_arrays[i-1][1])

    settings.plt.suptitle('Heatmap of Cortical area Neuronal Fire count', fontsize=12)

    # plt.pause(10)
    settings.plt.show()
    return
