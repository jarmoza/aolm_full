# Author: Jonathan Armoza
# Created: December 7, 2025
# Purpose: Contains the command line program for 'Art of Literary Modeling'

# Imports

# Built-ins
import argparse
from datetime import datetime
import os
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom

# Tutorial values and helper functions
from cli_lib import (
    output_metric_values,
    output_metric_tallies,
    # TODO: Remove for more generic edition reading function
    read_huckfinn_dataset_files_by_source,
    read_metadata_files_by_source
)
from cli_lib import create_metric

# Flag values and variables
from cli_lib import (
    CLI_FLAG_BASELINE_SOURCE_ID,
    CLI_FLAG_COLLECTION_TITLE,
    CLI_FLAG_INPUT_FOLDER,
    CLI_FLAG_METADATA_FOLDER,
    CLI_FLAG_METRICS,
    CLI_FLAG_SOURCE_ID,
    CLI_FLAG_WORK_TITLE,
    METRIC_FLAG_AUTHORIAL_SIGNATURE,
    METRIC_FLAG_RECORD_CONSENSUS,
    METRIC_FLAG_LEGOMENA,
    METRIC_FLAG_METADATA_SUFFICIENCY,
    METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORDS,
    METRIC_FLAG_LEXICAL_VALIDITY,
    VALID_METRICS
)

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


# Globals

# Pre-defined values for tutorial paths/IDs
CLI_DIRECTORY = ROOT_DIR[0:ROOT_DIR.rfind(os.sep)]
CLI_DATASET_LOCATION = f"{CLI_DIRECTORY}data{os.sep}editions{os.sep}"
CLI_METADATA_LOCATION = f"{CLI_DIRECTORY}data{os.sep}metadata{os.sep}"
CLI_OUTPUT_LOCATION = f"{CLI_DIRECTORY}output{os.sep}"
LEXICON_LOCATION = f"{ROOT_DIR}data{os.sep}lexicon{os.sep}coha{os.sep}lexicon.txt"


# Helper functions

def parse_args():

    # 1. Set up argument parser
    parser = argparse.ArgumentParser(description="Tutorial for 'Art of Literary Modeling'")

    # A. Dataset file folder for metrics (other than metadata sufficiency)
    parser.add_argument(
        CLI_FLAG_INPUT_FOLDER,
        type=str,
        help="Path to folder containing input records"
    )

    # B. Metadata file folder (for metadata sufficiency metric)
    parser.add_argument(
        CLI_FLAG_METADATA_FOLDER,
        type=str,
        help="Path to folder containing metadata files"
    )

    # C. Unique string ID for the digital source of (non-baseline) compared editions
    parser.add_argument(
        CLI_FLAG_SOURCE_ID,
        type=str,
        help="Unique string ID for editions being compared"
    )

    # D. Unique string ID for a baseline edition being compared against other editions
    parser.add_argument(
        CLI_FLAG_BASELINE_SOURCE_ID,
        type=str,
        help="Unique string ID for baseline edition"
    )

    # E. Full text name of single work title data quality metric is being run on
    parser.add_argument(
        CLI_FLAG_WORK_TITLE,
        type=str,
        help="Full name of work that will have data quality metric run on it"
    )

    # F. Full text name of collection of editions being compared (against a baseline edition)
    parser.add_argument(
        CLI_FLAG_COLLECTION_TITLE,
        type=str,
        help="Full text name of collection of editions being compared"
    )

    # G. Which metrics to run (e.g. read files and run metric (compute() then evaluate())
    parser.add_argument(
        CLI_FLAG_METRICS,
        type=str,
        help=(
            "String of metric codes to run. "
            "Available: "
            "m=metadata sufficiency, "
            "v=lexical validity, "
            "c=record consensus, "
            "a=authorial signature, "
            "l=legomena, "
            "r=record counts to control records"
        )
    )

    # 2. Parse arguments from command line
    parsed_args = parser.parse_args()

    # 3. Validate argument values
    validation_error = validate_args(parsed_args)

    return parsed_args, validation_error

def validate_args(p_parsed_args):

    # If no error, string will be blank
    validation_error = ""

    # Input folder
    if p_parsed_args.input_folder and not os.path.isdir(p_parsed_args.input_folder):
        validation_error = f"Invalid input folder: {p_parsed_args.input_folder}"
    # Metadata folder
    elif p_parsed_args.metadata_folder and not os.path.isdir(p_parsed_args.metadata_folder):
        validation_error = f"Invalid metadata folder: {p_parsed_args.metadata_folder}"
    # Metric flags
    elif p_parsed_args.metrics:
        metrics = set(p_parsed_args.metrics or "")
        invalid_metric_flags = metrics - VALID_METRICS
        if invalid_metric_flags:
            validation_error = f"Invalid metrics given: {invalid_metric_flags}"

    return validation_error


# Main Script

def run_command_line_tool():

    # 0. Runtime saved for output file
    script_run_time = datetime.now().strftime("%d%m%Y_%H%M%S")
    
    # 0. Retrieve command line arguments and check they are valid
    args, validation_error = parse_args()
    if validation_error:
        print(validation_error)
        return
    
    # 0. Lexicon will only be stored in memory if lexical validity metric is used
    coha_lexicon = None
    
    # =========================================================================
    # 1. Parameters for the data quality metric

    # A. The location of JSON dataset and metadata file(s) on the drive
    EDITIONS_LOCATION = args.input_folder if args.input_folder else CLI_DATASET_LOCATION
    METADATA_LOCATION = args.metadata_folder if args.metadata_folder else CLI_METADATA_LOCATION

    # B. Unique string IDs
    CLI_BASELINE_SOURCE_ID = args.baseline_source_id if args.baseline_source_id else SOURCE_ID_MTPO # 'mark_twain_project'
    CLI_SOURCE_ID = args.source_id if args.source_id else SOURCE_ID_IA  # 'internet_archive'
    CLI_COLLECTION_TITLE = args.collection_title if args.collection_title else "Internet Archive"
    CLI_WORK_TITLE = args.work_title if args.work_title else "Adventures of Huckleberry Finn"

    # 2. Read editions and metadata into reader objects
    edition_readers = None
    metadata = None
    only_metadata_metrics = METRIC_FLAG_METADATA_SUFFICIENCY == args.metrics
    if METRIC_FLAG_METADATA_SUFFICIENCY in args.metrics:
        metadata = read_metadata_files_by_source(METADATA_LOCATION, CLI_SOURCE_ID)
    if not only_metadata_metrics:
        edition_readers = read_huckfinn_dataset_files_by_source(
            EDITIONS_LOCATION, CLI_SOURCE_ID)
        if args.baseline_source_id:
            edition_readers.update(read_huckfinn_dataset_files_by_source(
                EDITIONS_LOCATION, CLI_BASELINE_SOURCE_ID))
    

    # 3. Run data quality metrics over the editions and/or metadata

    # A. Create the metric object(s)
    metric_list = {}
    for metric_flag in args.metrics:

        if METRIC_FLAG_AUTHORIAL_SIGNATURE == metric_flag:
            
            metric_list[metric_flag] = create_metric(
                metric_flag,
                [reader.filepath for reader in edition_readers[CLI_SOURCE_ID]]
            )
        elif METRIC_FLAG_METADATA_SUFFICIENCY == metric_flag:

            metric_list[metric_flag] = create_metric(
                metric_flag,
                metadata,
                p_collection_title=CLI_COLLECTION_TITLE,
                p_metric_id=f"{CLI_WORK_TITLE}_{CLI_SOURCE_ID}_MetadataSufficiency",
                p_source_id=CLI_SOURCE_ID,
                p_work_title=CLI_WORK_TITLE
            )
        elif METRIC_FLAG_RECORD_CONSENSUS == metric_flag:
        
            metric_list[metric_flag] = create_metric(
                metric_flag,
                edition_readers,
                p_collection_title=f"{CLI_SOURCE_ID}_{CLI_BASELINE_SOURCE_ID}",
                p_input_location=EDITIONS_LOCATION,
                p_metric_id=f"{CLI_WORK_TITLE}_{CLI_SOURCE_ID}_{CLI_BASELINE_SOURCE_ID}_RecordConsensus",
                p_source_id=f"{CLI_SOURCE_ID}_{CLI_BASELINE_SOURCE_ID}",
                p_work_title=CLI_WORK_TITLE
            )

        elif METRIC_FLAG_LEGOMENA == metric_flag:
        
            metric_list[metric_flag] = create_metric(
                "",
                edition_readers,
                p_metric_id=f"{CLI_SOURCE_ID}_Legomena"
            )
        elif METRIC_FLAG_LEXICAL_VALIDITY == metric_flag:

            # Make sure to load 'Corpus of Historical American English' lexicon, if not already loaded
            if not coha_lexicon:
                coha_lexicon = read_coha(LEXICON_LOCATION)

            metric_list[metric_flag] = create_metric(
                metric_flag,
                edition_readers,
                p_auxiliary_data=coha_lexicon,
                p_collectiont_title=CLI_COLLECTION_TITLE,
                p_input_location=EDITIONS_LOCATION,
                p_metric_id=f"{CLI_WORK_TITLE}_{CLI_SOURCE_ID}_LexicalValidity",
                p_source_id=CLI_SOURCE_ID,
                p_work_title=CLI_WORK_TITLE
            )
        elif METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORDS == metric_flag:

            metric_list[metric_flag] = create_metric(
                metric_flag,
                edition_readers,
                p_baseline_source_id=CLI_BASELINE_SOURCE_ID,
                p_collection_title=CLI_COLLECTION_TITLE,
                p_input_location=EDITIONS_LOCATION,
                p_metric_id=f"{CLI_WORK_TITLE}_{CLI_BASELINE_SOURCE_ID}v{CLI_SOURCE_ID}_RecCountsToControlRecs",
                p_source_id=CLI_SOURCE_ID,
                p_work_title=CLI_WORK_TITLE,
            )

    # B. Compute metric values for each metric
    for metric in metric_list.values():
        metric.compute()
        metric.evaluate()

    # C. Output the metric values
    for metric in metric_list.values():
        evaluation_output_filepath = f"{CLI_OUTPUT_LOCATION}{metric.s_metric_name}_metric_values_{script_run_time}.json"
        output_metric_values(metric, evaluation_output_filepath)


def main():

    # Run command line tool if command line arguments given to script
    if len(sys.argv) > 1:
        run_command_line_tool()


if "__main__" == __name__:
    main()
