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
    from matplotlib import colors  

    # Editions of the novel (sorted by publication year)
    editions = list(p_data.keys())
    editions = [(get_publication_year(edition_short_name), edition_short_name) for edition_short_name in editions]
    editions.sort(key=lambda x: x[0])
    editions = [edition_tuple[1] for edition_tuple in editions]
    n_editions = len(editions)
    
    # Determine the maximum number of chapters across all editions
    n_chapters = max(len(chapter_list) for chapter_list in p_data.values())

    # Fill in data and mask for missing chapters
    data = np.zeros((n_editions, n_chapters))
    mask = np.zeros((n_editions, n_chapters), dtype=bool)

    for index, edition in enumerate(editions):
        for index2 in range(n_chapters):
            value = p_data[edition][index2] if index2 < len(p_data[edition]) else None
            if value is None:
                mask[index, index2] = True
                data[index, index2] = 0
            else:
                data[index, index2] = value

    # Create colormap: numeric values → e.g., viridis; masked → black
    cmap = plt.cm.viridis
    cmap.set_bad(color="black")

    # Masked array
    data_masked = np.ma.array(data, mask=mask)    

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(data_masked, aspect="auto", cmap=cmap)

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

    # Add a small legend patch for missing chapters (black rectangles)
    # import matplotlib.patches as mpatches
    # missing_patch = mpatches.Patch(color="black", label="Missing chapter")
    # cbar.ax.legend(
    #     handles=[missing_patch],
    #     loc="lower right",
    #     frameon=False,
    #     fontsize=8
    # )   

    ax.set_title(p_chart_title)
    ax.set_xlabel("Chapter")
    ax.set_ylabel("Edition")

    plt.tight_layout()
    plt.show()

def plot_heatmap_version2(p_chart_title, p_metric_name, p_data):
    
    import numpy as np
    import matplotlib.pyplot as plt
    import math
    from matplotlib import colors
    import matplotlib.patches as mpatches

    # Editions of the novel (sorted by publication year)
    editions = list(p_data.keys())
    editions = [(get_publication_year(edition_short_name), edition_short_name) for edition_short_name in editions]
    editions.sort(key=lambda x: x[0])
    editions = [edition_tuple[1] for edition_tuple in editions]
    n_editions = len(editions)

    # Determine the maximum number of chapters across all editions (handles lists of unequal length)
    # p_data[edition] is assumed to be a list-like of length = number of chapters present
    n_chapters = max(len(v) for v in p_data.values()) if p_data else 0
    if n_chapters == 0:
        raise ValueError("p_data appears empty or contains no chapters.")

    # Prepare arrays
    data = np.zeros((n_editions, n_chapters), dtype=float)
    mask = np.zeros((n_editions, n_chapters), dtype=bool)

    # Fill arrays and build mask. Treat as missing if:
    #  - the edition list is shorter than the chapter index
    #  - the value is None
    #  - the value is NaN
    for i, edition in enumerate(editions):
        edition_list = p_data.get(edition, [])
        for j in range(n_chapters):
            if j >= len(edition_list):
                # absent because the list is too short
                mask[i, j] = True
                data[i, j] = 0.0
            else:
                val = edition_list[j]
                # treat None or NaN as missing
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    mask[i, j] = True
                    data[i, j] = 0.0
                else:
                    try:
                        data[i, j] = float(val)
                    except Exception:
                        # if conversion fails, mark as missing
                        mask[i, j] = True
                        data[i, j] = 0.0

    # Diagnostic printouts to help debugging
    total_masked = int(mask.sum())
    print(f"Heatmap diagnostic: {total_masked} masked cells out of {n_editions * n_chapters} total.")
    if total_masked:
        # show up to first 10 masked coordinates
        coords = list(zip(*np.where(mask)))
        shown = coords[:10]
        print("Sample masked coordinates (edition_index, chapter_index):", shown)
        # map edition indices to names for the sample
        print("Sample masked (edition_name, chapter_number):",
              [(editions[r], c + 1) for (r, c) in shown])

    # Create colormap and ensure masked (bad) color is black
    cmap = plt.cm.viridis
    # Make a copy of the colormap to avoid modifying the global colormap unexpectedly
    cmap = cmap.copy()
    cmap.set_bad(color='black')

    # Create masked array
    data_masked = np.ma.array(data, mask=mask)

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(data_masked, aspect='auto', cmap=cmap)

    # Set axis labels
    ax.set_xticks(np.arange(n_chapters))
    ax.set_xticklabels(np.arange(1, n_chapters + 1))
    ax.set_yticks(np.arange(n_editions))
    ax.set_yticklabels(editions)

    # Rotate x-axis labels for readability
    plt.setp(ax.get_xticklabels(), rotation=90, ha="center")

    # Add colorbar and label
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(p_metric_name)

    # Add a small legend patch for missing chapters (black rectangles) inside the colorbar
    missing_patch = mpatches.Patch(color="black", label="Missing chapter")
    # Put the legend just under the colorbar ticks, inside the colorbar axis
    cbar.ax.legend(handles=[missing_patch], loc='upper right', frameon=False, fontsize=8)

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
                    "sentences": [None] * p_ur_chapter_count,
                    "words": [None] * p_ur_chapter_count
                }

            editions[edition_name][count_type][int(chapter_name) - 1] = count

        # 2. Plot a 2D heatmap of the chapters of each edition by sentence data quality
        if "sentences" == p_count_type:
            plot_heatmap(
                "Mean Sentence Variance by Chapter in Internet Archive Editions of 'Adventures of Huckleberry Finn'",
                "Record Consensus data quality",
                { edition_name: editions[edition_name]["sentences"] for edition_name in editions }
            )
        elif "words" == p_count_type:  
            plot_heatmap(
                "Mean Word Variance by Chapter in Internet Archive Editions of 'Adventures of Huckleberry Finn'",
                "Record Consensus data quality",
                { edition_name: editions[edition_name]["words"] for edition_name in editions }
            )


# Main script

def main():

    plot_data = True
    if plot_data:

        # plot_results(EXPERIMENT_PATH + "huckfinn_pgiamtpo_subx4metric_variancetest.csv", 43, "sentences", "variance_from_sentence_consensus__by_chapter")
        plot_results(EXPERIMENT_PATH + "huckfinn_pgiamtpo_subx4metric_variancetest.csv", 43, "words", "variance_from_word_consensus__by_chapter")

        # plot_results(EXPERIMENT_PATH + "huckfinn_pgiamtpo_subx4metric.csv", 43, "words", "variance_from_word_consensus__by_chapter")
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

    output_csv_toggle = True
    # csv_filename = "huckfinn_pgiamtpo_subx4metric.csv"
    csv_filename = "huckfinn_pgiamtpo_subx4metric_variancetest.csv"
    if output_csv_toggle:
        output_lines = huckfinn_recordconsensus.__build_eval_output_line__()
        with open(EXPERIMENT_PATH + csv_filename, "w") as output_file:
            for line in output_lines:
                output_file.write(line)    


if "__main__" == __name__:
    main()

