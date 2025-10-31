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
        textposition="outside"
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
        marker=dict(size=8)
    )
)

# Layout with dual y-axis
fig.update_layout(
    title="Melville Novels: Hapax Counts vs Authorial Signature Distance",
    xaxis=dict(title="Novel", tickangle=-45, tickfont=dict(size=14)),
    yaxis=dict(title="Total Hapax", tickfont=dict(size=14)),
    yaxis2=dict(
        title="Distance from Authorial Signature",
        overlaying="y",
        side="right",
        tickfont=dict(size=14),
        showgrid=False
    ),
    legend=dict(x=0.05, y=0.95, font=dict(size=12)),
    bargap=0.3,
    title_font=dict(size=20)
)

fig.show()
