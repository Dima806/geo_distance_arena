"""Snap points to the nearest road node, and measure the snapping error.

Uses a scikit-learn ``BallTree`` with the haversine metric for fast nearest-node queries
over the graph. The snapping distance is reported as an explicit caveat: sparse rural
graphs snap points farther, which inflates road distance for those points.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from sklearn.neighbors import BallTree

from src.distance.haversine import EARTH_RADIUS_M

if TYPE_CHECKING:
    import networkx as nx
    from numpy.typing import ArrayLike


class SnapIndex:
    """Nearest-road-node lookup over a graph's nodes."""

    def __init__(self, node_ids: ArrayLike, lats: ArrayLike, lons: ArrayLike) -> None:
        self.node_ids = np.asarray(node_ids)
        coords = np.radians(
            np.column_stack([np.asarray(lats, dtype=float), np.asarray(lons, dtype=float)])
        )
        self._tree = BallTree(coords, metric="haversine")

    @classmethod
    def from_graph(cls, graph: nx.MultiDiGraph) -> SnapIndex:
        """Build a snap index from a graph whose nodes carry ``x`` (lon) and ``y`` (lat)."""
        nodes = list(graph.nodes)
        lats = [graph.nodes[n]["y"] for n in nodes]
        lons = [graph.nodes[n]["x"] for n in nodes]
        return cls(nodes, lats, lons)

    def nearest(self, lat: float, lon: float) -> tuple[int, float]:
        """Return ``(node_id, snap_distance_m)`` for the nearest road node to ``(lat, lon)``."""
        query = np.radians([[lat, lon]])
        dist, idx = self._tree.query(query, k=1)
        node = int(self.node_ids[int(idx[0, 0])])
        snap_m = float(dist[0, 0]) * EARTH_RADIUS_M
        return node, snap_m


def snapping_errors_m(graph: nx.MultiDiGraph, points: list[tuple[float, float]]) -> list[float]:
    """Return the snapping distance (metres) for each ``(lat, lon)`` in ``points``."""
    index = SnapIndex.from_graph(graph)
    return [index.nearest(lat, lon)[1] for lat, lon in points]
