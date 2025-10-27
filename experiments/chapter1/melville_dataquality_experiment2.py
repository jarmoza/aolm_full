# Author: Jonathan Armoza
# Created: July 7, 2025
# Purpose: Measure the data quality of Melville's works in terms of n-legomena

# Imports

# Built-ins

import glob
from math import ceil
import os
import re
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

publication_order = [

    ("typee", 1846),
    ("omoo", 1847),
    ("mardi", 1849),
    ("redburn", 1849),
    ("white_jacket", 1850),
    ("moby_dick", 1851),
    ("pierre", 1852),
    ("israel_potter", 1855),
    ("confidence_man", 1857)
]
publication_rank = { title: index for index, (title, year) in enumerate(publication_order) }
label_to_novel = {}


# Utility functions

def plot_novel_words():

    import plotly.express as px

    # Data
    novels = [
        "Typee", "Omoo", "Mardi Vol. 1", "Mardi Vol. 2", "Redburn",
        "White-Jacket", "Moby-Dick", "Pierre", "Israel Potter", "The Confidence-Man"
    ]

    words_in_body_text = [106775, 101141, 96024, 100194, 117915, 138171, 212131, 151731, 64483, 92840]

    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame({
        "Novel": novels,
        "Words in Body Text": words_in_body_text
    })

    # Simple bar chart
    fig = px.bar(
        df,
        x="Novel",
        y="Words in Body Text",
        title="Words in Body Text Across Melville Novels",
        labels={"Words in Body Text": "Words in Body Text", "Novel": "Novel"},
        text="Words in Body Text"
    )

    # Increase font sizes
    fig.update_traces(textfont_size=16)
    fig.update_layout(
        title_font=dict(size=22),
        xaxis=dict(title_font=dict(size=20), tickfont=dict(size=16)),
        yaxis=dict(title_font=dict(size=20), tickfont=dict(size=16))
    )

    fig.show()


def plot_chapter_count_and_words():

    import pandas as pd
    import plotly.graph_objects as go

    # Data
    data = {
        "Name": [
            "Typee", "Omoo", "Mardi Vol. 1", "Mardi Vol. 2", "Redburn",
            "White-Jacket", "Moby-Dick", "Pierre", "Israel Potter", "The Confidence-Man"
        ],
        "Chapter Count": [35, 82, 104, 91, 62, 93, 150, 114, 27, 46],
        "Avg. Chapter Words": [3051, 1234, 923, 1101, 1902, 1485, 1414, 1331, 2388, 2018]
    }

    df = pd.DataFrame(data)

    # Create figure
    fig = go.Figure()

    # Bar trace: Chapter Count
    fig.add_trace(
        go.Bar(
            x=df["Name"],
            y=df["Chapter Count"],
            name="Chapter Count",
            marker_color="lightblue"
        )
    )

    # Line trace: Avg. Chapter Words
    fig.add_trace(
        go.Scatter(
            x=df["Name"],
            y=df["Avg. Chapter Words"],
            name="Avg. Chapter Words",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="red", width=3),
            marker=dict(size=8)
        )
    )

    # Layout with secondary y-axis

    # Layout with larger fonts
    fig.update_layout(
        title="Melville Novels: Chapter Count vs. Average Chapter Words",
        xaxis=dict(
            title="Novel",
            title_font=dict(size=20),
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            title="Chapter Count",
            title_font=dict(size=20),
            tickfont=dict(size=16)
        ),
        yaxis2=dict(
            title="Avg. Chapter Words",
            title_font=dict(size=20),
            tickfont=dict(size=16),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.05, y=0.95, font=dict(size=16)),
        bargap=0.4
    )


    fig.show()


def extract_sort_key(p_label):

    novel_name = label_to_novel.get(p_label, "")
    
    # Volume number
    vol_match = re.search(r"vol\. (\d+)", p_label)
    volume = int(vol_match.group(1)) if vol_match else 0

    # Rank from publication order
    rank = publication_rank.get(novel_name, 999)

    return (rank, volume)

def plot_counts_bar_chart(p_labels, p_counts, p_title):

    df = pd.DataFrame({"Novel": p_labels, "Token Count": p_counts})
    fig = px.bar(df, x="Novel", y="Token Count",
                 title=p_title,
                 labels={"Token Count": "Token Count", "Novel": "Novel"},
                 text="Token Count")
    
    # Increase x-axis tick label font size
    fig.update_xaxes(tickfont=dict(size=16))  # x-axis labels
    fig.update_yaxes(tickfont=dict(size=16))  # y-axis labels (optional)

    # Increase font size of the text labels on bars
    fig.update_traces(textfont=dict(size=14, color='black'))  # adjust size and color

    # Optionally move bar text above bars
    fig.update_traces(textposition='outside')

    fig.update_traces(marker_color="indigo", textposition="outside")
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

# Main script

def main():

    # plot_chapter_count_and_words()
    plot_novel_words()
    if True:
        return

    # 0. Setup
    source_path = aolm_data_reading.melville_source_directory["collected"] + f"demarcated{os.sep}"
    demarcated_files = [filepath for filepath in glob.glob(source_path + "*.json")]
    plot_avg_chapter_legomena = True

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

    # Build a label dictionary between graph label and filepath (accounting for the 2 volume Mardi)
    legomena_label_dict = {}
    for filepath in demarcated_files:
        novel_name = file_to_novel_name_dict[filepath]
        publication_date = melville_novel_publication_dates[novel_name]
        label = f"{novel_name} ({publication_date})"
        if label in legomena_label_dict:
            label = f"{novel_name} vol. 2 ({publication_date})"
        legomena_label_dict[label] = filepath
    legomena_label_dict["mardi vol. 1 (1849)"] = legomena_label_dict["mardi (1849)"]
    del legomena_label_dict["mardi (1849)"]

    for label, filepath in legomena_label_dict.items():
        label_to_novel[label] = file_to_novel_name_dict[filepath].lower()    

    # Build tuple list for graph data
    if plot_avg_chapter_legomena:
        graph_data = sorted(
            [(label, avg_chapter_legomena_for_works[filepath]) for label, filepath in legomena_label_dict.items()],
            key=lambda x: extract_sort_key(x[0])
        )
        graph_title = "Average Hapax per Chapter in the Novels of Herman Melville"
    # Plot total legomena for the works instead
    else:
        graph_data = sorted(
            [(label, legomena_totals_for_works[filepath]) for label, filepath in legomena_label_dict.items()],
            key=lambda x: extract_sort_key(x[0])
        )
        graph_title = "Total Hapax in the Novels of Herman Melville"

    label_list, value_list = zip(*graph_data)
    label_list = list(label_list)   # ['Typee (1846)', 'Omoo (1847)']
    value_list = list(value_list)   # [12, 15]

    plot_counts_bar_chart(label_list, value_list, graph_title)


if "__main__" == __name__:
    main()

