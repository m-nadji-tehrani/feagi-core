
"""
This file contains all of the Visualization functions
"""
import universal_functions

if universal_functions.parameters["Switches"]["vis_show"]:
    import matplotlib as mpl
    mpl.use('TkAgg')
    import matplotlib.pylab as pylab
    import matplotlib.animation as animation
    import architect
    from misc import neuron_functions, universal_functions


def connectome_visualizer(cortical_area, neighbor_show='false', threshold=0):
    """Visualizes the Neurons in the connectome"""
    if not universal_functions.parameters["Switches"]["vis_init_status"]:
        universal_functions.vis_init()
    neuron_locations = architect.connectome_location_data(cortical_area)

    universal_functions.ax.set_xlim(
        universal_functions.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0],
        universal_functions.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1])
    universal_functions.ax.set_ylim(
        universal_functions.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0],
        universal_functions.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1])
    universal_functions.ax.set_zlim(
        universal_functions.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][0],
        universal_functions.genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["z"][1])

    for location in neuron_locations:
        universal_functions.ax.scatter(location[0], location[1], location[2], c='b', marker='.')

    # Displays the Axon-Dendrite connections when True is set
    if neighbor_show == 'true':
        data = universal_functions.brain[cortical_area]

        # The following code scans thru connectome and extract locations for source and destination neurons
        for key in data:
            if data[key]["neighbors"].keys():
                source_location = data[key]["location"]
                for subkey in data[key]["neighbors"]:
                    if (data[key]['neighbors'][subkey]['cortical_area'] == cortical_area) and (data[key]['neighbors']
                                [subkey]['postsynaptic_current'] > threshold):
                        destination_location = data[subkey]["location"]
                        a = universal_functions.Arrow3D([source_location[0], destination_location[0]], [source_location[1],
                                                                                                        destination_location[1]], [source_location[2], destination_location[2]],
                                                        mutation_scale=10, lw=1, arrowstyle="->", color="r")
                        universal_functions.ax.add_artist(a)
    universal_functions.plt.show()
    universal_functions.plt.pause(universal_functions.parameters["Timers"]["burst_timer"])
    return


def burst_visualization_manager():
    # global figure
    # figure = pylab.figure(figsize=pylab.figaspect(.15))
    #
    # pylab.thismanager = pylab.get_current_fig_manager()
    # pylab.thismanager.window.wm_geometry("+80+800")

    setup_canvas()

    ani = animation.FuncAnimation(universal_functions.fig, animate, interval=1000)

    universal_functions.ax.figure.canvas.draw()
    pylab.plt.show()


def setup_canvas():
    index = 0
    global indexed_cortical_list, d_vision, d_ipu, d_memory, d_opu

    indexed_cortical_list = []
    for key in universal_functions.cortical_areas:
        indexed_cortical_list.append([index, key])
        index += 1

    for entry in indexed_cortical_list:
        if universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'vision':
            if universal_functions.genome['blueprint'][entry[1]]['sub_group_id'] == 'vision_v1':
                d_vision = universal_functions.vision_figure.add_subplot(7, 3, universal_functions.genome['blueprint']
                [entry[1]]['plot_index'], projection='3d', aspect='equal')
                d_vision.set_title(entry[1])
                d_vision.set_xlim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
                d_vision.set_ylim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
                d_vision.set_zlim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
                d_vision.set_xlabel('X Label')
                d_vision.set_ylabel('Y Label')
                d_vision.set_zlabel('Z Label')

            elif universal_functions.genome['blueprint'][entry[1]]['sub_group_id'] == 'vision_v2':
                d_vision = universal_functions.vision_figure.add_subplot(7, 3, universal_functions.genome['blueprint']
                [entry[1]]['plot_index'], projection='3d', aspect='equal')
                d_vision.set_title(entry[1])
                d_vision.set_xlim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
                d_vision.set_ylim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
                d_vision.set_zlim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
                d_vision.set_xlabel('X Label')
                d_vision.set_ylabel('Y Label')
                d_vision.set_zlabel('Z Label')
            elif universal_functions.genome['blueprint'][entry[1]]['sub_group_id'] == 'vision_IT':
                d_vision = universal_functions.vision_figure.add_subplot(7, 3, universal_functions.genome['blueprint']
                [entry[1]]['plot_index'], projection='3d', aspect='equal')
                d_vision.set_title(entry[1])
                d_vision.set_xlim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
                d_vision.set_ylim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
                d_vision.set_zlim(
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                    universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
                d_vision.set_xlabel('X Label')
                d_vision.set_ylabel('Y Label')
                d_vision.set_zlabel('Z Label')

        elif universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'Memory':
            d_memory = universal_functions.memory_figure.add_subplot(2, 1, universal_functions.genome['blueprint']
            [entry[1]]['plot_index'], projection='3d')
            d_memory.set_title(entry[1])
            d_memory.set_xlim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
            d_memory.set_ylim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
            d_memory.set_zlim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
            d_memory.set_xlabel('X Label')
            d_memory.set_ylabel('Y Label')
            d_memory.set_zlabel('Z Label')

        elif universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'IPU':
            d_ipu = universal_functions.input_figure.add_subplot(1, 1, universal_functions.genome['blueprint']
            [entry[1]]['plot_index'], projection='3d')
            d_ipu.set_title(entry[1])
            d_ipu.set_xlim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
            d_ipu.set_ylim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
            d_ipu.set_zlim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
            d_ipu.set_xlabel('X Label')
            d_ipu.set_ylabel('Y Label')
            d_ipu.set_zlabel('Z Label')

        elif universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'OPU':
            d_opu = universal_functions.output_figure.add_subplot(1, 1, universal_functions.genome['blueprint']
            [entry[1]]['plot_index'], projection='3d')
            d_opu.set_title(entry[1])
            d_opu.set_xlim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["x"][1])
            d_opu.set_ylim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["y"][1])
            d_opu.set_zlim(
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][0],
                universal_functions.genome['blueprint'][entry[1]]["neuron_params"]["geometric_boundaries"]["z"][1])
            d_opu.set_xlabel('X Label')
            d_opu.set_ylabel('Y Label')
            d_opu.set_zlabel('Z Label')

            # universal_functions.ax.figure.canvas.draw()
            # pylab.plt.show()


def burst_iterator():
    for burst_data in universal_functions.fcl_burst_data_set:
        yield universal_functions.fcl_burst_data_set[burst_data]


def animate(i):
    if i == 0:
        fcl = next(burst_iterator())
    else:
        counter = i + 1
        fcl = burst_iterator().send(counter)
    print("<> ^V^V^V^V^ <>", fcl)
    if len(fcl) > 0:
        for entry in indexed_cortical_list:
            neuron_locations = neuron_functions.fire_candidate_locations(fcl)
            for location in neuron_locations[entry[1]]:
                if universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'vision':
                    d_vision.scatter(location[0], location[1], location[2], c='r', marker='^')
                if universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'Memory':
                    d_memory.scatter(location[0], location[1], location[2], c='r', marker='^')
                if universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'IPU':
                    d_ipu.scatter(location[0], location[1], location[2], c='r', marker='^')
                if universal_functions.genome['blueprint'][entry[1]]['group_id'] == 'OPU':
                    d_opu.scatter(location[0], location[1], location[2], c='r', marker='^')

    else:
        print("Need a sleep func here...")

    d_vision.clear()



def cortical_activity_visualizer(cortical_areas, x=30, y=30, z=30):
    """Visualizes the extent of Neuron activities"""
    if not universal_functions.parameters["Switches"]["vis_init_status"]:
        universal_functions.vis_init()

    # fig = universal_functions.plt.figure()
    fig = universal_functions.plt.figure(figsize=universal_functions.plt.figaspect(.2))
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
    universal_functions.plt.show()
    universal_functions.plt.pause(1)
    return


def mnist_img_show(IPU_input):
    """ Displays the image from MNIST database"""

    aa = universal_functions.input_figure.add_subplot(2, 1, 2)
    aa.set_title("User selection from MNIST")
    aa.imshow(IPU_input)

    # universal_functions.plt.suptitle('Heatmap of Cortical area Neuronal Fire count', fontsize=12)

    # plt.pause(10)
    # universal_functions.plt.show()
    universal_functions.plt.draw()
    universal_functions.plt.pause(universal_functions.parameters["Timers"]["burst_timer"])
    return


def cortical_heatmap(IPU_input, cortical_areas):
    """
    Create a 2D heatmap for the requested Cortical area based on the level of Neuronal activity
    :param cortical_area:
    :return:
    """
    # if not settings.Switches.vis_init_status:
    #     settings.vis_init()
    universal_functions.plt.ion()

    cortical_arrays = []
    cortical_arrays.append(["IPU_Vision", IPU_input])
    # for cortical_area in cortical_areas:
    #     genome = universal_functions.genome
    #     x1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][0]
    #     x2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["x"][1]
    #     y1 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][0]
    #     y2 = genome['blueprint'][cortical_area]["neuron_params"]["geometric_boundaries"]["y"][1]
    #
    #     # Convert Cortical data to a numpy array
    #     data = universal_functions.brain[cortical_area]
    #     cortical_array = np.zeros((x2-x1, y2-y1))
    #     for key in data:
    #         xx = data[key]['location'][0]
    #         yy = data[key]['location'][1]
    #         cortical_array[xx, yy] = data[key]['cumulative_fire_count_inst']
    #     cortical_arrays.append([cortical_area, cortical_array])

    # print(cortical_arrays)
    # print(cortical_arrays[0][1])

    fig2 = universal_functions.plt.figure(num=None, figsize=(8, 8), dpi=28, facecolor='w', edgecolor='k')

    mpl.pylab.thismanager = mpl.pylab.get_current_fig_manager()
    mpl.pylab.thismanager.window.wm_geometry("+20+300")

    for i in range(1, len(cortical_areas)+2):
        aa = fig2.add_subplot(1, len(cortical_areas)+1, i)
        aa.set_title(cortical_arrays[i-1][0])
        aa.imshow(cortical_arrays[i-1][1])

    universal_functions.plt.suptitle('Heatmap of Cortical area Neuronal Fire count', fontsize=12)

    # plt.pause(10)
    universal_functions.plt.show()
    return
