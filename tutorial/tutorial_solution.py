# Author: Jonathan Armoza
# Created: December 2, 2025
# Purpose: Contains the solution to the tutorial found in aolm_tutorial.py

# NOTE: Tutorial with instructions can be found in the "main" function at the bottom of this script file

# Imports

# Built-ins
from datetime import datetime
import os
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom

# Tutorial convenience functions
from cli_lib import (
    output_metric_tallies,
    output_metric_values,
    read_huckfinn_dataset_files_by_source,
    read_metadata_files_by_source
)

# Digital edition source IDs (subfolder names in the 'data' folder)
from cli_lib import (
    SOURCE_ID_IA,
    SOURCE_ID_MTPO,
    SOURCE_ID_PG
)

# Data quality metric objects
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords
from dq_metrics.dataset_consistency.consistency_recordconsensus import DatasetConsistency_RecordConsensus
from dq_metrics.dataset_signature.authorial_signature import DatasetSignature_AuthorialSignature
from dq_metrics.dataset_signature.legomena import DatasetSignature_Legomena
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity, read_coha

# Tutorial script can use the 'Art of Literary Modeling' CLI tool
from aolm_cli import run_command_line_tool


# Globals

# Tutorial code can use either a small version of the 'Huckleberry Finn' dataset or the full one
# NOTE: To switch to the full dataset, set USE_FULL_DATASET to 'True'
USE_FULL_DATASET = False
DATASET_BYSIZE_SUBDIR = "small_set"
if USE_FULL_DATASET:
    DATASET_BYSIZE_SUBDIR = "full_set"

# Pre-defined values for tutorial paths/IDs - for convenience
TUTORIAL_DIRECTORY = f"{ROOT_DIR}{os.sep}tutorial{os.sep}"
TUTORIAL_DATASET_LOCATION = f"{TUTORIAL_DIRECTORY}data{os.sep}{DATASET_BYSIZE_SUBDIR}{os.sep}editions{os.sep}"
TUTORIAL_METADATA_LOCATION = f"{TUTORIAL_DIRECTORY}data{os.sep}{DATASET_BYSIZE_SUBDIR}{os.sep}metadata{os.sep}"
TUTORIAL_OUTPUT_LOCATION = f"{TUTORIAL_DIRECTORY}output{os.sep}"
LEXICON_LOCATION = f"{ROOT_DIR}data{os.sep}lexicon{os.sep}coha{os.sep}lexicon.txt"


# Main script

def tutorial_solution():

    # 0. Runtime saved for output file
    script_run_time = datetime.now().strftime("%d%m%Y_%H%M%S")    

    # =========================================================================
    # =========================================================================
    # Tutorial Solution and Commentary

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

    # A. The location of your JSON dataset and/or metadata file(s) on the drive
    EDITIONS_LOCATION = TUTORIAL_DATASET_LOCATION
    # METADATA_LOCATION = TUTORIAL_METADATA_LOCATION

    # B. String ID variable definition
    # NOTE: These string IDs are specific to the 'Art of Literary Modeling' implementation of
    # metrics and used for convenience. They could be optional in your own implementation of a metric.
    TUTORIAL_BASELINE_SOURCE_ID = SOURCE_ID_MTPO # 'mark_twain_project'
    TUTORIAL_SOURCE_ID = SOURCE_ID_IA            # 'internet_archive'
    TUTORIAL_METRIC_ID = f"HuckFinn_{TUTORIAL_BASELINE_SOURCE_ID}v{TUTORIAL_SOURCE_ID}_RecCountsToControlRecs"
    TUTORIAL_COLLECTION_TITLE = "Internet Archive"
    TUTORIAL_WORK_TITLE = "Adventures of Huckleberry Finn"


    # =========================================================================
    # 2. Read editions and/or metadata into reader objects, depending on what inputs your metric needs

    print("Reading editions...")

    # A. Read compared editions and baseline edition and producer reader objects for each
    # NOTE: Source ID corresponds to the folder name in the data directory, in this case
    edition_readers = read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_SOURCE_ID)
    edition_readers.update(read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_BASELINE_SOURCE_ID))
    
    # B. Read metadata for a particular collection of editions (not for this tutorial)
    # metadata = read_metadata_files_by_source(METADATA_LOCATION, TUTORIAL_SOURCE_ID)


    # =========================================================================
    # 3. Run a data quality metric over the editions and/or metadata
    # NOTE: In this case, the choice is to run the 'record counts to control records' metric,
    # comparing editions of 'Adventures of Huckleberry Finn' from the 'Internet Archive'
    # against an edition of the book from 'Mark Twain Project Online' as a baseline

    print("Creating the 'record counts to control' metric...")

    # A. Create the metric object by calling its constructor
    metric = DatasetCompleteness_RecordCountsToControlRecords(
        # A unique string ID for the metric instance
        TUTORIAL_METRIC_ID,
        # Dictionary of reader objects for the compared editions and the baseline edition
        edition_readers,
        # A unique string ID for the digital source of the compared editions
        TUTORIAL_SOURCE_ID, 
        # Full name of the work whose editions are being compared ('Adventures of Huckleberry Finn' in this case)
        TUTORIAL_WORK_TITLE,
        # Full name of the digital source of the compared editions
        TUTORIAL_COLLECTION_TITLE,
        # Folder path to the compared editions' JSON files
        EDITIONS_LOCATION,
        # A unique string ID for the digital source of the baseline edition
        # This is used as a key in the edition_readers dict for the reader object of the baseline edition
        TUTORIAL_BASELINE_SOURCE_ID
    )

    # B. Tally record counts on the editions being compared and the baseline edition
    print("Computing metric tallies...")
    metric.compute()

    # C. Evaluate tallies by calculating statistics about them
    # This produces the metric and submetric values
    print("Evaluating metric tallies...")
    metric.evaluate()


    # =========================================================================
    # 4. Output results for further inspection, analysis, and visualization
    # NOTE: Output has yet to be standardized across AoLM metric and assessment implementations
    # For this reason, the 'output_metric_tallies' and 'output_metric_values' functions
    # have been provided for tutorial users

    # A. Output tallies for editions and baseline edition to a CSV file
    print("Outputting the metric tallies csv...")
    tally_output_filepath = f"{TUTORIAL_OUTPUT_LOCATION}{metric.s_metric_name}_metric_tallies_{script_run_time}.csv" 
    output_metric_tallies(metric, tally_output_filepath)

    # B. Output metric and submetric values (calculated during 'evaluate' call) to a JSON file
    print("Outputting the metric values json...")
    evaluation_output_filepath = f"{TUTORIAL_OUTPUT_LOCATION}{metric.s_metric_name}_metric_values_{script_run_time}.json"
    output_metric_values(metric, evaluation_output_filepath)


def main():

    # 0. Run command line tool if command line arguments given to script
    if len(sys.argv) > 1:
        run_command_line_tool()
        return
    
    # 1. Otherwise, run tutorial solution
    tutorial_solution()


if "__main__" == __name__:
    main()



