"""Maps and plots: folium for geography, matplotlib for distributions.

Thin helpers the notebooks and the Streamlit app call; all heavy lifting lives in the
distance, graph, scenario, and evaluation modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import folium
import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.figure import Figure
    from numpy.typing import NDArray

LatLon = tuple[float, float]


def detour_factor_histogram(factors: NDArray[np.float64], bins: int = 40) -> Figure:
    """Histogram of the detour-factor distribution with the mean marked."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(factors, bins=bins, color="#4C78A8", edgecolor="white")
    ax.axvline(float(np.mean(factors)), color="#E45756", linestyle="--", label="mean")
    ax.axvline(1.0, color="#333333", linestyle=":", label="straight-line (1.0)")
    ax.set_xlabel("road / straight-line (detour factor)")
    ax.set_ylabel("count")
    ax.legend()
    fig.tight_layout()
    return fig


def flip_map(assignments: pd.DataFrame, facilities: list[LatLon]) -> folium.Map:
    """Folium map of customers coloured by whether their nearest facility flipped."""
    center_lat = float(assignments["lat"].mean())
    center_lon = float(assignments["lon"].mean())
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    for lat, lon in facilities:
        folium.Marker([lat, lon], icon=folium.Icon(color="blue", icon="home")).add_to(fmap)

    for _, row in assignments.iterrows():
        flipped = bool(row["flip"])
        folium.CircleMarker(
            [float(row["lat"]), float(row["lon"])],
            radius=5,
            color="#E45756" if flipped else "#54A24B",
            fill=True,
            fill_opacity=0.8,
            popup="flip" if flipped else "stable",
        ).add_to(fmap)
    return fmap
