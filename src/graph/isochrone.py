"""Isochrones: the subgraph reachable within T minutes, as a catchment polygon.

A drive-time catchment is the honest answer to "what can this location serve"; it looks
nothing like the straight-line circle everyone draws.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx
from shapely.geometry import MultiPoint

if TYPE_CHECKING:
    from shapely.geometry.base import BaseGeometry


def reachable_nodes(
    graph: nx.MultiDiGraph,
    center_node: int,
    max_seconds: float,
    weight: str = "travel_time",
) -> list[int]:
    """Nodes reachable from ``center_node`` within ``max_seconds`` of travel time."""
    lengths = nx.single_source_dijkstra_path_length(
        graph, center_node, cutoff=max_seconds, weight=weight
    )
    return list(lengths.keys())


def isochrone_polygon(
    graph: nx.MultiDiGraph,
    center_node: int,
    max_seconds: float,
    weight: str = "travel_time",
) -> BaseGeometry:
    """Convex-hull polygon of the reachable nodes (lon/lat) within ``max_seconds``."""
    nodes = reachable_nodes(graph, center_node, max_seconds, weight)
    points = [(graph.nodes[n]["x"], graph.nodes[n]["y"]) for n in nodes]
    return MultiPoint(points).convex_hull
