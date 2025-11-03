# Author: Jonathan Armoza
# Created: October 31, 2025
# Purpose: Plot metadata sufficiency metric values for editions

# Imports

# Built-ins
import json
import os
import sys

# Third party
import pandas as pd
import plotly.express as px

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom
import aolm_data_reading
from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency


# Globals
MS_METRIC_NAME = DatasetCompleteness_MetadataSufficiency.s_metric_name
WORK_TITLE = "Adventures of Huckleberry Finn"
UR_EDITION = aolm_data_reading.MTPO


# Helper functions

def get_edition_shortname_from_metadata(p_text_json_filename):

    short_name = p_text_json_filename

    with open("/Users/weirdbeard/Documents/school/aolm_full/experiments/chapter1/huckfinneditions_filenames2fullnames.json", "r") as input_file:
        json_data = json.load(input_file)

    for key in json_data:
        if key in p_text_json_filename:
            short_name = json_data[key]["short_name"]
            break

    return short_name

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

    # 4. Calculate the metric values
    huckfinn_metadata_sufficiency.evaluate()

    # Return instance of the metric for further use
    return huckfinn_metadata_sufficiency


# Main script

# 1. Read, compute, and evaluate metrics
metrics = { source_id: run_huckfinn_dq_metadatasufficiency(source_id) for source_id in aolm_data_reading.huckfinn_source_fullnames if UR_EDITION != source_id }

# 2. Save metric values for plotting
metric_values = {}
for source_id in metrics:
    for filename in metrics[source_id].m_input:
        # print(get_edition_shortname_from_metadata(os.path.splitext(filename)[0]))
        metric_values[get_edition_shortname_from_metadata(os.path.splitext(filename)[0])] = \
            metrics[source_id].results["existence_and_completeness"]["percent_key_coverage"][filename]

order = [
    "montreal_dawson_1885_canadiana.org_2012",
    "ny_webster_1885_universityofcalifornialibraries_2006",
    "picadilly_1885_urbanschoolsanfrancisco_2011",
    "nylondon_harper_1896_universityofcalifornia_2006",
    "ny_harper_1904_haroldb.leelibrary_2011",
    "chattowindus_1910_2020",
    "ny_collier_1912_uncchapellhilluniversitylibrary_2015",
    "ny_harper_1912_universityoftoronto_2008",
    "harper_1918_2020",
    "harrap_1926_2020",
    "gutenberg_2011",
    "gutenberg_2016",
    "gutenberg_2021"
]

# 3. Convert to DataFrame
df = pd.DataFrame(list(metric_values.items()), columns=["Edition", "Percent Sufficient"])

# 4. Create Plotly Express bar plot

import plotly.express as px

# Example data
# metric_values = { get_edition_shortname_from_metadata(source_id): metrics[source_id].metric_evaluation for source_id in metrics }

fig = px.bar(
    x=list(metric_values.keys()),
    y=list(metric_values.values()),
    text=[f"{v:.2f}" for v in metric_values.values()],
    title="Metadata Existence and Completeness in Editions of 'Adventures of Huckleberry Finn'",
    color_discrete_sequence=["#0072B2"]  # Colorblind-friendly blue
)

# Layout adjustments
fig.update_traces(
    textposition='outside',
    textfont_size=14,
    cliponaxis=False
)

fig.update_layout(
    yaxis_title="Percent Key Coverage",
    xaxis_title="Edition",
    xaxis_tickangle=-45,
    template="plotly_white",
    height=700,
    font=dict(size=16),
    xaxis=dict(tickfont=dict(size=13),
               categoryarray=order,),
    yaxis=dict(tickfont=dict(size=14)),
    margin=dict(b=150)  # Prevent label clipping
)

fig.show()







