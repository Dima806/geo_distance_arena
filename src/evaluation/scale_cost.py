"""Compute cost versus N: straight-line is instant, road scales far worse."""

from __future__ import annotations

import random
from time import perf_counter
from typing import TYPE_CHECKING

import pandas as pd

from src.graph.matrix import road_distance_matrix, straight_line_matrix

if TYPE_CHECKING:
    import networkx as nx


def timing_vs_n(graph: nx.MultiDiGraph, sizes: list[int], seed: int = 42) -> pd.DataFrame:
    """Time the straight-line vs road distance matrix for growing N (sampled nodes)."""
    rng = random.Random(seed)
    nodes = list(graph.nodes)
    lats = {n: graph.nodes[n]["y"] for n in nodes}
    lons = {n: graph.nodes[n]["x"] for n in nodes}

    rows: list[dict[str, object]] = []
    for n in sizes:
        sample = rng.sample(nodes, min(n, len(nodes)))
        s_lats = [lats[node] for node in sample]
        s_lons = [lons[node] for node in sample]

        start = perf_counter()
        straight_line_matrix(s_lats, s_lons, s_lats, s_lons)
        straight_s = perf_counter() - start

        start = perf_counter()
        road_distance_matrix(graph, sample, sample)
        road_s = perf_counter() - start

        rows.append({"n": len(sample), "straight_line_s": straight_s, "road_s": road_s})
    return pd.DataFrame(rows)
