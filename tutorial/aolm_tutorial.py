# Author: Jonathan Armoza
# Created: December 2, 2025
# Purpose: A brief guide showing to how to use the data quality metrics of 'Art of Literary Modeling'

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

# Tutorial values and functions
from tutorial_lib import parse_args, read_json_files_by_subfolder
from tutorial_lib import (
    METRIC_FLAG_AUTHORIAL_SIGNATURE,
    METRIC_FLAG_CONSISTENCY_RECORDCONSENSUS,
    METRIC_FLAG_LEGOMENA,
    METRIC_FLAG_METADATA_SUFFICIENCY,
    METRIC_FLAG_RECORDCOUNT_TO_CONTROLRECORD,
    METRIC_FLAG_LEXICAL_VALIDITY
)

# Data quality metrics
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords
from dq_metrics.dataset_consistency.consistency_recordconsensus import DatasetConsistency_RecordConsensus
from dq_metrics.dataset_signature.authorial_signature import DatasetSignature_AuthorialSignature
from dq_metrics.dataset_signature.legomena import DatasetSignature_Legomena
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity


# Globals

TUTORIAL_DIRECTORY = ROOT_DIR[0:ROOT_DIR.rfind(os.sep)]
TUTORIAL_SOURCE_ID = "IA"
TUTORIAL_BASELINE_SOURCE_ID = "MTPO"
TUTORIAL_COLLECTION_TITLE = "Internet Archive"
TUTORIAL_WORK_TITLE = "Adventures of Huckleberry Finn"

# Metric flags
# NOTE: Setting to 'True' will run the metric; setting to 'False' will not

METRIC_AUTHORIAL_SIGNATURE = True
METRIC_CONSISTENCY_RECORD_CONSENSUS = True
METRIC_LEGOMENA = True
METRIC_LEXICAL_VALIDITY = True
METRIC_METADATA_SUFFICIENCY = True
METRIC_RECORDCOUNTS_TO_CONTROLRECORDS = True


# Main script

def main():

    # 0. Handle command line arguments

    # Retrieve command line arguments and check they are valid
    args, validation_error = parse_args()
    if validation_error:
        print(validation_error)
        return

    # Tutorial Instructions

    # =========================================================================
    # 0. Environment setup
    
    # A. Make sure you have 'conda' installed (see README.md for OS-specific instructions)
    
    # B. Install the 'conda' environment for the tutorial by running the command
    # below in the aolm_full root folder
    # > conda env create -f environment.yml

    # C. Activate the 'conda' environment by running the command
    # > conda activate aolm

    # =========================================================================
    # 1. Set the location of your JSON dataset file(s) on the drive
    # (a 'TUTORIAL_DIRECTORY' global variable exists for convenience)

    # ex. DATASET_LOCATION = f"{TUTORIAL_DIRECTORY}{os.sep}data{os.sep}"
    EDITIONS_LOCATION = args.input_folder
    METADATA_LOCATION = args.metadata_folder

    # 2. Read editions and metadata into reader objects
    edition_readers = read_json_files_by_subfolder(EDITIONS_LOCATION)
    metadata = read_json_files_by_subfolder(METADATA_LOCATION)


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
        EDITION_PATHS)

            # Consensus
            # p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath

    # Metadata Sufficiency
    huckfinn_metadata_sufficiency = 


    pass

if "__main__" == __name__:
    main(sys.argv)



