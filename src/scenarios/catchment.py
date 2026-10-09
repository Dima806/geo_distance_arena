"""Retail catchment three ways: straight-line circle, road distance, and drive-time.

The same location serves three very different-looking areas depending on the metric.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx
from shapely.geometry import MultiPoint, Point

from src.graph.isochrone import isochrone_polygon
from src.graph.snap import SnapIndex

if TYPE_CHECKING:
    from shapely.geometry.base import BaseGeometry

LatLon = tuple[float, float]


def straight_line_circle(
    center: LatLon, radius_m: float, degrees_per_m: float = 1.0 / 111_319.49
) -> BaseGeometry:
    """A crude straight-line catchment: a circle (buffer) in lon/lat degrees."""
    return Point(center[1], center[0]).buffer(radius_m * degrees_per_m)


def road_distance_catchment(
    graph: nx.MultiDiGraph, center: LatLon, max_road_m: float
) -> BaseGeometry:
    """Convex hull of nodes within ``max_road_m`` of road distance from ``center``."""
    index = SnapIndex.from_graph(graph)
    center_node, _ = index.nearest(*center)
    lengths = nx.single_source_dijkstra_path_length(
        graph, center_node, cutoff=max_road_m, weight="length"
    )
    points = [(graph.nodes[n]["x"], graph.nodes[n]["y"]) for n in lengths]
    return MultiPoint(points).convex_hull


def drive_time_catchment(
    graph: nx.MultiDiGraph, center: LatLon, max_seconds: float
) -> BaseGeometry:
    """Drive-time isochrone polygon from ``center``."""
    index = SnapIndex.from_graph(graph)
    center_node, _ = index.nearest(*center)
    return isochrone_polygon(graph, center_node, max_seconds)
