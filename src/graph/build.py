"""Build and cache road graphs.

Two sources:

* :func:`build_graph_from_place` downloads a real street network from OpenStreetMap with
  OSMnx (keyless Overpass, no Docker, no server). Used by the one-time ``make graph``
  step; OSMnx is imported lazily so the rest of the project -- and the whole test suite --
  runs without it.
* :func:`build_synthetic_barrier_graph` constructs a small, deterministic grid city split
  by a river with a single bridge. It needs no network, so tests and quick demos reproduce
  the detour-factor and nearest-facility-flip effects offline.

Real graphs are cached to GraphML so the download happens once and everything after runs
offline.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from src.distance.haversine import haversine_m


def build_synthetic_barrier_graph(
    rows: int = 8,
    cols: int = 8,
    river_col: int = 3,
    bridge_row: int = 0,
    lat0: float = 40.0,
    lon0: float = -74.0,
    dlat: float = 0.001,
    dlon: float = 0.001,
) -> nx.MultiDiGraph:
    """A grid city split by a north-south river crossed by a single bridge.

    Horizontal roads between columns ``river_col`` and ``river_col + 1`` exist only at
    ``bridge_row``; vertical roads always exist. Edge ``length`` is the great-circle
    distance between endpoints, so the shortest path is >= straight-line for every pair.
    """
    graph: nx.MultiDiGraph = nx.MultiDiGraph(crs="EPSG:4326")

    def node_id(row: int, col: int) -> int:
        return row * cols + col

    for row in range(rows):
        for col in range(cols):
            graph.add_node(node_id(row, col), x=lon0 + col * dlon, y=lat0 + row * dlat)

    def add_road(node_a: int, node_b: int) -> None:
        lat_a, lon_a = graph.nodes[node_a]["y"], graph.nodes[node_a]["x"]
        lat_b, lon_b = graph.nodes[node_b]["y"], graph.nodes[node_b]["x"]
        length = haversine_m(lat_a, lon_a, lat_b, lon_b)
        graph.add_edge(node_a, node_b, length=length, highway="residential")
        graph.add_edge(node_b, node_a, length=length, highway="residential")

    for row in range(rows):
        for col in range(cols):
            if row + 1 < rows:
                add_road(node_id(row, col), node_id(row + 1, col))
            if col + 1 < cols:
                crosses_river = col == river_col
                if not crosses_river or row == bridge_row:
                    add_road(node_id(row, col), node_id(row, col + 1))

    return graph


def build_graph_from_point(
    center_lat: float,
    center_lon: float,
    dist_m: float,
    network_type: str = "drive",
) -> nx.MultiDiGraph:
    """Download a real network within ``dist_m`` of a center point (online, keyless)."""
    import osmnx as ox

    return ox.graph_from_point((center_lat, center_lon), dist=dist_m, network_type=network_type)


def save_graphml(graph: nx.MultiDiGraph, path: Path | str) -> None:
    """Write a graph to GraphML, creating parent directories as needed."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    import osmnx as ox

    ox.save_graphml(graph, filepath=out)


def city_graph_path(name: str, mode: str = "drive", cache_dir: Path | str | None = None) -> Path:
    """Path of the cached GraphML for a city/mode."""
    from src.config import get_settings

    base = Path(cache_dir) if cache_dir is not None else Path(get_settings().graph.cache_dir)
    return base / f"{name}_{mode}.graphml"


def load_city_graph(name: str = "pittsburgh", mode: str = "drive") -> nx.MultiDiGraph:
    """Load a cached city graph (offline). Build and cache it on a miss (online)."""
    import osmnx as ox

    from src.config import get_settings

    path = city_graph_path(name, mode)
    if path.exists():
        return ox.load_graphml(path)

    settings = get_settings()
    city = next((c for c in settings.graph.cities if c.name == name), None)
    if city is None:
        msg = f"no city named {name!r} in settings"
        raise KeyError(msg)
    graph = build_graph_from_point(city.center_lat, city.center_lon, city.dist_m, mode)
    save_graphml(graph, path)
    return graph


def main() -> None:
    """``make graph`` entry point: download configured cities/modes and cache them."""
    import osmnx as ox

    from src.config import get_settings

    settings = get_settings()
    cache_dir = Path(settings.graph.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    for city in settings.graph.cities:
        for mode in settings.graph.network_types:
            print(
                f"Downloading {city.name} ({mode}) around ({city.center_lat}, {city.center_lon}) ..."
            )
            graph = build_graph_from_point(city.center_lat, city.center_lon, city.dist_m, mode)
            ox.save_graphml(graph, filepath=cache_dir / f"{city.name}_{mode}.graphml")

    synthetic = build_synthetic_barrier_graph()
    ox.save_graphml(synthetic, filepath=cache_dir / "synthetic_barrier.graphml")
    print(
        f"Cached {len(settings.graph.cities)} cities x {len(settings.graph.network_types)} modes to {cache_dir}"
    )


if __name__ == "__main__":
    main()
