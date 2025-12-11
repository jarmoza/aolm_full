# Author: Jonathan Armoza
# Created: December 2, 2025
# Purpose: Store helper functions and values for the 'Art of Literary Modeling' CLI script

# Imports

# Built-ins
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

# Edition folder names
SOURCE_ID_IA = "internet_archive"
SOURCE_ID_MTPO = "mark_twain_project"
SOURCE_ID_PG = "project_gutenberg"

# CLI flag values and variables
CLI_FLAG_BASELINE_SOURCE_ID = "--baseline-source-id"
CLI_FLAG_COLLECTION_TITLE = "--collection-title"
CLI_FLAG_INPUT_FOLDER = "--input-folder"
CLI_FLAG_METADATA_FOLDER = "--metadata_folder"
CLI_FLAG_METRICS = "--metrics"
CLI_FLAG_SOURCE_ID = "--source-id"
CLI_FLAG_WORK_TITLE = "--work-title"

METRIC_FLAG_AUTHORIAL_SIGNATURE = "a"
METRIC_FLAG_RECORD_CONSENSUS = "c"
METRIC_FLAG_LEGOMENA = "l"
METRIC_FLAG_METADATA_SUFFICIENCY = "m"
METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORDS = "r"
METRIC_FLAG_LEXICAL_VALIDITY = "v"

METRIC_FLAG_TO_OBJECT_DICT = {

    METRIC_FLAG_AUTHORIAL_SIGNATURE: DatasetSignature_AuthorialSignature,
    METRIC_FLAG_RECORD_CONSENSUS: DatasetConsistency_RecordConsensus,
    METRIC_FLAG_LEGOMENA: DatasetSignature_Legomena,
    METRIC_FLAG_METADATA_SUFFICIENCY: DatasetCompleteness_MetadataSufficiency,
    METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORDS: DatasetCompleteness_RecordCountsToControlRecords,
    METRIC_FLAG_LEXICAL_VALIDITY: DatasetValidity_LexicalValidity
}
VALID_METRICS = set(METRIC_FLAG_TO_OBJECT_DICT.keys())

# Text Reading Helper Functions

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
    
def read_metadata_files_by_source(p_json_folder, p_source_id):

    # 0. Ensure folder ends with a separator
    json_folder = p_json_folder
    if not json_folder.endswith(os.sep):
        json_folder += os.sep

    # 0. Dictionary to hold data keyed by folder name
    json_data = {}

    # 1. Read all JSON files in the subfolder for the given source ID
    folder_path = os.path.join(json_folder, p_source_id)
    json_filepaths = glob.glob(os.path.join(folder_path, "*.json"))
    for filepath in json_filepaths:
        with open(filepath, "r") as json_file:
            json_data[os.path.basename(filepath)] = json.load(json_file)

    return json_data


# Output Helper Functions

# NOTE: Output has yet to be standardized across AoLM metric and assessment implementations
# For this reason, the 'output_metric_tallies' and 'output_metric_values' functions
# have been provided for tutorial users

def output_metric_tallies(p_metric, p_output_filepath):
    
    if p_metric.s_metric_name == DatasetCompleteness_MetadataSufficiency.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetCompleteness_RecordCountsToControlRecords.s_metric_name:
        
        results_lines = p_metric.results_full_counts(p_include_header=True)
        with open(p_output_filepath, "w") as output_file:
            output_file.write("\n".join(results_lines))

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

        with open(p_output_filepath, "w") as output_file:
            json.dump(p_metric.eval_output, output_file, indent=4)
    elif p_metric.s_metric_name == DatasetConsistency_RecordConsensus.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetSignature_AuthorialSignature.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetSignature_Legomena.s_metric_name:
        pass
    elif p_metric.s_metric_name == DatasetValidity_LexicalValidity.s_metric_name:
        pass


# Metric Creation Helper Functions

# Factory function for the data quality metrics of 'Art of Literary Modeling'
def create_metric(
        p_metric_flag,
        p_input,
        p_auxiliary_data="",
        p_baseline_source_id="",
        p_collection_title="",
        p_input_location="",
        p_metric_id="",
        p_source_id="",
        p_work_title=""
):
    
    if METRIC_FLAG_AUTHORIAL_SIGNATURE == p_metric_flag:
        
        return DatasetSignature_AuthorialSignature(p_input)
    elif METRIC_FLAG_RECORD_CONSENSUS == p_metric_flag:
        
        return DatasetConsistency_RecordConsensus(
            p_metric_id,
            p_input,
            p_source_id,
            p_work_title,
            p_collection_title,
            p_input_location
        )
    elif METRIC_FLAG_LEGOMENA == p_metric_flag:
        
        return DatasetSignature_Legomena(p_input)
    elif METRIC_FLAG_METADATA_SUFFICIENCY == p_metric_flag:
        
        return DatasetCompleteness_MetadataSufficiency(
                p_metric_id,
                p_input,
                p_source_id,
                p_work_title,
                p_collection_title,
                p_input_location
            )
    elif METRIC_FLAG_RECORDCOUNTS_TO_CONTROLRECORDS == p_metric_flag:

        return DatasetCompleteness_RecordCountsToControlRecords(
            p_metric_id,
            p_input,
            p_source_id,
            p_work_title,
            p_collection_title,
            p_input_location,
            p_baseline_source_id
        )
    elif METRIC_FLAG_LEXICAL_VALIDITY == p_metric_flag:

        return DatasetValidity_LexicalValidity(
            p_metric_id,
            p_input,
            p_source_id,
            p_work_title,
            p_collection_title,
            p_input_location,
            p_auxiliary_data
        )            