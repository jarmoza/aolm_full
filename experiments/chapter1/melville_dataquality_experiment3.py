# Author: Jonathan Armoza
# Created: April 23, 2026
# Purpose: 
# (1) Compare the authorial signatures of the Project Gutenberg Melville and Internet Archive Melville corpora
# (2) Plot that corpora distance compared to the distances between individual PG texts and the corpus signature
# (3) Compute the lexica validity of each corpus

# Imports

# Built-ins

import glob
from math import ceil
import os
import re
import sys
from statistics import mean

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Third party

import numpy as np
import plotly.express as px
import pandas as pd

# Custom

import aolm_data_reading
from aolm_utilities import bar_plot
from pg_melville_reader import PGMelvilleReader
from dq_metrics.dataset_signature.authorial_signature import DatasetSignature_AuthorialSignature
from dq_metrics.dataset_signature.legomena import DatasetSignature_Legomena
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity, read_coha


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

def get_distance_between_signature_vectors(p_signature1, p_signature2):

    # 1. Build a shared vocabulary across both signatures
    shared_vocabulary = sorted(set(p_signature1.keys()) | set(p_signature2.keys()))

    # 2. Transform each signature dict into a vector over that shared vocabulary
    signature1_vector = np.array(
        [p_signature1.get(word, 0.0) for word in shared_vocabulary],
        dtype=float
    )
    signature2_vector = np.array(
        [p_signature2.get(word, 0.0) for word in shared_vocabulary],
        dtype=float
    )

    # 3. Compute cosine distance safely
    norm1 = np.linalg.norm(signature1_vector)
    norm2 = np.linalg.norm(signature2_vector)

    if norm1 == 0 or norm2 == 0:
        raise ValueError("One of the signature vectors has zero magnitude.")

    cosine_similarity = np.dot(signature1_vector, signature2_vector) / (norm1 * norm2)
    cosine_distance = 1 - cosine_similarity

    return cosine_distance

def get_file_text(p_source_filepath):
    with open(p_source_filepath, "r") as input_file:
        body_text = input_file.read()
    return body_text

def plot_pg_distances_plus_pg2ia_distance(p_pg2ia_distance):

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

    # I. Add inter-corpus distance for plotting
    sorted_labels.append("PG-IA distance")
    sorted_values.append(p_pg2ia_distance)

    # II. Add a new color for the inter-corpus distance
    colors = ["steelblue"] * (len(sorted_values) - 1) + ["#F58518"]

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
        "Distance from Melville's Authorial Signature [0,1]",
        colors=colors
    )

def sort_novels_by_publication(labels, values):
    """
    Sort novels and metric values by publication order + volume.
    Keeps the year in labels.
    """
    paired = list(zip(labels, values))
    paired_sorted = sorted(paired, key=lambda x: extract_sort_key(x[0]))
    sorted_labels, sorted_values = zip(*paired_sorted)
    return list(sorted_labels), list(sorted_values)


def main():

    # 0. Setup
    repositories = ["project_gutenberg", "internet_archive"]
    source_paths = {
        "project_gutenberg": aolm_data_reading.melville_source_directory["collected"] + f"body_text{os.sep}",
        "internet_archive": aolm_data_reading.melville_source_directory["internet_archive"] + f"body_text{os.sep}"
    }
    source_files = {}
    signature_metrics = {}

    # 1. Compute authorial signatures for each repository
    for repo_name in repositories:
        source_files[repo_name] = [filepath for filepath in glob.glob(source_paths[repo_name] + "*.txt")]

    for repo_name in repositories:

        # A. Calculate the author's signature
        signature_metrics[repo_name] = DatasetSignature_AuthorialSignature(source_files[repo_name])

        signature_metrics[repo_name].compute()      

        # B. Evaluate the source files' signatures against the average author signature
        signature_metrics[repo_name].evaluate()

    # 3. Compute the cosine distance between the repositories' authorial signatures
    repo_cosine_distance = get_distance_between_signature_vectors(
        signature_metrics["project_gutenberg"].signature,
        signature_metrics["internet_archive"].signature
    )

    print(f"Cosine distance between Project Gutenberg and Internet Archive Melville novels: {repo_cosine_distance}")

    # 4. Compute a quick and dirty lexical validity (without using reader objects) over the text files of both repositories
    compute_lexical_validity = False

    if compute_lexical_validity:
        # A. Read in the lexicon from COHA
        lexicon_filepath = "/Users/weirdbeard/Documents/school/aolm_full/data/lexicon/coha/lexicon.txt"
        coha_lexicon = read_coha(lexicon_filepath)
        
        # B. Compute the lexical validity of each work in each corpus according to COHA
        lexical_validities = { repo_name: {} for repo_name in repositories }
        for repo_name in repositories:
            for source_file in source_files[repo_name]:
                lexical_validities[repo_name][source_file] = \
                    DatasetValidity_LexicalValidity.lexical_validity(get_file_text(source_file), coha_lexicon)
                
        print(f"Project Gutenberg corpus average lexical validity: {mean([lexical_validities['project_gutenberg'][source_file] for source_file in lexical_validities['project_gutenberg']])}")
        print(f"Internet Archive corpus average lexical validity: {mean([lexical_validities['internet_archive'][source_file] for source_file in lexical_validities['internet_archive']])}")

        output_path = "/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/"
        with open(output_path + "pg_ia_melville_differences.csv", "w") as output_file:
            output_file.write("repository,filename,lexical_validity_percent\n")
            for repo_name in repositories:
                for source_file in source_files[repo_name]:
                    output_file.write(f"{repo_name},{os.path.basename(source_file)},{lexical_validities[repo_name][source_file]}\n")

    # 5. Plot the corpus distance against PG text-PG centroid distances
    plot_pg_distances_plus_pg2ia_distance(repo_cosine_distance)

    # # 0. Setup
    # source_path = aolm_data_reading.melville_source_directory["internet_archive"] + f"demarcated{os.sep}"
    # demarcated_files = [filepath for filepath in glob.glob(source_path + "*.json")]
    # plot_avg_chapter_legomena = False

    # # Read each Melville novel into memory
    # readers = [PGMelvilleReader(filepath) for filepath in demarcated_files]

    # # 1. Measure legomena by work and by chapter
    # dq_metric = DatasetSignature_Legomena(readers)
    # dq_metric.compute()
    # dq_metric.evaluate()

    # # 2. Output evaluations and metrics to csv
    # experiment_output_directory = f"{os.getcwd()}{os.sep}experiments{os.sep}outputs{os.sep}"
    # output_filepath = f"{experiment_output_directory}melville_novels_legomena_metric.csv"
    # dq_metric.to_csv(output_filepath)

if "__main__" == __name__:
    main()