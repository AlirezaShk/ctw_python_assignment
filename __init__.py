"""In order to avoid sticky stituations, this file adds current directory to path.

    It also holds the application name and version.
"""
import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# adding the current directory to
# the sys.path.
sys.path.append(current)

__proj_name__ = "ctw_project"
__version__ = "0.1.0"
