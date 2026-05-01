# Author: Jonathan Armoza
# Created: October 28, 2025
# Purpose: Compare total hapax legomena counts in Melville's novels to term frequency distance to novels mean term frequency vector

import plotly.graph_objects as go

# Novels in publication order, with parenthetical years
novels = [
    "Typee (1846)", "Omoo (1847)", "Mardi Vol.1 (1849)", "Mardi Vol.2 (1849)",
    "Redburn (1849)", "White Jacket (1850)", "Moby-Dick (1851)",
    "Pierre (1852)", "Israel Potter (1855)", "The Confidence-Man (1857)"
]

# Total hapax counts
hapax_counts = [5583, 6374, 7144, 9238, 7360, 9454, 11550, 9831, 6139, 7646]

# Authorial signature distances
signature_distances = [0.0147, 0.0117, 0.0066, 0.0202, 0.0175, 0.0063, 0.0054, 0.0206, 0.0185, 0.0350]

from scipy.stats import pearsonr

r, p = pearsonr(hapax_counts, signature_distances)
print(r, p)

from scipy.stats import spearmanr

rho, p = spearmanr(hapax_counts, signature_distances)
print(rho, p)

# Create figure
fig = go.Figure()

# Bar trace: Hapax counts
fig.add_trace(
    go.Bar(
        x=novels,
        y=hapax_counts,
        name="Total Hapax",
        marker_color="indigo",
        text=hapax_counts,
        textposition="outside",
        textfont=dict(size=18),  # match bar_text_font_size
        cliponaxis=False
    )
)

# Line trace: Authorial signature distance
fig.add_trace(
    go.Scatter(
        x=novels,
        y=signature_distances,
        name="Distance from Authorial Signature",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="firebrick", width=3),
        marker=dict(size=10)  # slightly larger to match scaling
    )
)

# Layout with dual y-axis
fig.update_layout(
    title=dict(
        text="Melville Novels: Hapax Counts vs Authorial Signature Distance",
        font=dict(size=26)  # match title_font_size
    ),
    xaxis=dict(
        title=dict(text="Novel", font=dict(size=18)),  # axis_title_font_size
        tickangle=-45,
        tickfont=dict(size=16)  # tick_font_size
    ),
    yaxis=dict(
        title=dict(text="Total Hapax", font=dict(size=18)),
        tickfont=dict(size=16)
    ),
    yaxis2=dict(
        title=dict(text="Distance from Authorial Signature", font=dict(size=18)),
        overlaying="y",
        side="right",
        tickfont=dict(size=16),
        showgrid=False
    ),
    legend=dict(
        x=0.05,
        y=0.95,
        font=dict(size=14)  # bump slightly for consistency
    ),
    bargap=0.3,
    height=1080,  # match your current approach
    margin=dict(l=80, r=80, t=100, b=90)
)

fig.show()
