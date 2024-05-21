#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='PyMMSp',
      version='1.0.0',
      description='Python MillimeterWave Spectrometer Controller',
      author='Dr. Luyao ZOU',
      author_email='luyao.zou@univ-littoral.fr',
      packages=find_packages('.', exclude=('data.*', 'test.*', 'src.*')),
      entry_points={
        'gui_scripts': [
            'pymmsp = pymmsp.launch:launch',
        ]},
      package_data={'pymmsp': ['resources/*.png', 'resources/*.ico']},
      install_requires=[
            'docutils>=0.3',
            'PyQt6>=6.7.0',
            'pyqtgraph>=0.13.0',
            'numpy>=1.10.1',
            'scipy>=1.2.1',
            'lmfit>=1.0.0',
            'pyvisa>=1.14',
        ],
      python_requires='>=3.8',
      license='MIT',
)
