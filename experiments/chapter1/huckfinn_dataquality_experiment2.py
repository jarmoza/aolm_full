# Author: Jonathan Armoza
# Created: May 14, 2025
# Purpose: Produces a granular data quality heatmap of Mark Twain's 'Adventures of Huckleberry Finn'
#          using the record counts to control records metric

# Imports

# Built-ins
import csv
import glob
import json
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
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords


# Globals

# String constants
TR_METRIC_NAME = DatasetCompleteness_RecordCountsToControlRecords.s_metric_name
UR_EDITION = aolm_data_reading.MTPO
WORK_TITLE = "Adventures of Huckleberry Finn"

# Variables

# Used to store already read Adventures of Huckleberry Finn editions
huckfinn_textdata = {}
coha_lexicon = None


# For output and plotting after metric evaluation
experiment_metrics = { source_id: 
    {
        TR_METRIC_NAME: {
            "individual_editions": {
                edition_name: {
                    "metric": None,
                    "evaluation": None
                } for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]
            },
        },
    } for source_id in aolm_data_reading.huckfinn_source_fullnames if UR_EDITION != source_id
}

ur_metrics = {
    UR_EDITION: {
        TR_METRIC_NAME: {
            "metric": 1.0,
            "evaluation": None
        }
    }
}


# Experiments

# Metric run helper functions

def select_huckfinn_textdata(p_source_id, p_edition_filenames=None):

    if p_edition_filenames:
        return { edition_filename: huckfinn_textdata[p_source_id][edition_filename] for edition_filename in p_edition_filenames }
    else:
        return huckfinn_textdata[p_source_id]

def run_huckfinn_dq_textrecordcounts(p_source_id, p_edition_filenames=None):

    # Text record counts
    # (Comparing Mark Twain Project Online edition record counts versus
    # <p_source_id> edition record counts)

    # NOTE: Make sure p_huckfinn_textdata matches the edition filenames passed in

    # 1. Read ur text and subject texts
    # huckfinn_textdata = aolm_data_reading.read_huckfinn_text(p_source_id, p_edition_filenames)
    huckfinn_texts = {}
    huckfinn_texts = select_huckfinn_textdata(p_source_id, p_edition_filenames)
    # huckfinn_textdata[aolm_data_reading.MTPO] = aolm_data_reading.read_huckfinn_text(aolm_data_reading.MTPO)
    huckfinn_texts.update(select_huckfinn_textdata(aolm_data_reading.MTPO))

    # 2. Create the data quality metric
    edition_str = "all editions" if None == p_edition_filenames else "editions " + ", ".join(p_edition_filenames)
    print(f"Computing '{TR_METRIC_NAME}' for {edition_str} of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[p_source_id]}...")
    edition_path = aolm_data_reading.huckfinn_directories[p_source_id]["txt"]
    if p_edition_filenames and len(p_edition_filenames):
        edition_path += p_edition_filenames[0]
    huckfinn_text_recordcounts = DatasetCompleteness_RecordCountsToControlRecords(
        f"HuckFinn_MTPOv{p_source_id}_TextRecordCounts",
        huckfinn_texts,
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

def read_texts():

    for source_id in aolm_data_reading.huckfinn_source_fullnames:
        print(f"Reading text of editions of {WORK_TITLE} from {aolm_data_reading.huckfinn_source_fullnames[source_id]}...")
        huckfinn_textdata[source_id] = aolm_data_reading.read_huckfinn_text(source_id)

def compute_metrics():

    # Rate individual source_id editions based on text record counts vs. ur edition
    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        # Skip ur edition
        if UR_EDITION == source_id:
            continue

        print_debug_header(f"Computing {source_id} metrics")

        for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
            experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"] = \
                run_huckfinn_dq_textrecordcounts(source_id, [f"{edition_name}-HuckFinn.json"])

def compute_and_evaluate_ur_edition():

    source_fullname = aolm_data_reading.huckfinn_source_fullnames[UR_EDITION]

    # Since there is no other edition to compare to text records to control records is 100%
    ur_metrics[UR_EDITION][TR_METRIC_NAME]["metric"] = DatasetCompleteness_RecordCountsToControlRecords(
        f"HuckFinn_MTPOv{UR_EDITION}_TextRecordCounts",
        select_huckfinn_textdata(UR_EDITION),
        UR_EDITION,
        WORK_TITLE,
        aolm_data_reading.huckfinn_source_fullnames[UR_EDITION],
        aolm_data_reading.huckfinn_directories[UR_EDITION]["txt"],
        aolm_data_reading.MTPO)
    ur_metrics[UR_EDITION][TR_METRIC_NAME]["metric"].set_evalmetric_value(100.0)
    ur_metrics[UR_EDITION][TR_METRIC_NAME]["evaluation"] = ur_metrics[UR_EDITION][TR_METRIC_NAME]["metric"].evaluations["metric"]

def evaluate_metrics():

    # Compute record counts to control records metric for each edition
    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        # Skip ur edition
        if UR_EDITION == source_id:
            continue

        print(f"Evaluating {source_id} metrics")

        source_fullname = aolm_data_reading.huckfinn_source_fullnames[source_id]

        for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
            experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["evaluation"] = \
                experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].evaluate()
            print(f"{source_fullname} '{TR_METRIC_NAME}' metric for {edition_name}: {experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["evaluation"]}")

def output_results(p_script_run_time):

    # Overall data quality results file
    output_filepath = f"{os.getcwd()}{os.sep}experiments{os.sep}outputs{os.sep}huckfinn_dq_experiment_{p_script_run_time}.csv"

    # 1. Output evaluation details

    # A. Lexical validity
    eval_lv_output_filepath = output_filepath.replace(".csv", f"_eval_{LV_METRIC_NAME}.json")

    # I. Experiment editions
    lv_eval_output = { source_id: experiment_metrics[source_id][LV_METRIC_NAME]["metric"].eval_output \
        for source_id in aolm_data_reading.huckfinn_source_fullnames if UR_EDITION != source_id }
    
    # II. Ur edition
    lv_eval_output[UR_EDITION] = ur_metrics[UR_EDITION][LV_METRIC_NAME]["metric"].eval_output

    print(f"Outputting {LV_METRIC_NAME} results to: {eval_lv_output_filepath}")
    with open(eval_lv_output_filepath, "w") as eval_output_file:
        json.dump(lv_eval_output, eval_output_file, indent=4)

    # B. Metadata sufficiency 
    eval_ms_output_filepath = output_filepath.replace(".csv", f"_eval_{MS_METRIC_NAME}.json")

    # I. Experiment editions
    ms_eval_output = { source_id: experiment_metrics[source_id][MS_METRIC_NAME]["metric"].eval_output \
        for source_id in aolm_data_reading.huckfinn_source_fullnames if UR_EDITION != source_id }
    
    # II. Ur editions
    ms_eval_output[UR_EDITION] = ur_metrics[UR_EDITION][MS_METRIC_NAME]["metric"].eval_output
    
    print(f"Outputting {MS_METRIC_NAME} results to: {eval_ms_output_filepath}")
    with open(eval_ms_output_filepath, "w") as eval_output_file:
        json.dump(ms_eval_output, eval_output_file, indent=4)

    # C. Text record counts to control records
    eval_tr_output_filepath = output_filepath.replace(".csv", f"_eval_{TR_METRIC_NAME}.json")

    # I. Merge all json evaluation data from text record counts to control record metrics
    tr_eval_output = {}
    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        # Skip ur edition
        if UR_EDITION == source_id:
            continue

        # Individual edition and overall source metrics evaluation data
        tr_eval_output[source_id] = {

            "individual_editions": { 
                edition_name: experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].eval_output \
                    for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]
            },
            "overall": experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"].eval_output
        }

    # II. Ur edition
    tr_eval_output[UR_EDITION] = {
        
        "individual_editions": {},
        "overall": ur_metrics[UR_EDITION][TR_METRIC_NAME]["metric"].eval_output
    }

    # III. Output all metric evaluation data to a single file
    print(f"Outputting {TR_METRIC_NAME} results to: {eval_tr_output_filepath}")
    with open(eval_tr_output_filepath, "w") as eval_output_file:
        json.dump(tr_eval_output, eval_output_file, indent=4)

    # 2. Output top level stats
    print(f"Outputting overall data quality results to: {output_filepath}")
    with open(output_filepath, "w") as output_file:

        # A. Output csv header
        DataQualityMetric.write_output_header(output_file)

        # B. Experiment editions
        for source_id in aolm_data_reading.huckfinn_source_fullnames:

            # Skip ur edition
            if UR_EDITION == source_id:
                continue

            # I. Lexical validity
            output_file.write(experiment_metrics[source_id][LV_METRIC_NAME]["metric"].output)

            # II. Metadata sufficiency
            output_file.write(experiment_metrics[source_id][MS_METRIC_NAME]["metric"].output)

            # III. Text record counts to control records

            # a. Individual editions vs. ur edition
            for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
                output_file.write(experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].output)

            # b. Overall text record counts to control record of all editions from this source
            output_file.write(experiment_metrics[source_id][TR_METRIC_NAME]["overall"]["metric"].output)

            # c. Overall data quality measurement of the source_id editions vs. ur edition
            output_file.write(f"Overall Quality:,{experiment_metrics[source_id]["overall_data_quality"]}\n")

        # C. Ur edition

        # I. Lexical validity
        output_file.write(ur_metrics[UR_EDITION][LV_METRIC_NAME]["metric"].output)

        # II. Metadata sufficiency
        output_file.write(ur_metrics[UR_EDITION][MS_METRIC_NAME]["metric"].output)

        # III. Text record counts to control records

        # a. Overall text record counts to control record of all editions from this source
        output_file.write(ur_metrics[UR_EDITION][TR_METRIC_NAME]["metric"].output)

        # b. Overall data quality measurement of the source_id editions vs. ur edition
        output_file.write(f"Overall Quality:,{ur_metrics[UR_EDITION]["overall_data_quality"]}\n")

def output_record_count_chapter_results(p_output_filepath):

    results_lines = []

    for source_id in aolm_data_reading.huckfinn_source_fullnames:

        # Skip ur edition
        if UR_EDITION == source_id:
            continue

        get_header = True

        for edition_name in aolm_data_reading.huckfinn_edition_names[source_id]:
            results_lines.append(experiment_metrics[source_id][TR_METRIC_NAME]["individual_editions"][edition_name]["metric"].results_full_counts(get_header))
            if get_header:
                get_header = False

    with open(p_output_filepath, "w") as output_file:
        for line_set in results_lines:
            output_file.write(f"{"\n".join(line_set)}\n")

def output_amalgamated_edition(p_results_filepath, p_ur_chapter_count):

    class BestChapterInstance:

        def __init__(self, p_count_type, p_chapter_number, p_count, p_edition_name):

            self.m_count_type = p_count_type
            self.m_chapter_number = p_chapter_number
            self.m_count = p_count
            self.m_edition_name = p_edition_name

        @property
        def count_type(self):
            return self.m_count_type
        @count_type.setter
        def count_type(self, p_count_type):
            self.m_count_type = p_count_type
        @property
        def chapter_number(self):
            return self.m_chapter_number
        @chapter_number.setter
        def chapter_number(self, p_chapter_number):
            self.m_chapter_number = p_chapter_number
        @property
        def count(self):
            return self.m_count
        @count.setter
        def count(self, p_count):
            self.m_count = p_count
        @property
        def edition_name(self):
            return self.m_edition_name
        @edition_name.setter
        def edition_name(self, p_edition_name):
            self.m_edition_name = p_edition_name                     
    
    with open(p_results_filepath, "r") as results_file:
    
        csv_reader = csv.DictReader(results_file)

        best_sentence_dict = { str(index): BestChapterInstance("sentence", str(index), 0, "") for index in range(1, p_ur_chapter_count + 1) }
        best_word_dict = { str(index): BestChapterInstance("word", str(index), 0, "") for index in range(1, p_ur_chapter_count + 1) }
    
        for row in csv_reader:

            if "edition_name" == row["edition_name"]:
                continue

            # edition_name,chapter_name,count_type,count
            edition_name = row["edition_name"]
            chapter_name = row["chapter_name"]
            count_type = row["count_type"]
            count = float(row["count"])

            # Isolate the best chapters according to the most accurate sentence count
            if count_type == "sentences" and count > best_sentence_dict[chapter_name].count:
                best_sentence_dict[chapter_name].edition_name = edition_name
                best_sentence_dict[chapter_name].chapter_name = chapter_name
                best_sentence_dict[chapter_name].count_type = count_type
                best_sentence_dict[chapter_name].count = count

            # Isolate the best chapters according to the most accurate word count
            if count_type == "words" and count > best_word_dict[chapter_name].count:
                best_word_dict[chapter_name].edition_name = edition_name
                best_word_dict[chapter_name].chapter_name = chapter_name
                best_word_dict[chapter_name].count_type = count_type
                best_word_dict[chapter_name].count = count            

    # Merge the two calculation results to create a best chapters list
    output_filepath = p_results_filepath[0:p_results_filepath.find(".")] + "_amalgam.csv"
    with open(output_filepath, "w") as output_file:

        output_file.write("count_type,chapter_name,edition_name,count\n")

        for index in range(1, p_ur_chapter_count + 1):
            chapter_name = str(index)
            output_file.write(f"{best_sentence_dict[chapter_name].count_type},{chapter_name},{best_sentence_dict[chapter_name].edition_name},{best_sentence_dict[chapter_name].count}\n")

        for index in range(1, p_ur_chapter_count + 1):
            chapter_name = str(index)
            output_file.write(f"{best_word_dict[chapter_name].count_type},{chapter_name},{best_word_dict[chapter_name].edition_name},{best_word_dict[chapter_name].count}\n")            

# Visualization

def plot_heatmap(p_chart_title, p_metric_name, p_data):

    import numpy as np
    import matplotlib.pyplot as plt    

    # Editions of the novel
    editions = list(p_data.keys())
    n_editions = len(editions)
    n_chapters = len(p_data[editions[0]])

    # Fill in data
    data = np.zeros((n_editions, n_chapters))
    for index in range(n_editions):
        for index2 in range(n_chapters):
            data[index, index2] = p_data[editions[index]][index2]

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(data, aspect='auto')

    # Set axis labels
    ax.set_xticks(np.arange(n_chapters))
    ax.set_xticklabels(np.arange(1, n_chapters + 1))
    ax.set_yticks(np.arange(n_editions))
    ax.set_yticklabels(editions)

    # Rotate x-axis labels for readability
    plt.setp(ax.get_xticklabels(), rotation=90, ha="center")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(p_metric_name)

    ax.set_title(p_chart_title)
    ax.set_xlabel("Chapter")
    ax.set_ylabel("Edition")

    plt.tight_layout()
    plt.show()

def plot_results(p_results_filepath, p_ur_chapter_count):

    # 1. Store all edition record count to control records results for sentences and words by chapter
    editions = {}
    with open(p_results_filepath, "r") as results_file:
    
        csv_reader = csv.DictReader(results_file)

        for row in csv_reader:

            # Skip header
            if "edition_name" == row["edition_name"]:
                continue

            # edition_name,chapter_name,count_type,count
            edition_name = row["edition_name"]
            chapter_name = row["chapter_name"]
            count_type = row["count_type"]
            count = float(row["count"])

            if edition_name not in editions:
                editions[edition_name] = {
                    "sentences": [0] * p_ur_chapter_count,
                    "words": [0] * p_ur_chapter_count
                }

            editions[edition_name][count_type][int(chapter_name) - 1] = count

        # 2. Plot a 2D heatmap of the chapters of each edition by sentence data quality
        # plot_heatmap(
        #     "Sentence Quality by Chapter in Editions of 'Adventures of Huckleberry Finn'",
        #     "Record counts to control records data quality",
        #     { edition_name: editions[edition_name]["sentences"] for edition_name in editions }
        # )
            
        plot_heatmap(
            "Word Quality by Chapter in Editions of 'Adventures of Huckleberry Finn'",
            "Record counts to control records data quality",
            { edition_name: editions[edition_name]["words"] for edition_name in editions }
        )


def main():

    # Experiment Description

    # Sources of Adventures of Huckleberry Finn by Mark Twain:
    # (1) Internet Archive
    # (2) Project Gutenberg edition
    # versus
    # (3) Mark Twain Project Online

    # Data quality metrics considered:
    # (A) Record Counts to Control Records (recordcounts_to_controlrecords.py)

    process_results = False
    graph = False
    results_filepath = "/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/huckfinn_dq_experiment2_full_results_29082025_192728.csv"
    ur_chapter_count = 43
    if graph:
        plot_results(results_filepath, ur_chapter_count)
    elif process_results:
        output_amalgamated_edition(results_filepath, ur_chapter_count)
        return True

    # 0. Setup

    # Run time saved for output file
    script_run_time = datetime.now().strftime("%d%m%Y_%H%M%S")

    # 1. Read dataset
    print_debug_header("Reading datasets")
    read_texts()

    # 2. Read dataset(s)/Compute metrics
    print_debug_header("Computing data quality metrics")
    compute_metrics()

    # 3. Evaluate (submetrics and overall metrics)
    print_debug_header("Evaluating data quality metric results")
    evaluate_metrics()

    # 4. Run data quality metrics over ur edition
    # NOTE: Since some metrics require comparison against ur edition
    # so if that's the case the ur edition would naturally get 100% for that metric

    # NOTE: For ur edition lexical compute needs to access aolm_text.body.values() differently
    print_debug_header(f"Computing data quality for {aolm_data_reading.MTPO} ur edition of {WORK_TITLE} and evaluating results")
    # read_texts()
    compute_and_evaluate_ur_edition()        

    # 5. Output record counts to control records results for chapter by chapter breakdown
    print_debug_header(f"Outputting {TR_METRIC_NAME} chapter by chapter results")
    output_filepath = f"/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/huckfinn_dq_experiment2_full_results_{script_run_time}.csv"
    output_record_count_chapter_results(output_filepath)


if "__main__" == __name__:

    main()









