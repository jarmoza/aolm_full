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
import os
import sys
from statistics import mean

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths()

# Custom

import aolm_data_reading
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords


# Experiments

# Metric run helper functions

def run_huckfinn_dq_metadatasufficiency(p_source_id, p_edition_filenames=None):

    # Metadata sufficiency
    # (Comparison among <p_source_id> editions only)

    # 1. Read in texts to be compared
    huckfinn_metadata = aolm_data_reading.read_huckfinn_metadata(p_source_id, p_edition_filenames)

    # 2. Create the data quality metric
    huckfinn_metadata_sufficiency = DatasetCompleteness_MetadataSufficiency(f"HuckFinn_{p_source_id}_MetadataSufficiency", huckfinn_metadata)

    # 3. Compute the metric and save results
    huckfinn_metadata_sufficiency.compute()

    # Return instance of the metric for further use
    return huckfinn_metadata_sufficiency

def run_huckfinn_dq_textrecordcounts(p_source_id, p_edition_filenames=None):

    # Text record counts
    # (Comparing Mark Twain Project Online edition record counts versus
    # <p_source_id> edition record counts)

    # 1. Read ur text and subject texts
    huckfinn_textdata = aolm_data_reading.read_huckfinn_text(p_source_id, p_edition_filenames)
    huckfinn_textdata[aolm_data_reading.MTPO] = aolm_data_reading.read_marktwain_project_online_text()

    # 2. Create the data quality metric
    huckfinn_text_recordcounts = DatasetCompleteness_RecordCountsToControlRecords(f"HuckFinn_MTPOv{p_source_id}_TextRecordCounts", huckfinn_textdata)
    huckfinn_text_recordcounts.urtext_name = aolm_data_reading.MTPO
    huckfinn_text_recordcounts.metric_min = 0.95

    # 3. Compute the metric and save results
    huckfinn_text_recordcounts.compute()

    # Return instance of the metric for further use
    return huckfinn_text_recordcounts


def main():

    # Data Quality of Sources:
    # (1) Internet Archive
    # (2) Project Gutenberg edition
    # versus Mark Twain Project Online
    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        source_fullname = aolm_data_reading.huckfinn_source_fullnames[source_id]

        # 1. Huck Finn source vs. Mark Twain Project Online (MTPO)

        # A. Rate source_id editions data quality based on metadata sufficiency
        metric = run_huckfinn_dq_metadatasufficiency(source_id)
        evaluation = metric.evaluate()
        print(f"{source_fullname} metadata sufficiency metric: {evaluation}")    

        # B. Rate individual source_id editions based on text record counts vs. MTPO
        for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
            metric = run_huckfinn_dq_textrecordcounts(source_id, [f"{edition_name}-HuckFinn.json"])
            evaluation = metric.evaluate()
            print(f"{source_fullname} text records count metric for {edition_name}: {evaluation}")

        # C. Rate all source_id editions based on text record counts vs. MTPO
        metric = run_huckfinn_dq_textrecordcounts(source_id)
        evaluation = metric.evaluate()
        print(f"Overall {source_fullname} text records metric: {evaluation}")

        # D. Combine the results of source_id metadata sufficiency and overall source_id text record counts vs. MTPO
        # for an overall data quality measurement of the source_id editions vs. MTPO
        metrics = [
            run_huckfinn_dq_metadatasufficiency(source_id),
            run_huckfinn_dq_textrecordcounts(source_id)
        ]
        evaluations = [metric.evaluate() for metric in metrics]
        overall_evaluation = mean(evaluations)
        print(f"Overall {source_fullname} data quality: {overall_evaluation}")

        # 4. Visualize metric with metric min falloff chart


if "__main__" == __name__:

    main() 









