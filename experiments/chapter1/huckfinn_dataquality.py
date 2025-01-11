# Author: Jonathan Armoza
# Created: July 25, 2024
# Purpose: Measuring data quality for the Huckleberry Finn data set

# List of data quality metrics to consider

# 1. Consistency
# 2. Integrity

# Tasks

# 1. Come up with reasonable interpretations/metrics of consistency and integrity for the Huck Finn corpus
# 2. Understand the state of the Huck Finn corpus
# - Create a document where the folders/files of the Twain corpus are explained and their provenance properly cited
# 3. Consider how metrics will apply to either the raw data downloaded or the demarcated data
# - e.g. Maybe we would prefer to put some dq metrics over the raw data, and for others examining portions of the text
# itself to use the demarcated data
# 4. Consider metadata assessments as dq metrics

# Note: Demarcated data consists of texts that have been uniformly subdivided by using uniform headings
# i.e. Huck Finn being divided by the same chapter name so chapter text can undergo relevant dq metrics


# NOTE: Thoughts/hypotheses and then findings should be written up
# These writings can then be used as an experimental (scientific) means of tweaking the data quality
# metrics, how they are weighted in the data quality framework machine/script


### Experiment 1

# Metadata quality

# Hypothesis

### Experiment 2

# Text quality
# Let's re-read Sebastian Coleman and my notes for data quality metrics that would be applicable for the texts in the collection
# Then implement a few metrics using the text ingestion utility scripts already written

# Hypothesis: Texts should (1) Contain all chapters found in the Ur copy (MTPO)
# and (2) be mostly identical internally chapter by chapter

# Format for experiment functions

# <quality-type>_<work-short-title>_<experiment-short-description>_<experiment-number>

# Imports

# Built-ins
import json
import os
import sys
from statistics import mean

# Custom

# Command line
sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}data_quality{os.sep}core")

# IDE
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}data_quality{os.sep}core")

from dq_metric import DataQualityMetric
from mtpo_huckfinn_reader import MTPOHuckFinnReader
from pg_huckfinn_reader import PGHuckFinnReader


# Globals

huckfinn_paths = {

    "ia_json_path": "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/json",
    "ia_txt_path": "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/txt",
    "pg_path": "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/project_gutenberg"
}

# Mark Twain Project Online abbreviation
MTPO = "mtpo"

# Utility functions

def read_marktwain_project_online_text():

    # 1. Read in Ur text
    mtpo_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    mtpo_huckfinn_file = "MTDP10000_edited.xml"
    mtpo_reader = MTPOHuckFinnReader(mtpo_huckfinn_filepath + mtpo_huckfinn_file)
    mtpo_reader.read()
    
    return mtpo_reader    

def read_project_gutenberg_metadata():

    pg_huckfinn_filepath = f"{huckfinn_paths["pg_path"]}{os.sep}metadata{os.sep}"
    subject_filepath_list = [
        
        pg_huckfinn_filepath + "2011-05-03-HuckFinn_metadata.json",
        pg_huckfinn_filepath + "2016-08-17-HuckFinn_metadata.json",
        pg_huckfinn_filepath + "2021-02-21-HuckFinn_metadata.json"
    ]
    metadata_json = {}
    for subject_filepath in subject_filepath_list:
        with open(subject_filepath, "r") as json_file:
            metadata_json[os.path.basename(subject_filepath)] = json.load(json_file)

    return metadata_json

def read_project_gutenburg_text():

    huckfinn_text_readers = {}

    # 1. Read in each Project Gutenberg edition of Huckleberry Finn
    pg_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}project_gutenberg{os.sep}json{os.sep}"
    subject_filepath_list = [
        pg_huckfinn_filepath + "2011-05-03-HuckFinn.json",
        pg_huckfinn_filepath + "2016-08-17-HuckFinn.json",
        pg_huckfinn_filepath + "2021-02-21-HuckFinn.json"
    ]
    for filepath in subject_filepath_list:
        huckfinn_text_readers[os.path.basename(filepath)] = PGHuckFinnReader(filepath)
        huckfinn_text_readers[os.path.basename(filepath)].read()

    return huckfinn_text_readers

# Experiments

# Metric run helper functions

def run_pg_huckfinn_dq_metadatasufficiency():

    # Metadata sufficiency (MTPO vs PG)

    huckfinn_pg_metadata = read_project_gutenberg_metadata()
    huckfinn_pg_metadata_sufficiency = DataQualityMetric("HuckFinn_PG_MetadataSufficiency", huckfinn_pg_metadata)
    huckfinn_pg_metadata_sufficiency.run(p_show_explanations=True)

    return huckfinn_pg_metadata_sufficiency

def run_pg_huckfinn_dq_textrecordcounts():

    # Text record counts (MTPO vs PG)

    # 1. Read ur text and subject texts
    huckfinn_textdata = read_project_gutenburg_text()
    huckfinn_textdata[MTPO] = read_marktwain_project_online_text()

    # 2. Create data quality metric
    huckfinn_pg_text_recordcounts = DataQualityMetric("HuckFinn_PG_TextRecordCounts", huckfinn_textdata)
    huckfinn_pg_text_recordcounts.urtext_name = MTPO
    huckfinn_pg_text_recordcounts.metric_min = 0.95

    # 3. Compute metric and save results
    huckfinn_pg_text_recordcounts.compute()

    # 4. Visualize metric with metric min falloff chart

    return huckfinn_pg_text_recordcounts


def main():

    dq_metrics = [
        run_pg_huckfinn_dq_metadatasufficiency(),
        run_pg_huckfinn_dq_textrecordcounts()
    ]

    dq_metric_evaluations = [metric.evaluate() for metric in dq_metrics]
    
    overall_evaluation = mean(dq_metric_evaluations)

    print(f"Overall Project Gutenberg data quality: {overall_evaluation}")


if "__main__" == __name__:

    main() 









