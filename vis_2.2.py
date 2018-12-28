# -*- coding: utf-8 -*-
"""
    Animated 3D sinc function
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys

import os
import json
import time
import random
import numpy as np

import sys
sys.path.append('/Users/mntehrani/Documents/PycharmProjects/Metis/venv/lib/python3.7/site-packages/')


global connectome_file_path

try:
    # connectome_file_path = sys.argv[1]
    connectome_file_path = './connectome_4/'
    if connectome_file_path:
        print("Connectome path is:", connectome_file_path)
except IndexError or NameError:
    print("Error occurred while setting the connectome path")

with open(connectome_file_path + 'genome_tmp.json', "r") as genome_file:
    genome_data = json.load(genome_file)
    genome = genome_data

blueprint = genome["blueprint"]
cortical_list = []
for key in blueprint:
    cortical_list.append(key)

def load_brain():
    global connectome_file_path
    brain = {}
    for item in cortical_list:
        if os.path.isfile(connectome_file_path + item + '.json'):
            with open(connectome_file_path + item + '.json', "r") as data_file:
                data = json.load(data_file)
                brain[item] = data
    return brain


class Visualizer(object):
    def __init__(self):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()

        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        self.pts = np.array([[-1, -1, -1], [5, 5, 5]])

        for i in range(50):
            self.traces[i] = gl.GLScatterPlotItem(pos=self.pts,
                                                  size=np.array([10,30]),
                                                  color=np.array([[0.11,0.7, 1, 1],
                                                                  [0.5, 0.5, 0.5, 0.5]]),
                                                  pxMode=True)
            self.w.addItem(self.traces[i])


    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color, size):
        self.traces[name].setData(pos=points, color=color, size=size)

    def update(self):
        data_points = self.pts.shape[0]
        for i in range(50):
            self.set_plotdata(
                name=i, points=self.pts,
                color=pg.glColor((i, 100)),
                size=3
            )

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(100)
        self.start()

def build_plot_data(cortical_area, threshold):
    plot_data = []
    brain = load_brain()
    data = brain[cortical_area]
    for neuron_id in data:
        if data[neuron_id]["neighbors"].keys():
            source_location = data[neuron_id]["location"]
            for subkey in data[neuron_id]["neighbors"]:
                if (data[neuron_id]['neighbors'][subkey]['cortical_area'] == cortical_area) and (
                        data[neuron_id]['neighbors'][subkey]['postsynaptic_current'] >= threshold):
                    destination_location = data[subkey]["location"]
                    if source_location not in plot_data:
                        plot_data.append(source_location)
                    if destination_location not in plot_data:
                        plot_data.append(destination_location)
    print(">>>-->>>")
    i = 0
    for _ in plot_data:
        print(i,'', _)
        i += 1
    print("<<<--<<<")
    return plot_data



def connectome_visualizer(cortical_area, threshold=0.1):
    """Visualizes the Neurons in the connectome"""

    cortical_file_path = connectome_file_path + cortical_area + '.json'
    latest_modification_date = os.path.getmtime(cortical_file_path)

    # todo: Figure how to determine the delta between previous data-set and new one to solve cumulative plot issue
    plot_data = build_plot_data(cortical_area, threshold)
    print("plot data size=", np.array(plot_data).shape)

    while 1 == 1:
        new_modification_date = os.path.getmtime(cortical_file_path)
        print('---')
        if latest_modification_date != new_modification_date:
            print('+++')
            print(new_modification_date)

            latest_modification_date = new_modification_date
            previous_plot_data = plot_data
            print("previous plot data size=", np.array(previous_plot_data).shape)

            plot_data = build_plot_data(cortical_area, threshold)
            print("plot data size=", np.array(plot_data).shape)

            plot_delta = []
            print("*************************************")

            if plot_data != previous_plot_data:
                for item in plot_data:
                    if item not in previous_plot_data:
                        plot_delta.append(item)
                        print("The following were added:", item)
                    else:
                        print("Item not found.")

                print("plot_delta", plot_delta)
                pos = np.array(plot_delta)
                total_points = np.array(plot_data)
                print(">>>>", pos.shape, total_points.shape)
                if pos != []:
                    # print("POS:\n", pos)
                    v.pts = pos
                    v.animation()
            else:
                print("Plot data has remained unchanged...")

        time.sleep(5)


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = Visualizer()
    # v.animation()

    connectome_visualizer('vision_memory')