# Author: Jonathan Armoza
# Created: July 7, 2025
# Purpose: Measure the data quality of Melville's works in terms of hapax legomenon

# Imports

# Built-ins

import glob
import os
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom

import aolm_data_reading
from aolm_utilities import bar_plot
from dq_metrics.dataset_signature.hapax_legomenon import DatasetSignature_HapaxLegomenon

