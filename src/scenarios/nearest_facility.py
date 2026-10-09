"""Which facility is "nearest" -- and how often straight-line and road disagree.

For each customer, the nearest facility by straight-line distance and by road distance
are both computed; where they differ, the assignment "flips". Flips cluster at barriers,
exactly the hard cases where the wrong "nearest branch" costs the most.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from src.distance.haversine import haversine_m
from src.distance.road import road_distance_m
from src.graph.snap import SnapIndex

LatLon = tuple[float, float]


def _road_or_inf(graph: nx.MultiDiGraph, orig_node: int, dest_node: int) -> float:
    """Road distance, or infinity when the destination is unreachable (one-ways/islands)."""
    try:
        return road_distance_m(graph, orig_node, dest_node)
    except nx.NetworkXNoPath:
        return float("inf")


def assign_nearest(
    graph: nx.MultiDiGraph,
    facilities: list[LatLon],
    customers: list[LatLon],
) -> pd.DataFrame:
    """Assign each customer to its nearest facility by straight-line and by road.

    Returns a frame with one row per customer: coordinates, the index of the
    straight-line-nearest and road-nearest facility, both distances, and ``flip``.
    """
    index = SnapIndex.from_graph(graph)
    facility_nodes = [index.nearest(lat, lon)[0] for lat, lon in facilities]

    rows: list[dict[str, object]] = []
    for lat, lon in customers:
        customer_node, _snap_m = index.nearest(lat, lon)
        straight = [haversine_m(lat, lon, f_lat, f_lon) for f_lat, f_lon in facilities]
        road = [_road_or_inf(graph, customer_node, f_node) for f_node in facility_nodes]
        straight_nearest = int(np.argmin(straight))
        road_nearest = int(np.argmin(road))
        rows.append(
            {
                "lat": lat,
                "lon": lon,
                "straight_nearest": straight_nearest,
                "road_nearest": road_nearest,
                "straight_m": straight[straight_nearest],
                "road_m": road[road_nearest],
                "flip": straight_nearest != road_nearest,
            }
        )
    return pd.DataFrame(rows)
