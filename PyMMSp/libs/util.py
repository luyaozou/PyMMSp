#! encoding = utf-8

""" Utility functions for file handling """

import importlib.resources as pkg_resources
import os


def abs_path(pkg, resource):
    """ Get absolute path of a resource file in a package
    :argument
        pkg: str        package name
        resource: str   resource file name
    :return
        str             absolute path of the resource file
    """
    with pkg_resources.path(pkg, resource) as f:
        abs_path = str(f)
    return abs_path
