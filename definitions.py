# Author: Jonathan Armoza
# Created: January 12, 2025
# Purpose: Contains variables accessible throughout project

# Imports

# Built-ins
import os
import sys


# Globals

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Import Paths
def add_lib_paths(p_sys_object):
    
    p_sys_object.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}objects")
    p_sys_object.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}utilities")
    p_sys_object.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}data_quality{os.sep}core")
    p_sys_object.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}data_quality{os.sep}core{os.sep}dq_metrics")