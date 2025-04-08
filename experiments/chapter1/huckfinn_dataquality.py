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

"""
    Data Quality Metrics

    1) Lexical Validity
    - Takes in multiple editions across a collection
    2) Metadata Sufficiency
    3) Record Counts to Control Records

"""

# Imports

# Built-ins
import csv
import os
import sys
from datetime import datetime
from statistics import mean

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Third party
import pandas as pd
import plotly.express as px

# Custom

import aolm_data_reading
from aolm_utilities import print_debug_header
from dq_metric import DataQualityMetric
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords

# Globals

# String constants
MS_METRIC_NAME = DatasetCompleteness_MetadataSufficiency.s_metric_name
TR_METRIC_NAME = DatasetCompleteness_RecordCountsToControlRecords.s_metric_name
WORK_TITLE = "Adventures of Huckleberry Finn"
UR_EDITION = aolm_data_reading.MTPO

# For output and plotting after metric evaluation
experiment_metrics = { source_id: 
    {
        MS_METRIC_NAME: {
            "metric": None,
            "evaluation": None
        },
        TR_METRIC_NAME: {
            "individual_editions": {
                edition_name: {
                    "metric": None,
                    "evaluation": None
                } for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]
            },
            "overall": {
                "metric": None,
                "evaluation": None
            }
        },
        "overall_data_quality": None
    } for source_id in aolm_data_reading.huckfinn_source_fullnames if aolm_data_reading.MTPO != source_id
}


# Experiments

# Metric run helper functions

def run_huckfinn_dq_metadatasufficiency(p_source_id, p_edition_filenames=None):

    # Metadata sufficiency
    # (Comparison among <p_source_id> editions only)

    # 1. Read in texts to be compared
    print(f"Reading metadata for editions of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[p_source_id]}...")
    huckfinn_metadata = aolm_data_reading.read_huckfinn_metadata(p_source_id, p_edition_filenames)

    # 2. Create the data quality metric
    edition_str = "all editions" if None == p_edition_filenames else "editions " + ", ".join(p_edition_filenames)
    print(f"Computing '{MS_METRIC_NAME}' for {edition_str} of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[p_source_id]}...")
    huckfinn_metadata_sufficiency = DatasetCompleteness_MetadataSufficiency(
        f"HuckFinn_{p_source_id}_MetadataSufficiency",
        huckfinn_metadata,
        p_source_id,
        WORK_TITLE,
        aolm_data_reading.huckfinn_source_fullnames[p_source_id],
        aolm_data_reading.huckfinn_directories[p_source_id]["metadata"])

    # 3. Compute the metric and save results
    huckfinn_metadata_sufficiency.compute()

    # Return instance of the metric for further use
    return huckfinn_metadata_sufficiency

def run_huckfinn_dq_textrecordcounts(p_source_id, p_edition_filenames=None):

    # Text record counts
    # (Comparing Mark Twain Project Online edition record counts versus
    # <p_source_id> edition record counts)

    # NOTE: Make sure p_huckfinn_textdata matches the edition filenames passed in

    # 1. Read ur text and subject texts
    print(f"Reading text of editions of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[p_source_id]}...")
    huckfinn_textdata = aolm_data_reading.read_huckfinn_text(p_source_id, p_edition_filenames)
    print(f"Reading text of edition of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[aolm_data_reading.MTPO]} as the control record...")
    huckfinn_textdata[aolm_data_reading.MTPO] = aolm_data_reading.read_marktwain_project_online_text()

    # 2. Create the data quality metric
    edition_str = "all editions" if None == p_edition_filenames else "editions " + ", ".join(p_edition_filenames)
    print(f"Computing '{TR_METRIC_NAME}' for {edition_str} of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[p_source_id]}...")
    edition_path = aolm_data_reading.huckfinn_directories[p_source_id]["txt"]
    if p_edition_filenames and len(p_edition_filenames):
        edition_path += p_edition_filenames[0]
    huckfinn_text_recordcounts = DatasetCompleteness_RecordCountsToControlRecords(
        f"HuckFinn_MTPOv{p_source_id}_TextRecordCounts",
        huckfinn_textdata,
        p_source_id,
        WORK_TITLE,
        aolm_data_reading.huckfinn_source_fullnames[p_source_id],
        edition_path,
        aolm_data_reading.MTPO)

    huckfinn_text_recordcounts.urtext_name = aolm_data_reading.MTPO
    huckfinn_text_recordcounts.metric_min = 0.95

    # 3. Compute the metric and save results
    huckfinn_text_recordcounts.compute()

    # Return instance of the metric for further use
    return huckfinn_text_recordcounts


# Main script

def read_and_compute_metrics():

    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        # Skip ur edition
        if UR_EDITION == source_id:
            continue

        huckfinn_textdata = None

        # A. Rate source_id editions data quality based on metadata sufficiency
        experiment_metrics[source_id][MS_METRIC_NAME]["metric"] = \
            run_huckfinn_dq_metadatasufficiency(source_id)

        # B. Rate individual source_id editions based on text record counts vs. ur edition
        for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
            experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"] = \
                run_huckfinn_dq_textrecordcounts(source_id, [f"{edition_name}-HuckFinn.json"])

        # C. Rate all source_id editions based on text record counts vs. ur edition
        experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"] = \
            run_huckfinn_dq_textrecordcounts(source_id)
        
def evaluate_metrics():

    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        # Skip ur edition
        if UR_EDITION == source_id:
            continue

        source_fullname = aolm_data_reading.huckfinn_source_fullnames[source_id]

        # A. Metadata sufficiency
        experiment_metrics[source_id][MS_METRIC_NAME]["evaluation"] = \
            experiment_metrics[source_id][MS_METRIC_NAME]["metric"].evaluate()
        print(f"{source_fullname} '{MS_METRIC_NAME}' metric: {experiment_metrics[source_id][MS_METRIC_NAME]["evaluation"]}")

        # B. Text record counts to control record by edition
        for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
            experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["evaluation"] = \
                experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].evaluate()
            print(f"{source_fullname} '{TR_METRIC_NAME}' metric for {edition_name}: {experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["evaluation"]}")

        # C. Overall text record counts to control record of all editions from this source
        experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["evaluation"] = \
            experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"].evaluate()
        print(f"Overall {source_fullname} '{TR_METRIC_NAME}' metric: {experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["evaluation"]}")

        # D. Evaluation for both metadata sufficiency and text record counts to control record
        experiment_metrics[source_id]["overall_data_quality"] = mean([
            experiment_metrics[source_id][MS_METRIC_NAME]["evaluation"],
            experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["evaluation"]
        ])

        metric_weights = {
            MS_METRIC_NAME: 0.25,
            TR_METRIC_NAME: 0.75
        }
        experiment_metrics[source_id]["overall_data_quality"] = \
            (metric_weights[MS_METRIC_NAME] * experiment_metrics[source_id][MS_METRIC_NAME]["evaluation"]) + \
            (metric_weights[TR_METRIC_NAME] * experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["evaluation"])
        print(f"Overall {source_fullname} data quality: {experiment_metrics[source_id]["overall_data_quality"]}")

def output_results(p_output_filepath):

    print(f"Outputting results to: {p_output_filepath}")

    # 1. Output evaluation details

    # A. Metadata sufficiency 
    eval_ms_output_filepath = p_output_filepath.replace(".csv", f"_eval_{MS_METRIC_NAME}.csv")
    
    with open(eval_ms_output_filepath, "w") as eval_output_file:

        # Output csv header
        DatasetCompleteness_MetadataSufficiency.write_eval_output_header(eval_output_file)

        for source_id in aolm_data_reading.huckfinn_source_fullnames:

            # Skip ur edition
            if UR_EDITION == source_id:
                continue
            
            eval_output_file.write(experiment_metrics[source_id][MS_METRIC_NAME]["metric"].eval_output)

    # B. Text record counts to control records
    eval_tr_output_filepath = p_output_filepath.replace(".csv", f"_eval_{TR_METRIC_NAME}.csv")

    # Gather all column names from the metric instances
    tr_eval_column_names = []
    for source_id in aolm_data_reading.huckfinn_source_fullnames:

            # Skip ur edition
            if UR_EDITION == source_id:
                continue

            # Gather column names for individual edition (only do it once per
            # source since each edition evaluation will contain the same columns)
            for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
                eval_columns = experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].eval_output_header.strip().split(",")    
                for column in eval_columns:
                    if column not in tr_eval_column_names:
                        tr_eval_column_names.append(column)
                break

            # eval_columns = experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"].eval_output_header.strip().split(",")
            # for column in eval_columns:
            #     if column not in tr_eval_column_names:
            #         tr_eval_column_names.append(column)

    with open(eval_tr_output_filepath, "w") as eval_output_file:

        # Output csv header
        eval_output_file.write(",".join(tr_eval_column_names) + "\n")

        # DatasetCompleteness_RecordCountsToControlRecords.write_eval_output_header(eval_output_file)

        for source_id in aolm_data_reading.huckfinn_source_fullnames:

            # Skip ur edition
            if UR_EDITION == source_id:
                continue

            for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
                eval_output_dict = experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].eval_output
                values_list = []
                for key in tr_eval_column_names:
                    values_list.append(str(eval_output_dict[key]) if key in eval_output_dict else "N/A")
                eval_output_file.write(",".join(values_list) + "\n")

            # Suggest edition name "sourceid_overall" here?
            eval_output_dict = experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"].eval_output
            values_list = []
            for key in tr_eval_column_names:
                values_list.append(str(eval_output_dict[key]) if key in eval_output_dict else "N/A")
            eval_output_file.write(",".join(values_list) + "\n")

    
    # 2. Output top level stats

    with open(p_output_filepath, "w") as output_file:

        # Output csv header
        DataQualityMetric.write_output_header(output_file)

        for source_id in aolm_data_reading.huckfinn_source_fullnames:

            # Skip ur edition
            if UR_EDITION == source_id:
                continue

            # A. Metadata sufficiency
            output_file.write(experiment_metrics[source_id][MS_METRIC_NAME]["metric"].output)

            # B. Text record counts to control records for individual editions vs. ur edition
            for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
                output_file.write(experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].output)

            # C. Overall text record counts to control record of all editions from this source
            output_file.write(experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"].output)

            # D. Overall data quality measurement of the source_id editions vs. ur edition
            output_file.write(f"Overall Quality:,{experiment_metrics[source_id]["overall_data_quality"]}\n")

def plot_results(p_output_filepath):

    # 1. Read in data quality metric results
    with open(p_output_filepath, "r") as input_file:
        results_reader = csv.DictReader(input_file.readlines())

    # 2. Read in metadata sufficiency metric evaluation
    eval_ms_output_filepath = p_output_filepath.replace(".csv", f"_eval_{MS_METRIC_NAME}.csv")
    with open(eval_ms_output_filepath, "r") as input_file:
        ms_eval_reader = csv.DictReader(input_file.readlines())

    # Read in record counts to control records metric evaluation
    eval_tr_output_filepath = p_output_filepath.replace(".csv", f"_eval_{TR_METRIC_NAME}.csv")
    with open(eval_tr_output_filepath, "r") as input_file:
        tr_eval_reader = csv.DictReader(input_file.readlines())

    # Multi Bar chart out each result across editions and sources
    import plotly.express as px
    df = px.data.tips()
    fig = px.histogram(df, x="sex", y="total_bill",
             color='smoker', barmode='group',
             height=400)
    fig.show()

# Test

def plot_results2(p_output_filepath):

    # # 1. Read in data quality metric results
    # with open(p_output_filepath, "r") as input_file:
    #     results_reader = csv.DictReader(input_file.readlines())
    #     results_data = list(results_reader)

    # # 2. Read in metadata sufficiency metric evaluation
    # eval_ms_output_filepath = p_output_filepath.replace(".csv", f"_eval_{MS_METRIC_NAME}.csv")
    # with open(eval_ms_output_filepath, "r") as input_file:
    #     ms_eval_reader = csv.DictReader(input_file.readlines())
    #     ms_eval_data = list(ms_eval_reader)

    # 3. Read in record counts to control records metric evaluation
    # eval_tr_output_filepath = p_output_filepath.replace(".csv", f"_eval_{TR_METRIC_NAME}.csv")
    with open(p_output_filepath, "r") as input_file:
        tr_eval_reader = csv.DictReader(input_file.readlines())
        tr_eval_data = list(tr_eval_reader)

    # Convert the evaluation data to DataFrames
    # df_results = pd.DataFrame(results_data)
    # df_ms_eval = pd.DataFrame(ms_eval_data)
    df_tr_eval = pd.DataFrame(tr_eval_data)

    # Remove rows with empty filenames
    df_tr_eval = df_tr_eval[df_tr_eval["filename"].notna() & df_tr_eval["filename"].str.strip().astype(bool)]

    # source
    # work_title
    # edition_title
    # metric
    # value
    # compared_against
    # filename
    # filepath
    # path
    # submetric__chapter_count
    # submetric__sentence_count
    # submetric__word_count
    # subsubmetric__chapter_count
    # subsubmetric__sentence_count
    # subsubmetric__word_count

    # Example: Plot histogram for a specific metric
    # fig = px.histogram(
    #     df_tr_eval,
    #     x="value",
    #     color="source",
    #     facet_col="edition_title",
    #     labels={"value": "Metric Value", "source": "Source"},
    #     title="Metric Values by Source and Edition",
    #     barmode='group',
    #     height=600
    # )
    fig = px.bar(
        df_tr_eval,
        x="filename",
        y="value",
        title="Metric Values by Source and Edition",
        barmode='group',
        height=600
    )    
    fig.show()


def main():

    # Example usage
    # output_filepath = "/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/huckfinn_dq_experiment_26022025_155205_eval_record_counts_to_control.csv"
    # plot_results2(output_filepath)

    # if True:
    #     return    

    # Experiment Description

    # Dataset Completeness for sources of Adventures of Huckleberry Finn by Mark Twain:
    # (1) Internet Archive
    # (2) Project Gutenberg edition
    # versus
    # (3) Mark Twain Project Online

    # Data quality metrics considered:
    # (A) Metadata Sufficiency (metadata_sufficiency.py)
    # (B) Record Counts to Control Records (recordcounts_to_controlrecords.py)

    # Short-circuit to move directly to plotting once output has been generated
    compute_and_evaluate = True
    output_filepath = "/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/huckfinn_dq_experiment_05022025_150854.csv"

    if compute_and_evaluate:

        # 0. Setup

        # Run time saved for output file
        script_run_time = datetime.now().strftime("%d%m%Y_%H%M%S")

        # Results file
        output_filepath = f"{os.getcwd()}{os.sep}experiments{os.sep}outputs{os.sep}huckfinn_dq_experiment_{script_run_time}.csv"

        # 1. Read dataset(s)/Compute metrics
        print_debug_header("Reading datasets and computing data quality metrics")
        read_and_compute_metrics()

        # 2. Evaluate (submetrics and overall metrics)
        print_debug_header("Evaluating data quality metric results")
        evaluate_metrics()

        # 3. Output results for data quality metrics to csv file
        print_debug_header("Outputting metric results")
        output_results(output_filepath)
    
    # 4. Visualize metric with metric min falloff chart
    # print_debug_header("Plotting results")
    # plot_results(output_filepath)

if "__main__" == __name__:

    main() 









