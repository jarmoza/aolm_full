# Author: Jonathan Armoza
# Created: December 2, 2025
# Purpose: Store helper functions for the 'Art of Literary Modeling' tutorial script

# Imports

# Built-ins
import argparse
import glob
import json
import os
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom

# Edition readers
from ia_huckfinn_reader import IAHuckFinnReader
from mtpo_huckfinn_reader import MTPOHuckFinnReader
from pg_huckfinn_reader import PGHuckFinnReader

# Data quality metrics
from aolm_code.data_quality.core.dq_metric import DataQualityMetric
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords
from dq_metrics.dataset_consistency.consistency_recordconsensus import DatasetConsistency_RecordConsensus
from dq_metrics.dataset_signature.authorial_signature import DatasetSignature_AuthorialSignature
from dq_metrics.dataset_signature.legomena import DatasetSignature_Legomena
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity


# Globals

# Values for command line script

METRIC_FLAG_AUTHORIAL_SIGNATURE = "a"
METRIC_FLAG_CONSISTENCY_RECORDCONSENSUS = "c"
METRIC_FLAG_LEGOMENA = "l"
METRIC_FLAG_METADATA_SUFFICIENCY = "m"
METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORD = "r"
METRIC_FLAG_LEXICAL_VALIDITY = "v"

METRIC_FLAG_TO_OBJECT_DICT = {

    METRIC_FLAG_AUTHORIAL_SIGNATURE: DatasetSignature_AuthorialSignature,
    METRIC_FLAG_CONSISTENCY_RECORDCONSENSUS: DatasetConsistency_RecordConsensus,
    METRIC_FLAG_LEGOMENA: DatasetSignature_Legomena,
    METRIC_FLAG_METADATA_SUFFICIENCY: DatasetCompleteness_MetadataSufficiency,
    METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORD: DatasetCompleteness_RecordCountsToControlRecords,
    METRIC_FLAG_LEXICAL_VALIDITY: DatasetValidity_LexicalValidity
}
VALID_METRICS = set(METRIC_FLAG_TO_OBJECT_DICT.keys())

# Edition folder names

SOURCE_ID_IA = "internet_archive"
SOURCE_ID_MTPO = "mark_twain_project"
SOURCE_ID_PG = "project_gutenberg"

# Helper functions

def parse_args():

    # 1. Set up argument parser
    parser = argparse.ArgumentParser(description="Tutorial for 'Art of Literary Modeling'")

    # A. Dataset file folder for metrics (other than metadata sufficiency)
    parser.add_argument(
        "--input-folder",
        type=str,
        help="Path to folder containing input records"
    )

    # B. Metadata file folder (for metadata sufficiency metric)
    parser.add_argument(
        "--metadata-folder",
        type=str,
        help="Path to folder containing metadata files"
    )

    # C. Which metrics to run (e.g. read files and run metric (compute() then evaluate())
    parser.add_argument(
        "-m", "--metrics",
        type=str,
        help=(
            "String of metric codes to run. "
            "Available: "
            "m=metadata sufficiency, "
            "v=lexical validity, "
            "c=record consensus, "
            "a=authorial signature, "
            "l=legomena, "
            "r=record counts"
        )
    )

    # 2. Parse arguments from command line
    parsed_args = parser.parse_args()

    # 3. Validate argument values
    validation_error = validate_args(parsed_args)

    return parsed_args, validation_error

def read_huckfinn_dataset_files_by_source(p_dataset_location, p_source_id):
    
    # 1. Get all JSON filepaths in p_dataset_location's subfolder for p_source_id
    edition_filepaths = []
    if SOURCE_ID_MTPO == p_source_id:
        edition_filepaths = glob.glob(os.path.join(p_dataset_location + p_source_id, f"*.xml"))
    else:
        edition_filepaths = glob.glob(os.path.join(p_dataset_location + p_source_id, "*.json"))

    # 2. Create collection-specific reader objects for each edition and read/process each edition
    if SOURCE_ID_IA == p_source_id:
        huckfinn_text_readers = { filepath: IAHuckFinnReader(filepath) for filepath in edition_filepaths }
        for filepath in edition_filepaths:
            huckfinn_text_readers[filepath].read()        
    elif SOURCE_ID_PG == p_source_id:
        huckfinn_text_readers = { filepath: PGHuckFinnReader(filepath) for filepath in edition_filepaths }
        for filepath in edition_filepaths:
            huckfinn_text_readers[filepath].read()        
    elif SOURCE_ID_MTPO == p_source_id:
        huckfinn_text_readers = { SOURCE_ID_MTPO:  MTPOHuckFinnReader(edition_filepaths[0]) }
        huckfinn_text_readers[SOURCE_ID_MTPO].read()

    return huckfinn_text_readers
    
def read_metadata_files_by_source(p_json_folder):

    # 0. Ensure folder ends with a separator
    json_folder = p_json_folder
    if not json_folder.endswith(os.sep):
        json_folder += os.sep

    # 0. Dictionary to hold data keyed by folder name
    json_data = {}

    # 1. Read all JSON files in json_folder's top level subfolders
    for folder_name in os.listdir(json_folder):
        
        folder_path = os.path.join(json_folder, folder_name)

        if os.path.isdir(folder_path):
            
            # A. Find all JSON files in this subfolder
            json_filepaths = glob.glob(os.path.join(folder_path, "*.json"))

            # B. Read and store JSON files for this folder
            json_data[folder_name] = {}
            for filepath in json_filepaths:
                with open(filepath, "r") as json_file:
                    json_data[folder_name][os.path.basename(filepath)] = json.load(json_file)

    return json_data

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

# Output functions for metric tallies

# NOTE: Output has yet to be standardized across AoLM metric and assessment implementations
# For this reason, the 'output_metric_tallies' and 'output_metric_values' functions
# have been provided for tutorial users

def output_metric_tallies(p_metric, p_output_filepath):
    
    if p_metric.s_metric_name == DatasetCompleteness_MetadataSufficiency.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetCompleteness_RecordCountsToControlRecords.s_metric_name:
        output_recordcounts_to_controlrecord_tallies(p_metric, p_output_filepath)
    elif p_metric.s_metric_name == DatasetConsistency_RecordConsensus.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetSignature_AuthorialSignature.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetSignature_Legomena.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetValidity_LexicalValidity.s_metric_name:
        pass

def output_metric_values(p_metric, p_output_filepath):

    if p_metric.s_metric_name == DatasetCompleteness_MetadataSufficiency.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetCompleteness_RecordCountsToControlRecords.s_metric_name:
        output_recordcounts_to_controlrecord_values(p_metric, p_output_filepath)
    elif p_metric.s_metric_name == DatasetConsistency_RecordConsensus.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetSignature_AuthorialSignature.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetSignature_Legomena.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetValidity_LexicalValidity.s_metric_name:
        pass

def output_recordcounts_to_controlrecord_tallies(p_metric, p_output_filepath):

    results_lines = p_metric.results_full_counts(p_include_header=True)

    with open(p_output_filepath, "w") as output_file:
        output_file.write("\n".join(results_lines))

def output_recordcounts_to_controlrecord_values(p_metric, p_output_filepath):

    with open(p_output_filepath, "w") as output_file:

        DataQualityMetric.write_output_header(output_file)
        metric_values = p_metric.output
        output_file.write(metric_values)
