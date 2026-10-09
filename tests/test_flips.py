"""Nearest-facility assignment flips between metrics, and the flips sit at the barrier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.evaluation.ranking_flips import flip_rate
from src.scenarios.nearest_facility import assign_nearest

if TYPE_CHECKING:
    import networkx as nx

# Two facilities on the top row: A just across the river (east), B on the same side (west).
FACILITIES = [(40.007, -73.996), (40.007, -74.000)]  # (A across river, B same side)
# Customers on the west bank near the barrier, where the bridge is far (row 0).
CUSTOMERS = [(40.007, -73.997), (40.006, -73.997), (40.005, -73.997)]
# The river runs between columns 3 and 4: lon0 + 3.5 * dlon = -74.0 + 0.0035.
BARRIER_LON = -73.9965


def test_some_assignments_flip(barrier_graph: nx.MultiDiGraph) -> None:
    assignments = assign_nearest(barrier_graph, FACILITIES, CUSTOMERS)
    assert flip_rate(assignments) > 0.0


def test_top_customer_flips_to_same_side_facility(barrier_graph: nx.MultiDiGraph) -> None:
    assignments = assign_nearest(barrier_graph, FACILITIES, [(40.007, -73.997)])
    row = assignments.iloc[0]
    assert row["straight_nearest"] == 0  # straight line picks A, just across the river
    assert row["road_nearest"] == 1  # the road reaches B first (bridge is far)
    assert bool(row["flip"]) is True


def test_flips_are_near_the_barrier(barrier_graph: nx.MultiDiGraph) -> None:
    from src.distance.haversine import haversine_m

    assignments = assign_nearest(barrier_graph, FACILITIES, CUSTOMERS)
    flipped = assignments[assignments["flip"]]
    assert len(flipped) > 0
    for lat, lon in zip(flipped["lat"], flipped["lon"], strict=False):
        distance_to_barrier = haversine_m(lat, lon, lat, BARRIER_LON)
        assert distance_to_barrier < 150.0  # within one grid cell of the river
