# -*- coding: utf-8 -*-
"""
Demonstrates use of GLScatterPlotItem with rapidly-updating plots.

"""

## Add path to library (just for examples; you do not need this)
# import initExample

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
w.show()
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')

g = gl.GLGridItem()
w.addItem(g)

phase = 0.

pos3 = np.zeros((100, 100, 3))
pos3[:, :, :2] = np.mgrid[:100, :100].transpose(1, 2, 0) * [-0.1, 0.1]
pos3 = pos3.reshape(10000, 3)
d3 = (pos3 ** 2).sum(axis=1) ** 0.5

sp3 = gl.GLScatterPlotItem(pos=pos3, color=(1, 1, 1, .3), size=0.1, pxMode=False)

w.addItem(sp3)

def update():

    global phase, sp2, d2

    phase -= 0.1

    ## update surface positions and colors
    global sp3, d3, pos3
    z = -np.cos(d3 * 2 + phase)
    pos3[:, 2] = z
    color = np.empty((len(d3), 4), dtype=np.float32)
    color[:, 3] = 0.3
    color[:, 0] = np.clip(z * 3.0, 0, 1)
    color[:, 1] = np.clip(z * 1.0, 0, 1)
    color[:, 2] = np.clip(z ** 3, 0, 1)
    sp3.setData(pos=pos3, color=color)

t = QtCore.QTimer()
t.timeout.connect(update)
t.start(1)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()