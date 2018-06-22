
"""
This file contains all of the Visualization functions
"""

import os.path
os.chdir("/Users/mntehrani/Documents/PycharmProjects/Metis/")

from time import sleep
import json

import matplotlib as mpl
mpl.use('TkAgg')

import matplotlib.pylab as pylab
import matplotlib.animation as animation
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
from matplotlib import style

# style.use('dark_background')

from architect import connectome_location_data
from misc.neuron_functions import fire_candidate_locations
from misc.universal_functions import brain, genome, parameters, cortical_areas, latest_fcl_file, load_fcl_in_memory


# if parameters["Switches"]["visualize_latest_file"]:
#     fcl_file = latest_fcl_file()
# else:
#     fcl_file = parameters["InitData"]["fcl_to_visualize"]
#
# fcl_burst_data_set = load_fcl_in_memory(fcl_file)


def vis_init():
    # plt.ion()
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

        # plt.ion()
        global fig
        fig = pylab.plt.figure()
        global ax
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 30)
        ax.set_zlim(0, 30)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        fig.suptitle("Main plot")

    parameters["Switches"]["vis_init_status"] = True


def init_burst_visualization():
    # global burst_figure
    # burst_figure = plt.figure(figsize=plt.figaspect(.15))
    # plt.thismanager = plt.get_current_fig_manager()
    # plt.thismanager.window.wm_geometry("+80+800")

    global input_figure
    input_figure = pylab.plt.figure(figsize=(2, 3))
    pylab.plt.thismanager = pylab.plt.get_current_fig_manager()
    pylab.plt.thismanager.window.wm_geometry("+20+600")
    pylab.plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    global vision_figure
    vision_figure = pylab.plt.figure(figsize=(6, 10))
    pylab.plt.thismanager = pylab.plt.get_current_fig_manager()
    pylab.plt.thismanager.window.wm_geometry("+300+20")
    pylab.plt.subplots_adjust(left=0, bottom=0, right=1, top=.98, wspace=0.2, hspace=0)

    global memory_figure
    memory_figure = pylab.plt.figure(figsize=(2, 6))
    pylab.plt.thismanager = pylab.plt.get_current_fig_manager()
    pylab.plt.thismanager.window.wm_geometry("+920+300")
    pylab.plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    global output_figure
    output_figure = pylab.plt.figure(figsize=(2, 3))
    pylab.plt.thismanager = pylab.plt.get_current_fig_manager()
    pylab.plt.thismanager.window.wm_geometry("+1200+600")
    pylab.plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


def connectome_visualizer(cortical_area, neighbor_show='false', threshold=0):
    """Visualizes the Neurons in the connectome"""
    if not parameters["Switches"]["vis_init_status"]:
        vis_init()
    neuron_locations = connectome_location_data(cortical_area)

    ax.set_xlim(
        genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0],
        genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1])
    ax.set_ylim(
        genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0],
        genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1])
    ax.set_zlim(
        genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0],
        genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1])

    for location in neuron_locations:
        ax.scatter(location[0], location[1], location[2], c='b', marker='.')

    # Displays the Axon-Dendrite connections when True is set
    if neighbor_show == 'true':
        data = brain[cortical_area]

        # The following code scans thru connectome and extract locations for source and destination neurons
        for key in data:
            if data[key]["neighbors"].keys():
                source_location = data[key]["location"]
                for subkey in data[key]["neighbors"]:
                    if (data[key]['neighbors'][subkey]['cortical_area'] == cortical_area) and (data[key]['neighbors']
                                [subkey]['postsynaptic_current'] > threshold):
                        destination_location = data[subkey]["location"]
                        a = Arrow3D([source_location[0], destination_location[0]],
                                    [source_location[1], destination_location[1]],
                                    [source_location[2], destination_location[2]],
                                    mutation_scale=10, lw=1, arrowstyle="->", color="r")
                        ax.add_artist(a)
    pylab.plt.show()
    pylab.plt.pause(parameters["Timers"]["burst_timer"])
    return


def burst_visualization_manager():
    # global figure
    # figure = pylab.figure(figsize=pylab.figaspect(.15))
    #
    # pylab.thismanager = pylab.get_current_fig_manager()
    # pylab.thismanager.window.wm_geometry("+80+800")

    setup_canvas()

    ani = animation.FuncAnimation(fig, animate, interval=1000)

    ax.figure.canvas.draw()
    pylab.plt.cla()
    # pylab.plt.show()

    # for burst in burst_iterator():
    #     fcl = burst
    #     print("FCL from the mrg func:", fcl)


# def burst_iterator():
#     for burst_data in fcl_burst_data_set:
#         yield fcl_burst_data_set[burst_data]


def animate(i):

    with open('./fcl_repo/fcl.json', 'r') as fcl_file:
        fcl = fcl_file.read()
        # print("*****************************************\n", fcl)
        # print("*****************************************\n")
    # ax.clear()
    print("*****************************************\n", fcl)
    if len(fcl) > 0:
        for entry in indexed_cortical_list:
            try:
                neuron_locations = fire_candidate_locations(fcl)
                print("neuron locations:", neuron_locations)
                for location in neuron_locations[entry[1]]:
                    if genome['blueprint'][entry[1]]['group_id'] == 'vision':
                        d_vision.scatter(location[0], location[1], location[2], c='r', marker='^')
                    if genome['blueprint'][entry[1]]['group_id'] == 'Memory':
                        d_memory.scatter(location[0], location[1], location[2], c='r', marker='^')
                    if genome['blueprint'][entry[1]]['group_id'] == 'IPU':
                        d_ipu.scatter(location[0], location[1], location[2], c='r', marker='^')
                    if genome['blueprint'][entry[1]]['group_id'] == 'OPU':
                        d_opu.scatter(location[0], location[1], location[2], c='r', marker='^')
            finally:
                pass

    else:
        sleep(1)
        # print("haha")


def setup_canvas():
    index = 0
    global indexed_cortical_list, d_vision, d_ipu, d_memory, d_opu

    indexed_cortical_list = []
    for key in cortical_areas:
        indexed_cortical_list.append([index, key])
        index += 1

    for entry in indexed_cortical_list:
        if genome['blueprint'][entry[1]]['group_id'] == 'vision':
            if genome['blueprint'][entry[1]]['sub_group_id'] == 'vision_v1':
                d_vision = vision_figure.add_subplot(7, 3, genome['blueprint']
                [entry[1]]['plot_index'], projection='3d', aspect='equal')
                d_vision.set_title(entry[1])
                d_vision.set_xlim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
                d_vision.set_ylim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
                d_vision.set_zlim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
                d_vision.set_xlabel('X Label')
                d_vision.set_ylabel('Y Label')
                d_vision.set_zlabel('Z Label')

            elif genome['blueprint'][entry[1]]['sub_group_id'] == 'vision_v2':
                d_vision = vision_figure.add_subplot(7, 3, genome['blueprint']
                [entry[1]]['plot_index'], projection='3d', aspect='equal')
                d_vision.set_title(entry[1])
                d_vision.set_xlim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
                d_vision.set_ylim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
                d_vision.set_zlim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
                d_vision.set_xlabel('X Label')
                d_vision.set_ylabel('Y Label')
                d_vision.set_zlabel('Z Label')
            elif genome['blueprint'][entry[1]]['sub_group_id'] == 'vision_IT':
                d_vision = vision_figure.add_subplot(7, 3, genome['blueprint']
                [entry[1]]['plot_index'], projection='3d', aspect='equal')
                d_vision.set_title(entry[1])
                d_vision.set_xlim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
                d_vision.set_ylim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
                d_vision.set_zlim(
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                    genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
                d_vision.set_xlabel('X Label')
                d_vision.set_ylabel('Y Label')
                d_vision.set_zlabel('Z Label')

        elif genome['blueprint'][entry[1]]['group_id'] == 'Memory':
            d_memory = memory_figure.add_subplot(2, 1, genome['blueprint']
            [entry[1]]['plot_index'], projection='3d')
            d_memory.set_title(entry[1])
            d_memory.set_xlim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
            d_memory.set_ylim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
            d_memory.set_zlim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
            d_memory.set_xlabel('X Label')
            d_memory.set_ylabel('Y Label')
            d_memory.set_zlabel('Z Label')

        elif genome['blueprint'][entry[1]]['group_id'] == 'IPU':
            d_ipu = input_figure.add_subplot(1, 1, genome['blueprint']
            [entry[1]]['plot_index'], projection='3d')
            d_ipu.set_title(entry[1])
            d_ipu.set_xlim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
            d_ipu.set_ylim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
            d_ipu.set_zlim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
            d_ipu.set_xlabel('X Label')
            d_ipu.set_ylabel('Y Label')
            d_ipu.set_zlabel('Z Label')

        elif genome['blueprint'][entry[1]]['group_id'] == 'OPU':
            d_opu = output_figure.add_subplot(1, 1, genome['blueprint']
            [entry[1]]['plot_index'], projection='3d')
            d_opu.set_title(entry[1])
            d_opu.set_xlim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
            d_opu.set_ylim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
            d_opu.set_zlim(
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
            d_opu.set_xlabel('X Label')
            d_opu.set_ylabel('Y Label')
            d_opu.set_zlabel('Z Label')

            # ax.figure.canvas.draw()
            # pylab.plt.show()


def cortical_activity_visualizer(cortical_areas, x=30, y=30, z=30):
    """Visualizes the extent of Neuron activities"""
    if not parameters["Switches"]["vis_init_status"]:
        vis_init()

    # fig = pylab.plt.figure()
    fig = pylab.plt.figure(figsize=pylab.plt.figaspect(.2))
    fig.suptitle('Cortical Activities\n')

    for cortical_area in cortical_areas:
        neuron_locations = connectome_location_data(cortical_area)
        aa = fig.add_subplot(1, len(cortical_areas)+1, cortical_areas.index(cortical_area)+1)
        aa.set_title(cortical_area)
        aa.set_xlim(0, x)
        aa.set_ylim(0, y)
        # aa.set_zlim(0, z)
        for location in neuron_locations:
            # aa.scatter(location[0], location[1], location[2], s=location[3])
            aa.scatter(location[0], location[1], s=location[3])
    pylab.plt.show()
    pylab.plt.pause(1)
    return


def mnist_img_show(IPU_input):
    """ Displays the image from MNIST database"""

    aa = input_figure.add_subplot(2, 1, 2)
    aa.set_title("User selection from MNIST")
    aa.imshow(IPU_input)

    # plt.suptitle('Heatmap of Cortical area Neuronal Fire count', fontsize=12)

    # plt.pause(10)
    # plt.show()
    pylab.plt.draw()
    pylab.plt.pause(parameters["Timers"]["burst_timer"])
    return


def cortical_heatmap(IPU_input, cortical_areas):
    """
    Create a 2D heatmap for the requested Cortical area based on the level of Neuronal activity
    :param cortical_area:
    :return:
    """
    # if not settings.Switches.vis_init_status:
    #     settings.vis_init()
    pylab.plt.ion()

    cortical_arrays = []
    cortical_arrays.append(["IPU_Vision", IPU_input])
    # for cortical_area in cortical_areas:
    #     genome = genome
    #     x1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0]
    #     x2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1]
    #     y1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0]
    #     y2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1]
    #
    #     # Convert Cortical data to a numpy array
    #     data = brain[cortical_area]
    #     cortical_array = np.zeros((x2-x1, y2-y1))
    #     for key in data:
    #         xx = data[key]['location'][0]
    #         yy = data[key]['location'][1]
    #         cortical_array[xx, yy] = data[key]['cumulative_fire_count_inst']
    #     cortical_arrays.append([cortical_area, cortical_array])

    # print(cortical_arrays)
    # print(cortical_arrays[0][1])

    fig2 = pylab.plt.figure(num=None, figsize=(8, 8), dpi=28, facecolor='w', edgecolor='k')

    mpl.pylab.thismanager = mpl.pylab.get_current_fig_manager()
    mpl.pylab.thismanager.window.wm_geometry("+20+300")

    for i in range(1, len(cortical_areas)+2):
        aa = fig2.add_subplot(1, len(cortical_areas)+1, i)
        aa.set_title(cortical_arrays[i-1][0])
        aa.imshow(cortical_arrays[i-1][1])

    pylab.plt.suptitle('Heatmap of Cortical area Neuronal Fire count', fontsize=12)

    # plt.pause(10)
    pylab.plt.show()
    return


vis_init()
init_burst_visualization()
burst_visualization_manager()
