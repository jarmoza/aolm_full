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
def add_lib_paths():
    
    sys.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}objects")
    sys.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}utilities")
    sys.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}data_quality{os.sep}core")
    sys.path.append(f"{ROOT_DIR}{os.sep}aolm_code{os.sep}data_quality{os.sep}core{os.sep}dq_metrics")