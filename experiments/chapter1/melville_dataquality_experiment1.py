# Author: Jonathan Armoza
# Created: May 19, 2025
# Purpose: Measure the data quality of Melville's works in terms of presence of authorial signature

# Imports

# Built-ins

import glob
import os
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
    print("Text distance from author signature ranked (least to most)")
    source_signature_distances = signature_metric.signature_distances
    for index in range(len(source_signature_distances)):
        print(f"#{index + 1}. {source_signature_distances[index][0]}: {source_signature_distances[index][1]}")

    # Plot the ranked distances
    bar_plot(
        [aolm_data_reading.melville_filename_to_title[sig_dist[0]] for sig_dist in source_signature_distances],
        "Title",
        [1 - float(sig_dist[1]) for sig_dist in source_signature_distances],
        "Distance",
        "Distance from Melville's Authorial Signature [0,1]"
    )

if "__main__" == __name__:
    main()