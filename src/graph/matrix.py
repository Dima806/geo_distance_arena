"""Many-to-many distance matrices: fast straight-line and honest road distance.

Straight-line is a vectorised broadcast (and a BallTree for nearest-neighbour over huge
point sets); road distance is one Dijkstra per origin. The gap in cost is the whole point
of the speed-accuracy trade-off, and motivates the hybrid prefilter in notebook 05.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx
import numpy as np
from sklearn.neighbors import BallTree

from src.distance.haversine import EARTH_RADIUS_M

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def straight_line_matrix(
    lats_a: ArrayLike,
    lons_a: ArrayLike,
    lats_b: ArrayLike,
    lons_b: ArrayLike,
) -> NDArray[np.float64]:
    """Pairwise great-circle distances (metres) between set A (rows) and set B (cols)."""
    lat_a = np.radians(np.asarray(lats_a, dtype=float))[:, None]
    lon_a = np.radians(np.asarray(lons_a, dtype=float))[:, None]
    lat_b = np.radians(np.asarray(lats_b, dtype=float))[None, :]
    lon_b = np.radians(np.asarray(lons_b, dtype=float))[None, :]
    dlat = lat_b - lat_a
    dlon = lon_b - lon_a
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat_a) * np.cos(lat_b) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def road_distance_matrix(
    graph: nx.MultiDiGraph,
    origin_nodes: list[int],
    dest_nodes: list[int],
    weight: str = "length",
) -> NDArray[np.float64]:
    """Road distance (or time, via ``weight``) matrix via one Dijkstra per origin."""
    dest_index = {node: col for col, node in enumerate(dest_nodes)}
    out = np.full((len(origin_nodes), len(dest_nodes)), np.inf)
    for row, origin in enumerate(origin_nodes):
        lengths = nx.single_source_dijkstra_path_length(graph, origin, weight=weight)
        for node, length in lengths.items():
            col = dest_index.get(node)
            if col is not None:
                out[row, col] = length
    return out


def nearest_candidates(
    cand_lats: ArrayLike,
    cand_lons: ArrayLike,
    query_lats: ArrayLike,
    query_lons: ArrayLike,
    k: int,
) -> tuple[NDArray[np.int64], NDArray[np.float64]]:
    """BallTree(haversine) prefilter: ``k`` nearest candidates per query point.

    Returns ``(indices, distances_m)``. This is the cheap shortlist step of the hybrid
    that road distance then re-ranks.
    """
    cand = np.radians(
        np.column_stack([np.asarray(cand_lats, dtype=float), np.asarray(cand_lons, dtype=float)])
    )
    query = np.radians(
        np.column_stack([np.asarray(query_lats, dtype=float), np.asarray(query_lons, dtype=float)])
    )
    tree = BallTree(cand, metric="haversine")
    dist, idx = tree.query(query, k=k)
    return idx.astype(np.int64), dist * EARTH_RADIUS_M
