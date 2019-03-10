import sys
sys.path.append('/Users/mntehrani/PycharmProjects/Metis/venv/lib/python3.7/site-packages/')

from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("mycython_test.pyx"))