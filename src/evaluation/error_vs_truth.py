"""Straight-line error of each method against the geodesic ground truth."""

from __future__ import annotations

import pandas as pd

from src.distance.geodesic import geodesic_distance_m
from src.distance.haversine import haversine_m
from src.distance.manhattan import manhattan_distance_m
from src.distance.projected import naive_degree_scaled_m, projected_distance_m

Pair = tuple[float, float, float, float]


def straight_line_errors(pairs: list[Pair]) -> pd.DataFrame:
    """Compare every straight-line method to the geodesic truth over ``pairs``.

    Each pair is ``(lat1, lon1, lat2, lon2)``. Returns absolute and relative error of
    haversine, projected-Euclidean, Manhattan, and the naive degrees-as-metres bug.
    """
    rows: list[dict[str, object]] = []
    for lat1, lon1, lat2, lon2 in pairs:
        truth = geodesic_distance_m(lat1, lon1, lat2, lon2)
        methods = {
            "haversine": haversine_m(lat1, lon1, lat2, lon2),
            "projected": projected_distance_m(lat1, lon1, lat2, lon2),
            "manhattan": manhattan_distance_m(lat1, lon1, lat2, lon2),
            "naive_degree_scaled": naive_degree_scaled_m(lat1, lon1, lat2, lon2),
        }
        row: dict[str, object] = {"geodesic_m": truth}
        for name, value in methods.items():
            row[f"{name}_m"] = value
            row[f"{name}_abs_err_m"] = abs(value - truth)
            row[f"{name}_rel_err"] = abs(value - truth) / truth if truth > 0 else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)
