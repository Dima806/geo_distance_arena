"""The arena harness: every method on the same point pairs, side by side."""

from __future__ import annotations

import pandas as pd

from src.distance.geodesic import geodesic_distance_m
from src.distance.haversine import haversine_m
from src.distance.manhattan import manhattan_distance_m
from src.distance.projected import projected_distance_m

Pair = tuple[float, float, float, float]


def compare_methods(pairs: list[Pair]) -> pd.DataFrame:
    """Return one row per pair with every straight-line method's distance (metres).

    Road distance and travel time need a graph and are added by the road-aware scenarios;
    this harness covers the keyless, graph-free straight-line family.
    """
    rows: list[dict[str, float]] = []
    for lat1, lon1, lat2, lon2 in pairs:
        rows.append(
            {
                "geodesic_m": geodesic_distance_m(lat1, lon1, lat2, lon2),
                "haversine_m": haversine_m(lat1, lon1, lat2, lon2),
                "projected_m": projected_distance_m(lat1, lon1, lat2, lon2),
                "manhattan_m": manhattan_distance_m(lat1, lon1, lat2, lon2),
            }
        )
    return pd.DataFrame(rows)
