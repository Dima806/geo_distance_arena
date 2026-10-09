"""The detour factor (circuity): the ratio of road distance to straight-line distance."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from src.distance.haversine import haversine_m
from src.distance.road import road_distance_m

if TYPE_CHECKING:
    import networkx as nx
    from numpy.typing import NDArray


def detour_factors(
    graph: nx.MultiDiGraph, node_pairs: list[tuple[int, int]]
) -> NDArray[np.float64]:
    """Road/straight ratio for each ``(orig_node, dest_node)`` pair."""
    ratios: list[float] = []
    for orig, dest in node_pairs:
        lat1, lon1 = graph.nodes[orig]["y"], graph.nodes[orig]["x"]
        lat2, lon2 = graph.nodes[dest]["y"], graph.nodes[dest]["x"]
        straight = haversine_m(lat1, lon1, lat2, lon2)
        if straight <= 0:
            continue
        ratios.append(road_distance_m(graph, orig, dest) / straight)
    return np.asarray(ratios, dtype=float)


def summarize(factors: NDArray[np.float64]) -> dict[str, float]:
    """Mean, median, p90, max, and std of a detour-factor distribution."""
    return {
        "mean": float(np.mean(factors)),
        "median": float(np.median(factors)),
        "p90": float(np.percentile(factors, 90)),
        "max": float(np.max(factors)),
        "std": float(np.std(factors)),
    }
