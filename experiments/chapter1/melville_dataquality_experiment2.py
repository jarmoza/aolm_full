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
from pg_melville_reader import PGMelvilleReader
from dq_metrics.dataset_signature.hapax_legomenon import DatasetSignature_HapaxLegomenon

# Main script

def main():

    # 0. Setup
    source_path = aolm_data_reading.melville_source_directory["collected"] + f"demarcated{os.sep}"
    demarcated_files = [filepath for filepath in glob.glob(source_path + "*.json")]

    # Read each Melville novel into memory
    readers = [PGMelvilleReader(filepath) for filepath in demarcated_files]

    # Measure hapax by work and by chapter
    dq_metric = DatasetSignature_HapaxLegomenon(readers)
    dq_metric.compute()
    dq_metric.evaluate()

    # Produce comparison visualization
    if True:
        return


if "__main__" == __name__:
    main()

