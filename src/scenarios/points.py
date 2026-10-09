"""Deterministic scenario points on the city graph (depot, customers, facilities).

Sampled from graph nodes with a fixed seed and cached to JSON, standing in for geocoded
addresses so the notebooks run offline without calling Nominatim. Real addresses would be
resolved once with :mod:`src.geocode.nominatim` and cached the same way.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import TYPE_CHECKING

from src.config import get_settings
from src.graph.snap import SnapIndex

if TYPE_CHECKING:
    import networkx as nx

LatLon = list[float]


def _node_latlon(graph: nx.MultiDiGraph, node: int) -> LatLon:
    return [float(graph.nodes[node]["y"]), float(graph.nodes[node]["x"])]


def generate_scenario(
    graph: nx.MultiDiGraph, n_customers: int = 120, seed: int = 42
) -> dict[str, object]:
    """Build a depot, a customer base, and four spread-out facilities from graph nodes."""
    rng = random.Random(seed)
    nodes = list(graph.nodes)
    sample = rng.sample(nodes, min(n_customers, len(nodes)))
    customers = [_node_latlon(graph, node) for node in sample]

    lats = [graph.nodes[n]["y"] for n in nodes]
    lons = [graph.nodes[n]["x"] for n in nodes]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    quarter_lat = (max(lats) - min(lats)) / 4.0
    quarter_lon = (max(lons) - min(lons)) / 4.0

    index = SnapIndex.from_graph(graph)
    depot = _node_latlon(graph, index.nearest(center_lat + quarter_lat, center_lon)[0])
    facility_targets = [
        (center_lat + quarter_lat, center_lon - quarter_lon),
        (center_lat + quarter_lat, center_lon + quarter_lon),
        (center_lat - quarter_lat, center_lon - quarter_lon),
        (center_lat - quarter_lat, center_lon + quarter_lon),
    ]
    facilities = [_node_latlon(graph, index.nearest(lat, lon)[0]) for lat, lon in facility_targets]

    return {"depot": depot, "customers": customers, "facilities": facilities}


def scenario_path(name: str = "pittsburgh") -> Path:
    """Path of the cached scenario JSON for a city."""
    return Path(get_settings().geocode.cache_dir) / f"{name}_scenario.json"


def save_scenario(scenario: dict[str, object], name: str = "pittsburgh") -> Path:
    """Write a scenario to JSON under the geocode cache directory."""
    path = scenario_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scenario, indent=2, sort_keys=True))
    return path


def load_scenario(
    name: str = "pittsburgh", n_customers: int = 120, seed: int = 42
) -> dict[str, object]:
    """Load the cached scenario, regenerating it from the cached graph if the JSON is absent.

    The scenario JSON is a (git-ignored) cache; on a fresh checkout it is rebuilt offline
    from the committed city GraphML, so it need not be committed to stay reproducible.
    """
    path = scenario_path(name)
    if path.exists():
        return json.loads(path.read_text())

    from src.graph.build import load_city_graph

    scenario = generate_scenario(
        load_city_graph(name, "drive"), n_customers=n_customers, seed=seed
    )
    save_scenario(scenario, name)
    return scenario
