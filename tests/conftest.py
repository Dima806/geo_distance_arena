"""Shared fixtures. The planted barrier graph lets every test run offline."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.distance.road import add_edge_speeds, add_edge_travel_times
from src.graph.build import build_synthetic_barrier_graph

if TYPE_CHECKING:
    import networkx as nx


@pytest.fixture
def barrier_graph() -> nx.MultiDiGraph:
    """An 8x8 grid city split by a river with one bridge, speeds and times attached."""
    graph = build_synthetic_barrier_graph()
    add_edge_speeds(graph, default_kph=30.0)
    add_edge_travel_times(graph)
    return graph
