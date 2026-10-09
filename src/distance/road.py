"""Road distance and travel time on a street network.

The honest measurement: shortest path through a real (or planted) road graph with
NetworkX. Operates on any ``networkx.MultiDiGraph`` whose nodes carry ``x``/``y``
(lon/lat) and whose edges carry ``length`` (metres) -- the OSMnx convention -- so the
heavy OSMnx download is isolated in :mod:`src.graph.build` and never needed here.

Edge speeds and travel times are derived from OSM ``highway`` classes (or a default), so
free, speed-limited travel time comes for nothing but CPU. Live-traffic ETA is out of
scope and needs a routing engine.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from src.distance.haversine import haversine_m

if TYPE_CHECKING:
    from collections.abc import Mapping


def _highway_class(value: object) -> str | None:
    """Normalise an OSM ``highway`` tag (which may be a list) to a single class."""
    if isinstance(value, list):
        return str(value[0]) if value else None
    if value is None:
        return None
    return str(value)


def add_edge_speeds(
    graph: nx.MultiDiGraph,
    default_kph: float,
    by_highway: Mapping[str, float] | None = None,
) -> nx.MultiDiGraph:
    """Annotate every edge with ``speed_kph`` from its highway class or the default."""
    by_highway = dict(by_highway or {})
    for _u, _v, data in graph.edges(data=True):
        hwy = _highway_class(data.get("highway"))
        data["speed_kph"] = by_highway.get(hwy, default_kph) if hwy else default_kph
    return graph


def add_edge_travel_times(graph: nx.MultiDiGraph, default_kph: float = 50.0) -> nx.MultiDiGraph:
    """Annotate every edge with ``travel_time`` (seconds) from ``length`` and ``speed_kph``."""
    for _u, _v, data in graph.edges(data=True):
        kph = float(data.get("speed_kph", default_kph))
        metres_per_second = kph * 1000.0 / 3600.0
        data["travel_time"] = float(data["length"]) / metres_per_second
    return graph


def road_distance_m(graph: nx.MultiDiGraph, orig_node: int, dest_node: int) -> float:
    """Shortest-path road distance in metres (Dijkstra on ``length``)."""
    return float(nx.shortest_path_length(graph, orig_node, dest_node, weight="length"))


def road_travel_time_s(graph: nx.MultiDiGraph, orig_node: int, dest_node: int) -> float:
    """Shortest travel time in seconds (Dijkstra on ``travel_time``)."""
    return float(nx.shortest_path_length(graph, orig_node, dest_node, weight="travel_time"))


def astar_distance_m(graph: nx.MultiDiGraph, orig_node: int, dest_node: int) -> float:
    """Road distance via A* with a haversine heuristic (admissible, so == Dijkstra)."""

    def heuristic(node_u: int, node_v: int) -> float:
        lat_u, lon_u = graph.nodes[node_u]["y"], graph.nodes[node_u]["x"]
        lat_v, lon_v = graph.nodes[node_v]["y"], graph.nodes[node_v]["x"]
        return haversine_m(lat_u, lon_u, lat_v, lon_v)

    return float(
        nx.astar_path_length(graph, orig_node, dest_node, heuristic=heuristic, weight="length")
    )


def route_distance_m(graph: nx.MultiDiGraph, route: list[int]) -> float:
    """Total length in metres of an explicit node ``route``."""
    total = 0.0
    for node_u, node_v in zip(route[:-1], route[1:], strict=False):
        edge_data = min(graph[node_u][node_v].values(), key=lambda d: d["length"])
        total += float(edge_data["length"])
    return total
