"""Depot -> customers: the straight-line radius versus the real road distance.

The straight-line "within X km" radius is a circle on a map; the road distance is what
the van drives. The per-customer detour factor shows how badly the circle misleads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from src.distance.haversine import haversine_m
from src.distance.road import road_distance_m, road_travel_time_s
from src.graph.snap import SnapIndex

if TYPE_CHECKING:
    import networkx as nx

LatLon = tuple[float, float]


def depot_to_customers(
    graph: nx.MultiDiGraph,
    depot: LatLon,
    customers: list[LatLon],
    *,
    with_time: bool = False,
) -> pd.DataFrame:
    """Straight-line vs road distance (and optional travel time) from depot to customers."""
    index = SnapIndex.from_graph(graph)
    depot_node, _ = index.nearest(*depot)

    rows: list[dict[str, object]] = []
    for lat, lon in customers:
        customer_node, snap_m = index.nearest(lat, lon)
        straight = haversine_m(depot[0], depot[1], lat, lon)
        road = road_distance_m(graph, depot_node, customer_node)
        row: dict[str, object] = {
            "lat": lat,
            "lon": lon,
            "straight_m": straight,
            "road_m": road,
            "detour_factor": road / straight if straight > 0 else float("nan"),
            "snap_m": snap_m,
        }
        if with_time:
            row["road_time_s"] = road_travel_time_s(graph, depot_node, customer_node)
        rows.append(row)
    return pd.DataFrame(rows)
