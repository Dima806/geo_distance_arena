"""Logistics cost estimation, and why a single detour-factor correction is not enough.

A straight-line cost matrix underprices far and barrier-separated legs. Multiplying by the
mean detour factor fixes the average but leaves the barrier cases just as wrong -- shown
here by the residual after correction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from src.graph.matrix import road_distance_matrix, straight_line_matrix
from src.graph.snap import SnapIndex

if TYPE_CHECKING:
    import networkx as nx
    from numpy.typing import NDArray

LatLon = tuple[float, float]


def straight_line_cost_matrix(
    origins: list[LatLon],
    dests: list[LatLon],
    cost_per_km: float = 1.0,
) -> NDArray[np.float64]:
    """Cost matrix from straight-line distance (the cheap, biased default)."""
    o_lats = [p[0] for p in origins]
    o_lons = [p[1] for p in origins]
    d_lats = [p[0] for p in dests]
    d_lons = [p[1] for p in dests]
    return straight_line_matrix(o_lats, o_lons, d_lats, d_lons) / 1000.0 * cost_per_km


def road_cost_matrix(
    graph: nx.MultiDiGraph,
    origins: list[LatLon],
    dests: list[LatLon],
    cost_per_km: float = 1.0,
) -> NDArray[np.float64]:
    """Cost matrix from true road distance (snap each point, then Dijkstra)."""
    index = SnapIndex.from_graph(graph)
    origin_nodes = [index.nearest(lat, lon)[0] for lat, lon in origins]
    dest_nodes = [index.nearest(lat, lon)[0] for lat, lon in dests]
    return road_distance_matrix(graph, origin_nodes, dest_nodes) / 1000.0 * cost_per_km


def single_multiplier_residual(
    straight: NDArray[np.float64],
    road: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Residual after correcting straight-line by its mean road/straight ratio.

    A flat multiplier removes the average bias but not the barrier bias; the returned
    residual (corrected minus true, as a fraction of true) stays large at barriers.
    """
    finite = np.isfinite(road) & (straight > 0)
    mean_factor = float(np.mean(road[finite] / straight[finite]))
    corrected = straight * mean_factor
    with np.errstate(divide="ignore", invalid="ignore"):
        return (corrected - road) / road
