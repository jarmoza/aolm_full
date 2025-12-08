# Author: Jonathan Armoza
# Created: December 5, 2025
# Purpose: Contains the solution to the tutorial found in aolm_tutorial.py

# NOTE: Tutorial with instructions can be found in the "main" function at the bottom of this script file

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

# Tutorial values and helper functions
from tutorial_lib import (
    output_metric_values,
    output_metric_tallies,
    parse_args,
    read_huckfinn_dataset_files_by_source,
    read_metadata_files_by_subfolder
)
from tutorial_lib import (
    METRIC_FLAG_AUTHORIAL_SIGNATURE,
    METRIC_FLAG_CONSISTENCY_RECORDCONSENSUS,
    METRIC_FLAG_LEGOMENA,
    METRIC_FLAG_METADATA_SUFFICIENCY,
    METRIC_FLAG_RECORDCOUNT_TO_CONTROLRECORD,
    METRIC_FLAG_LEXICAL_VALIDITY
)
from tutorial_lib import (
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
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity


# Globals

TUTORIAL_DIRECTORY = ROOT_DIR[0:ROOT_DIR.rfind(os.sep)]
TUTORIAL_DATASET_LOCATION = f"{TUTORIAL_DIRECTORY}data{os.sep}editions{os.sep}"
TUTORIAL_METADATA_LOCATION = f"{TUTORIAL_DIRECTORY}data{os.sep}metadata{os.sep}"
TUTORIAL_OUTPUT_LOCATION = f"{TUTORIAL_DIRECTORY}output{os.sep}"


# Main script

def tutorial_solution():

    # =========================================================================
    # 0. Environment setup
    
    # A. Make sure you have 'conda' installed (see README.md for OS-specific instructions)
    
    # B. Install the 'conda' environment for the tutorial by running the command
    # below in the aolm_full root folder
    # > conda env create -f environment.yml

    # C. Activate the 'conda' environment by running the command
    # > conda activate aolm

    # =========================================================================
    # 1. Parameters for the data quality metric

    # A. The location of your JSON dataset and metadata file(s) on the drive
    EDITIONS_LOCATION = TUTORIAL_DATASET_LOCATION
    # METADATA_LOCATION = TUTORIAL_METADATA_LOCATION

    # B. Collection IDs
    # (NOTE: These string IDs are specific to the AoLM implementation of
    # metrics and would be optional otherwise)
    TUTORIAL_BASELINE_SOURCE_ID = SOURCE_ID_MTPO # 'mark_twain_project'
    TUTORIAL_SOURCE_ID = SOURCE_ID_IA            # 'internet_archive'
    TUTORIAL_METRIC_ID = f"HuckFinn_{TUTORIAL_BASELINE_SOURCE_ID}v{TUTORIAL_SOURCE_ID}_RecCountsToControlRecs"
    TUTORIAL_COLLECTION_TITLE = "Internet Archive"
    TUTORIAL_WORK_TITLE = "Adventures of Huckleberry Finn"

    # =========================================================================
    # 2. Read editions and/or metadata into reader objects, depending on what inputs your metric needs

    edition_readers = read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, [TUTORIAL_SOURCE_ID, TUTORIAL_BASELINE_SOURCE_ID])
    # metadata = read_metadata_files_by_subfolder(METADATA_LOCATION)

    # =========================================================================
    # 3. Run a data quality metric over the editions and/or metadata
    # NOTE: In this case, the choice is to run the 'record counts to control records' metric,
    # comparing editions of 'Adventures of Huckleberry Finn' from the 'Internet Archive'
    # against an edition of the book from 'Mark Twain Project Online' as a baseline

    # A. Create the metric object by calling its constructor
    metric = DatasetCompleteness_RecordCountsToControlRecords(
        # Desired string ID for the metric
        TUTORIAL_METRIC_ID,
        # Dictionary of reader objects that have read all digital editions in the dataset folder,
        # keyed on short ID names for each digital source
        edition_readers,
        # Key used in the edition_readers dict for the reader objects of each edition from that digital source
        TUTORIAL_SOURCE_ID, 
        # Full name of the work whose editions are being compared ('Adventures of Huckleberry Finn' in this case)
        TUTORIAL_WORK_TITLE,
        # Full name of the digital source of the editions
        TUTORIAL_COLLECTION_TITLE,
        # Folder path to the edition JSON files
        EDITIONS_LOCATION,
        # Key used in the edition_readers dict for the reader object of the baseline edition
        TUTORIAL_BASELINE_SOURCE_ID
    )

    # B. Tally record counts on the editions being compared and the baseline edition
    metric.compute()

    # C. Evaluate tallies by calculating statistics about them
    metric.evaluate()

    # =========================================================================
    # 4. Output results to CSV for further inspection, analysis, and visualization
    # NOTE: Output has yet to be standardized across AoLM metric and assessment implementations
    # For this reason, the 'output_metric_tallies' and 'output_metric_values' functions
    # have been provided for tutorial users

    # A. Output tallies for editions and baseline edition to a CSV file
    tally_output_filepath = f"{TUTORIAL_OUTPUT_LOCATION}metric_tallies.csv" 
    output_metric_tallies(metric, tally_output_filepath)

    # B. Output metric and submetric values (calculated during 'evaluate' call) to a JSON file
    evaluation_output_filepath = f"{TUTORIAL_OUTPUT_LOCATION}metric_values.json" 
    output_metric_values(metric, evaluation_output_filepath)


def run_command_line_tool():
    
    # 0. Retrieve command line arguments and check they are valid
    args, validation_error = parse_args()
    if validation_error:
        print(validation_error)
        return
    
    # =========================================================================
    # 1. Set the location of JSON dataset file(s) on the drive   

    EDITIONS_LOCATION = args.input_folder if args.input_folder else TUTORIAL_DATASET_LOCATION
    METADATA_LOCATION = args.metadata_folder if args.metadata_folder else TUTORIAL_METADATA_LOCATION

    # 2. Read editions and metadata into reader objects
    edition_readers = read_json_files_by_subfolder(EDITIONS_LOCATION)
    metadata = read_json_files_by_subfolder(METADATA_LOCATION)

    # 3. Run data quality metrics over the editions and/or metadata
    metric_list = {}
    for metric_flag in args.metrics:
        if METRIC_FLAG_METADATA_SUFFICIENCY == metric_flag:
            metric_list[metric_flag] = DatasetCompleteness_MetadataSufficiency(
                f"HuckFinn_{TUTORIAL_SOURCE_ID}_MetadataSufficiency",
                metadata,
                TUTORIAL_SOURCE_ID,
                TUTORIAL_WORK_TITLE,
                TUTORIAL_COLLECTION_TITLE,
                METADATA_LOCATION
            )
            # p_name, p_input, p_source_id, p_work_title, p_collection_title, p_metadata_directory
        elif METRIC_RECORDCOUNTS_TO_CONTROLRECORDS == metric_flag:

            metric_list[metric_flag] = DatasetCompleteness_RecordCountsToControlRecords(
                f"HuckFinn_MTPOv{TUTORIAL_SOURCE_ID}_TextRecordCounts",
                edition_readers,
                TUTORIAL_SOURCE_ID,
                TUTORIAL_WORK_TITLE,
                TUTORIAL_COLLECTION_TITLE,
                EDITIONS_LOCATION,
                TUTORIAL_BASELINE_SOURCE_ID)
        elif DatasetConsistency_RecordConsensus == metric_flag:

            metric_list[metric_flag] = DatasetConsistency_RecordConsensus(
                f"HuckFinn_PG_IA_MTPO_Consistency_RecordConsensus",
                { reader_name: huckfinn_textdata[id][reader_name] for id in huckfinn_textdata for reader_name in huckfinn_textdata[id] },
                "PG_IA_MTPO",
                WORK_TITLE,
                "_".join([aolm_data_reading.huckfinn_source_fullnames[id] for id in COLLECTION_IDS]),
                EDITION_PATHS
            )

            # Consensus
            # p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath

    # Metadata Sufficiency
    huckfinn_metadata_sufficiency =     


# Main script

def main():

    # 0. Run command line tool if command line arguments given to script
    if len(sys.argv) > 1:
        run_command_line_tool()
        return

    tutorial_solution()


if "__main__" == __name__:
    main(sys.argv)



