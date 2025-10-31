# Author: Jonathan Armoza
# Created: May 19, 2025
# Purpose: Measure the data quality of Melville's works in terms of presence of authorial signature

# Imports

# Built-ins

import glob
import os
import re
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom

import aolm_data_reading
from aolm_utilities import bar_plot
from dq_metrics.dataset_signature.authorial_signature import DatasetSignature_AuthorialSignature


# Globals

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


# Helper functions

def extract_sort_key(label):
    """
    Computes a sort key for sorting novels by publication order and volume.
    Keeps the year in parentheses in the label for plotting.
    """
    # Remove year in parentheses for ranking only
    base_name = re.sub(r"\s*\(.*\)", "", label).strip().lower()

    # Map volumes back to main novel for ranking
    if "mardi" in base_name:
        rank_name = "mardi"
    elif "white_jacket" in base_name or "white-jacket" in base_name:
        rank_name = "white_jacket"
    elif "moby_dick" in base_name or "moby-dick" in base_name:
        rank_name = "moby_dick"
    elif "israel_potter" in base_name:
        rank_name = "israel_potter"
    elif "confidence-man" in base_name or "confidence_man" in base_name:
        rank_name = "confidence_man"
    else:
        rank_name = base_name.replace("-", "_").replace(" ", "_")

    # Publication rank
    rank = publication_rank.get(rank_name, 999)

    # Volume number if present
    vol_match = re.search(r"vol\. (\d+)", base_name, re.IGNORECASE)
    volume = int(vol_match.group(1)) if vol_match else 0

    return (rank, volume)

def sort_novels_by_publication(labels, values):
    """
    Sort novels and metric values by publication order + volume.
    Keeps the year in labels.
    """
    paired = list(zip(labels, values))
    paired_sorted = sorted(paired, key=lambda x: extract_sort_key(x[0]))
    sorted_labels, sorted_values = zip(*paired_sorted)
    return list(sorted_labels), list(sorted_values)


# Main script

def main():

    # 0. Setup
    source_path = aolm_data_reading.melville_source_directory["collected"] + f"body_text{os.sep}"
    source_files = [filepath for filepath in glob.glob(source_path + "*.txt")]

    # 1. Calculate the author's signature
    signature_metric = DatasetSignature_AuthorialSignature(source_files)
    signature_metric.compute()

    # 2. Evaluate the source files' signatures against the average author signature
    signature_metric.evaluate()
    
    # 3. Output and visualizations

    # A. Superlatives
    print(f"Most Melvillian text: {signature_metric.most_like_author_signature}")
    print(f"Least Melvillian text: {signature_metric.least_like_author_signature}")

    # B. All source texts ranked by signature distance
    source_signature_distances = signature_metric.signature_distances

    # C. Build label/value lists with years in labels
    labels = []
    values = []
    for signature in source_signature_distances:

        filename = os.path.basename(signature[0])
        base_title = aolm_data_reading.melville_filename_to_title[filename]  # e.g., "Mardi Vol. 1"
        
        # Map back to lowercase main title for year lookup
        key = base_title.lower().replace("-", "_").replace(" ", "_")
        if "mardi" in key:
            key = "mardi"
        elif key == "white_jacket":
            key = "white_jacket"
        elif key == "moby_dick":
            key = "moby_dick"
        elif key == "israel_potter":
            key = "israel_potter"
        elif "confidence" in key:
            key = "confidence_man"

        year = melville_novel_publication_dates.get(key, "")
        labels.append(f"{base_title} ({year})")
        values.append(float(signature[1]))


    # D. Convert to labels and values ---
    # labels = [aolm_data_reading.melville_filename_to_title[os.path.basename(sig[0])] for sig in source_signature_distances]
    # values = [float(sig[1]) for sig in source_signature_distances]

    # E. Sort by publication order (handles Mardi volumes automatically) ---
    sorted_labels, sorted_values = sort_novels_by_publication(labels, values)

    # F. Print the sorted distances
    print("Text distance from author signature ranked by publication order:")
    for idx, (label, value) in enumerate(zip(sorted_labels, sorted_values), start=1):
        print(f"#{idx}. {label}: {value:.4f}")

    # G. Plot the sorted distances
    bar_plot(
        sorted_labels,
        "Title",
        sorted_values,
        "Distance",
        "Distance from Melville's Authorial Signature [0,1]"
    )


if "__main__" == __name__:
    main()