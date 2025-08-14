# Author: Jonathan Armoza
# Created: July 7, 2025
# Purpose: Measure the data quality of Melville's works in terms of n-legomena

# Imports

# Built-ins

import glob
from math import ceil
import os
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Third party

import plotly.express as px
import pandas as pd

# Custom

import aolm_data_reading
from aolm_utilities import bar_plot
from pg_melville_reader import PGMelvilleReader
from dq_metrics.dataset_signature.legomena import DatasetSignature_Legomena


# Globals

# Produce comparison visualization
melville_novel_publication_dates = {

    "typee": 1846,
    "omoo": 1847,
    "mardi": 1849,
    "redburn": 1849,
    "white_jacket": 1850,
    "moby_dick": 1851,
    "pierre": 1852,
    "israel_potter": 1855,
    "confidence_man": 1857
}

# Utility functions

def plot_counts_bar_chart(p_labels, p_counts, p_title):

    df = pd.DataFrame({"Novel": p_labels, "Token Count": p_counts})
    fig = px.bar(df, x="Novel", y="Token Count",
                 title=p_title,
                 labels={"Token Count": "Token Count", "Novel": "Novel"},
                 text="Token Count")
    fig.update_traces(marker_color="indigo", textposition="outside")
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

# Main script

def main():

    # 0. Setup
    source_path = aolm_data_reading.melville_source_directory["collected"] + f"demarcated{os.sep}"
    demarcated_files = [filepath for filepath in glob.glob(source_path + "*.json")]

    # Read each Melville novel into memory
    readers = [PGMelvilleReader(filepath) for filepath in demarcated_files]

    # 1. Measure legomena by work and by chapter
    dq_metric = DatasetSignature_Legomena(readers)
    dq_metric.compute()
    dq_metric.evaluate()

    # 2. Output evaluations and metrics to csv
    experiment_output_directory = f"{os.getcwd()}{os.sep}experiments{os.sep}outputs{os.sep}"
    output_filepath = f"{experiment_output_directory}melville_novels_legomena_metric.csv"
    dq_metric.to_csv(output_filepath)

    # 3. Data visualization

    # Associate text files with novel names (and implicitly publication dates)
    file_to_novel_name_dict = { filepath: None for filepath in demarcated_files }
    
    for filepath in file_to_novel_name_dict:
        for novel_name in melville_novel_publication_dates:
            if novel_name in filepath:
                file_to_novel_name_dict[filepath] = novel_name
                break

    # Evaluations
    avg_chapter_legomena_for_works = { filepath: ceil(dq_metric.avg_chapter_legomena_for_work(filepath)) for filepath in dq_metric.filepaths }
    legomena_totals_for_works = { filepath: dq_metric.legomena_total_for_work(filepath) for filepath in dq_metric.filepaths }
    avg_legomena_count = dq_metric.avg_legomena_count

    legomena_list = []

    for filepath in demarcated_files:

        novel_name = file_to_novel_name_dict[filepath]
        publication_date = melville_novel_publication_dates[novel_name]
        label = f"{novel_name} ({publication_date})"
        if label in legomena_list:
            label = f"{novel_name} vol. 2 ({publication_date})"
        legomena_list.append(label)

    plot_counts_bar_chart(legomena_list, avg_chapter_legomena_for_works.values(), "Average Hapax per Chapter in the Novels of Herman Melville")


if "__main__" == __name__:
    main()

