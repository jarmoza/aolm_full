# Author: Jonathan Armoza
# Created: October 28, 2025
# Purpose: Measure the consensus of editions of Twain's 'Adventures of Huckleberry Finn'

# Imports

# Built-ins
import os
import sys
from collections import Counter
from math import ceil
from statistics import mean, median

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom
import aolm_data_reading
from aolm_textutilities import AOLMTextUtilities
from aolm_utilities import print_debug_header
from dq_metric import DataQualityMetric
from dq_metrics.dataset_consistency.consistency_recordconsensus import DatasetConsistency_RecordConsensus

# Globals

EXPERIMENT_PATH = ROOT_DIR + f"{os.sep}experiments{os.sep}outputs{os.sep}"

# Helpers

def get_edition_shortname_from_metadata(p_text_json_filename):

    import json

    short_name = p_text_json_filename

    with open("/Users/weirdbeard/Documents/school/aolm_full/experiments/chapter1/huckfinneditions_filenames2fullnames.json", "r") as input_file:
        json_data = json.load(input_file)

    for key in json_data:
        if key in p_text_json_filename:
            short_name = json_data[key]["short_name"]
            break

    return short_name

def get_publication_year(p_edition_short_name):

    publication_year = ""

    if "gutenberg" in p_edition_short_name:
        publication_year = p_edition_short_name[p_edition_short_name.rfind("_") + 1:]
    else:
        for index in range(0, len(p_edition_short_name)):
            if p_edition_short_name[index].isdigit():
                publication_year = p_edition_short_name[index:index + p_edition_short_name[index:].find("_")]
                break

    return publication_year


# Test script visualization

def plot_heatmap(p_chart_title, p_metric_name, p_data):

    import numpy as np
    import matplotlib.pyplot as plt    

    # Editions of the novel (sorted by publication year)
    editions = list(p_data.keys())
    editions = [(get_publication_year(edition_short_name), edition_short_name) for edition_short_name in editions]
    editions.sort(key=lambda x: x[0])
    editions = [edition_tuple[1] for edition_tuple in editions]
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

def plot_results(p_results_filepath, p_ur_chapter_count, p_count_type, p_count_column):

    import csv

    # 1. Store all edition record count to control records results for sentences and words by chapter
    editions = {}
    with open(p_results_filepath, "r") as results_file:
    
        csv_reader = csv.DictReader(results_file)

        for row in csv_reader:

            # Skip header
            if "edition_name" == row["edition_name"]:
                continue

            # edition_name,chapter_name,count_type,count
            edition_name = get_edition_shortname_from_metadata(row["edition_name"])
            chapter_name = row["chapter"]
            count_type = p_count_type
            count = float(row[p_count_column])

            if edition_name not in editions:
                editions[edition_name] = {
                    "sentences": [0] * p_ur_chapter_count,
                    "words": [0] * p_ur_chapter_count
                }

            editions[edition_name][count_type][int(chapter_name) - 1] = count

        # 2. Plot a 2D heatmap of the chapters of each edition by sentence data quality
        if "sentences" == p_count_type:
            plot_heatmap(
                "Mean Sentence Variance by Chapter in Internet Archive Editions of 'Adventures of Huckleberry Finn'",
                "Record Consistency data quality",
                { edition_name: editions[edition_name]["sentences"] for edition_name in editions }
            )
        elif "words" == p_count_type:  
            plot_heatmap(
                "Mean Word Varianbce by Chapter in Internet Archive Editions of 'Adventures of Huckleberry Finn'",
                "Record consistency data quality",
                { edition_name: editions[edition_name]["words"] for edition_name in editions }
            )


# Main script

def main():

    plot_data = True
    if plot_data:

        plot_results(EXPERIMENT_PATH + "huckfinn_pgiamtpo_subx4metric.csv", 43, "words", "variance_from_word_consensus__by_chapter")
        # plot_results(EXPERIMENT_PATH + "huckfinn_pgiamtpo_subx4metric.csv", 43, "sentences", "variance_from_sentence_consensus__by_chapter")

        return

    # Experiment: Word and Sentence consensus across 
    # Internet Archive, Project Gutenberg, and Mark Twain Project Online
    # editions of 'Adventures of Huckleberry Finn'

    COLLECTION_IDS = [aolm_data_reading.PG, aolm_data_reading.IA, aolm_data_reading.MTPO]
    COLLECTION_FULL_NAMES = { id: aolm_data_reading.huckfinn_source_fullnames[id] for id in COLLECTION_IDS }
    EDITION_PATHS = { id: aolm_data_reading.huckfinn_directories[id]["txt"] for id in COLLECTION_IDS }
    WORK_TITLE = "Adventures of Huckleberry Finn"
    
    # 1. Read in all Huckleberry finn editions from Internet Archive
    print_debug_header(f"Reading editions of {WORK_TITLE}...")
    huckfinn_textdata = { id: aolm_data_reading.read_huckfinn_text(id) for id in COLLECTION_IDS }

    # 2. Compute metric
    print_debug_header(f"Computing record consensus metric for collections...")
    huckfinn_recordconsensus = DatasetConsistency_RecordConsensus(
        f"HuckFinn_PG_IA_MTPO_Consistency_RecordConsensus",
        {reader_name: huckfinn_textdata[id][reader_name] for id in huckfinn_textdata for reader_name in huckfinn_textdata[id]},
        "PG_IA_MTPO",
        WORK_TITLE,
        "_".join([aolm_data_reading.huckfinn_source_fullnames[id] for id in COLLECTION_IDS]),
        EDITION_PATHS)
    huckfinn_recordconsensus.consistency_threshold = 0.5
    huckfinn_recordconsensus.compute()
    
    # 3. Evaluate the results
    print_debug_header("Evaluating metric results...")
    huckfinn_recordconsensus.evaluate()

    # 4. Output the metric evaluations
    print(f"Metric: {100 * huckfinn_recordconsensus.metric_evaluation}%")
    print(f"Submetrics: {huckfinn_recordconsensus.m_evaluations["submetric"]}")

    output_lines = huckfinn_recordconsensus.__build_eval_output_line__()
    with open(EXPERIMENT_PATH + "huckfinn_pgiamtpo_subx4metric.csv", "w") as output_file:
        for line in output_lines:
            output_file.write(line)    


if "__main__" == __name__:
    main()

