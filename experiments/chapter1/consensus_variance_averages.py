# Author: Jonathan Armoza
# Created: October 28, 2025
# Purpose: Read in the variance values for word and sentences of each chapter of the
# Internet Archive, Project Gutenberg, and Mark Twain Project Online editions and 
# compute the overall edition variance averages

import os
import pandas as pd
import plotly.express as px
import plotly.colors as pc

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

# Path to your CSV file
csv_file = f"{os.getcwd()}{os.sep}experiments{os.sep}outputs{os.sep}huckfinn_pgiamtpo_subx4metric.csv"

# Read the CSV into a DataFrame
df = pd.read_csv(csv_file)

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Group by edition_name and calculate the mean of the two columns
averages = df.groupby("edition_name")[
    ["variance_from_sentence_consensus__by_chapter", 
     "variance_from_word_consensus__by_chapter"]
].mean().reset_index()

# Human-readable names for the editions
averages["short_name"] = averages["edition_name"].apply(get_edition_shortname_from_metadata)

# Print the result
print(averages)

# Melt the DataFrame to long format for Plotly Express
averages_melted = averages.melt(
    id_vars="short_name", 
    value_vars=["variance_from_sentence_consensus__by_chapter", 
                "variance_from_word_consensus__by_chapter"],
    var_name="Metric",
    value_name="Average Variance"
)

# Choose a colorblind-friendly palette
color_palette = pc.qualitative.Safe 

# Create a bar plot
fig = px.bar(
    averages_melted,
    x="short_name",
    y="Average Variance",
    color="Metric",
    barmode="group",
    color_discrete_sequence=color_palette,
    title="Average Variance from Sentence and Word Consensus by Edition",
    labels={"short_name": "Edition Name", "Average Variance": "Average Variance"}
)

# Update layout for larger fonts
fig.update_layout(
    title_font=dict(size=24),
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
    xaxis_tickfont=dict(size=14),
    yaxis_tickfont=dict(size=14),
    legend_title_font=dict(size=16),
    legend_font=dict(size=14)
)

# Rotate x-axis labels for readability
fig.update_xaxes(tickangle=-45)

# Show the interactive plot
fig.show()