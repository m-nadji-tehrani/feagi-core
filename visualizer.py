
"""
This file contains all of the Visualization functions
"""

import json
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d import axes3d
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import time

import settings
import architect

global init_status
init_status = False


def init():
    plt.ion()
    print("Initializing plot...")
    global Arrow3D
    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)

        plt.ion()
        fig = plt.figure()
        global ax
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 30)
        ax.set_zlim(0, 30)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
    global init_status
    init_status = True


def connectome_visualizer(cortical_area, x=30, y=30, z=30, neighbor_show='false'):
    """Visualizes the Neurons in the connectome"""
    global init_status
    if not init_status:
        init()
    neuron_locations = architect.connectome_location_data(cortical_area)
    ax.set_xlim(0, x)
    ax.set_ylim(0, y)
    ax.set_zlim(0, z)

    for location in neuron_locations:
        ax.scatter(location[0], location[1], location[2], c='b', marker='.')

    # Displays the Axon-Dendrite connections when True is set
    if neighbor_show == 'true':
        data = settings.brain[cortical_area]

        # The following code scans thru connectome and extract locations for source and destination neurons
        for key in data:
            if data[key]["neighbors"].keys() != []:
                source_location = data[key]["location"]
                for subkey in data[key]["neighbors"]:
                    if data[key]['neighbors'][subkey]['cortical_area'] == cortical_area:
                        destination_location = data[subkey]["location"]
                        a = Arrow3D([source_location[0], destination_location[0]], [source_location[1],
                                    destination_location[1]], [source_location[2], destination_location[2]],
                                    mutation_scale=10, lw=1, arrowstyle="->", color="r")
                        ax.add_artist(a)
    plt.show()
    return


def burst_visualizer(neuron_locations):
    """This function receives the coordinate location for firing neuron and will have it visualized"""
    global init_status
    if not init_status:
        init()
    # Toggle the visual appearance of the Neuron to resemble firing action
    for location in neuron_locations:
        ax.scatter(location[0], location[1], location[2], c='r', marker='^')
    plt.pause(settings.burst_timer)

    for location in neuron_locations:
        ax.scatter(location[0], location[1], location[2], c='b', marker='^')
    plt.pause(settings.burst_timer)
    # time.sleep(settings.burst_timer)

    return


def cortical_heatmap(IPU_input, cortical_areas):
    """
    Create a 2D heatmap for the requested Cortical area based on the level of Neuronal activity
    :param cortical_area:
    :return:
    """
    cortical_arrays = []
    cortical_arrays.append(["IPU_Vision", IPU_input])
    for cortical_area in cortical_areas:
        genome = settings.genome
        x1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0]
        x2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1]
        y1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0]
        y2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1]

        # Convert Cortical data to a numpy array
        data = settings.brain[cortical_area]
        cortical_array = np.zeros((x2-x1, y2-y1))
        for key in data:
            xx = data[key]['location'][0]
            yy = data[key]['location'][1]
            cortical_array[xx, yy] = data[key]['cumulative_fire_count']
        cortical_arrays.append([cortical_area, cortical_array])

    # print(cortical_arrays)
    print(cortical_arrays[0][1])

    fig = plt.figure()
    for i in range(1, len(cortical_areas)+2):
        aa = fig.add_subplot(1, len(cortical_areas)+1, i)
        aa.set_title(cortical_arrays[i-1][0])
        aa.imshow(cortical_arrays[i-1][1])

    plt.suptitle('Heatmap of Cortical area Neuronal Fire count', fontsize=12)

    # plt.pause(10)
    plt.show()
    return
