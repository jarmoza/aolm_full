# Author: Jonathan Armoza
# Created: December 2, 2025
# Purpose: A brief guide showing to how to use the data quality metrics of 'Art of Literary Modeling'

# NOTE: Tutorial code can be placed in the 'tutorial_workspace' function near the bottom of this script file

# Imports

# Built-ins
import os
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom

# Tutorial convenience functions
from tutorial_lib import (
    output_metric_tallies,
    output_metric_values,
    read_huckfinn_dataset_files_by_source,
    read_metadata_files_by_source
)

# Digital edition source IDs (subfolder names in the 'data' folder)
from tutorial_lib import (
    SOURCE_ID_IA,
    SOURCE_ID_MTPO,
    SOURCE_ID_PG
)

# Data quality metrics
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords
from dq_metrics.dataset_consistency.consistency_recordconsensus import DatasetConsistency_RecordConsensus
from dq_metrics.dataset_signature.authorial_signature import DatasetSignature_AuthorialSignature
from dq_metrics.dataset_signature.legomena import DatasetSignature_Legomena
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity

# Tutorial script can use the 'Art of Literary Modeling' CLI tool
from aolm_cli import run_command_line_tool


# Globals

# Pre-defined values for tutorial paths/IDs - for convenience
TUTORIAL_DIRECTORY = f"{ROOT_DIR}{os.sep}tutorial{os.sep}"
TUTORIAL_DATASET_LOCATION = f"{TUTORIAL_DIRECTORY}data{os.sep}editions{os.sep}"
TUTORIAL_METADATA_LOCATION = f"{TUTORIAL_DIRECTORY}data{os.sep}metadata{os.sep}"
TUTORIAL_OUTPUT_LOCATION = f"{TUTORIAL_DIRECTORY}output{os.sep}"
LEXICON_LOCATION = f"{ROOT_DIR}data{os.sep}lexicon{os.sep}coha{os.sep}lexicon.txt"


# Main script

def tutorial_workspace():

    # =========================================================================
    # =========================================================================
    # Tutorial Instructions and Pseudocode

    # =========================================================================
    # 0. Environment setup
    
    # A. Make sure you have 'conda' installed (see README.md for OS-specific instructions)
    
    # B. Install the 'conda' environment for the tutorial by running the command
    # below in the aolm_full root folder
    # > conda env create -f environment.yml

    # C. Before running this script, activate the 'conda' environment by running the command
    # > conda activate aolm


    # =========================================================================
    # 1. Parameters for the data quality metric (optional)

    # A. The locations of your JSON dataset and/or metadata file(s) on your hard drive

    # B. String ID variable definition


    # =========================================================================
    # 2. Read editions and/or metadata into reader objects, depending on what inputs your metric needs

    # A. Read compared editions and baseline edition

    # B. Read metadata (not for this tutorial, but this is where you would do it)


    # =========================================================================
    # 3. Run a data quality metric over the editions and/or metadata
    # NOTE: In this case, the choice is to run the 'record counts to control records' metric,
    # comparing editions of 'Adventures of Huckleberry Finn' from the 'Internet Archive'
    # against an edition of the book from 'Mark Twain Project Online' as a baseline    

    # A. Create an instance of the 'record counts to control' metric

    # B. Run the metric's 'compute'

    # C. Run the metric's 'evaluate'


    # =========================================================================
    # 4. Output results for further inspection, analysis, and visualization
    
    # A. Output the metric tallies
    
    # B. Output the metric values

    pass


def main():

    # 0. Run command line tool if command line arguments given to script
    if len(sys.argv) > 1:
        run_command_line_tool()
        return
    
    # 1. Otherwise, run tutorial code
    tutorial_workspace()


if "__main__" == __name__:
    main()



