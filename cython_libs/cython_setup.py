"""
use the following to build:

python3 cython_setup.py build_ext --inplace
"""

import sys
sys.path.append('/Users/mntehrani/PycharmProjects/Metis/venv/lib/python3.7/site-packages/')

from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("neuron_functions_cy.pyx"))
setup(ext_modules=cythonize("ipu_vision_cy.pyx"))
