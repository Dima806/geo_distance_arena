"""Road distance is reproducible: Dijkstra == A*, and road >= straight-line everywhere."""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from src.distance.haversine import haversine_m
from src.distance.road import astar_distance_m, road_distance_m, road_travel_time_s

if TYPE_CHECKING:
    import networkx as nx

# A spread of grid nodes, including cross-river pairs (3/4 straddle the barrier).
SAMPLE_NODES = [0, 3, 4, 7, 24, 27, 28, 59, 60, 63]


def _lat_lon(graph: nx.MultiDiGraph, node: int) -> tuple[float, float]:
    return graph.nodes[node]["y"], graph.nodes[node]["x"]


def test_dijkstra_equals_astar(barrier_graph: nx.MultiDiGraph) -> None:
    for orig, dest in combinations(SAMPLE_NODES, 2):
        dijkstra = road_distance_m(barrier_graph, orig, dest)
        astar = astar_distance_m(barrier_graph, orig, dest)
        assert abs(dijkstra - astar) < 1e-6


def test_road_is_at_least_straight_line(barrier_graph: nx.MultiDiGraph) -> None:
    for orig, dest in combinations(SAMPLE_NODES, 2):
        lat1, lon1 = _lat_lon(barrier_graph, orig)
        lat2, lon2 = _lat_lon(barrier_graph, dest)
        straight = haversine_m(lat1, lon1, lat2, lon2)
        road = road_distance_m(barrier_graph, orig, dest)
        assert road >= straight - 1e-6


def test_cross_barrier_detour_is_large(barrier_graph: nx.MultiDiGraph) -> None:
    # Node 59 (row 7, west of river) to node 60 (row 7, east): the only bridge is at row 0,
    # so the road detours far beyond the ~85 m straight line.
    lat1, lon1 = _lat_lon(barrier_graph, 59)
    lat2, lon2 = _lat_lon(barrier_graph, 60)
    straight = haversine_m(lat1, lon1, lat2, lon2)
    road = road_distance_m(barrier_graph, 59, 60)
    assert road / straight > 3.0


def test_travel_time_is_positive(barrier_graph: nx.MultiDiGraph) -> None:
    assert road_travel_time_s(barrier_graph, 0, 63) > 0.0
