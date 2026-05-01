# Author: Jonathan Armoza
# Created: October 31, 2025
# Purpose: Plot record count to control submetric values for editions for words and sentences

import json
import os
import pandas as pd
import plotly.express as px
import plotly.colors as pc
import re

def get_edition_shortname_from_metadata(p_text_json_filename):

    short_name = p_text_json_filename

    with open(f"{os.getcwd()}{os.sep}huckfinneditions_filenames2fullnames.json", "r") as input_file:
        json_data = json.load(input_file)

    for key in json_data:
        if key in p_text_json_filename:
            short_name = json_data[key]["short_name"]
            break

    return short_name

# with open(f"{os.getcwd()}{os.sep}..{os.sep}outputs{os.sep}huckfinn_dq_experiment_01112025_181442_eval_record_counts_to_control.json", "r") as input_file:
with open(f"{os.getcwd()}{os.sep}..{os.sep}outputs{os.sep}huckfinn_dq_experiment_dqaf_final_eval_record_counts_to_control.json", "r") as input_file:
    json_data = json.load(input_file)

edition_order = [
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

# --- Prepare a DataFrame ---
rows = []
for source_key in ["ia", "pg"]:
    editions = json_data[source_key]["individual_editions"]
    for edition_id, edition_data in editions.items():
        rows.append({
            "Edition": get_edition_shortname_from_metadata(edition_data["edition_title"]),
            "Source": edition_data["source"],
            "Sentence Count": edition_data["submetric"]["sentence_count"],
            "Word Count": edition_data["submetric"]["word_count"]
        })

df = pd.DataFrame(rows)

# Melt for plotting
df_melted = df.melt(
    id_vars=["Edition", "Source"],
    value_vars=["Sentence Count", "Word Count"],
    var_name="Metric",
    value_name="Value"
)

# Apply categorical ordering for x-axis
df_melted['Edition'] = pd.Categorical(df_melted['Edition'],
                                      categories=edition_order,
                                      ordered=True)
df_melted["Metric"] = df_melted["Metric"].replace({
    "Sentence Count": "Sentence Match",
    "Word Count": "Word Match"
})

# Colorblind-friendly palette
color_palette = pc.qualitative.Safe

# --- Vertical bar plot ---
fig = px.bar(
    df_melted,
    x="Edition",       # editions along x-axis
    y="Value",         # counts along y-axis
    color="Metric",
    barmode="group",
    color_discrete_sequence=color_palette,
    text=df_melted["Value"].map(lambda v: f"{v:.2f}"),
    hover_data={"Source": True, "Metric": True, "Value": ":.2f"}
)

# Place labels above bars and prevent clipping
fig.update_traces(textposition='outside',
                  textfont=dict(size=18),
                  cliponaxis=False)

# Layout adjustments
# fig.update_layout(
#     title="Sentence and Word Match Percentages by Edition (Compared against the MTPO Edition)",
#     xaxis_title="Edition",
#     yaxis_title="Percent Match",
#     template="plotly_white",
#     height=800,
#     title_font=dict(size=24),
#     xaxis_title_font=dict(size=18),
#     yaxis_title_font=dict(size=18),
#     xaxis_tickfont=dict(size=14),
#     yaxis_tickfont=dict(size=14, family="Arial Bold"),
#     xaxis_tickangle=-45,
#     legend_title_font=dict(size=16),
#     legend_font=dict(size=14)
# )

fig.update_layout(
    title="Sentence and Word Match Percentages by Edition (Compared against the MTPO Edition)",
    xaxis_title="Edition",
    yaxis_title="Percent Match",
    template="plotly_white",
    height=800,

    # Title
    title_font=dict(size=26),

    # Axis titles
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),

    # Tick labels
    xaxis=dict(
        tickfont=dict(size=15),
        tickangle=-45,
        categoryarray=edition_order
    ),
    yaxis=dict(
        tickfont=dict(size=16)
    ),

    # Legend
    legend_title_font=dict(size=16),
    legend_font=dict(size=14),

    # Prevent crowding at bottom
    margin=dict(b=180)
)

fig.update_yaxes(tickformat=".0f")



fig.show()


