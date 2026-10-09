"""Manhattan (grid) distance, a cheap stand-in for road distance in a grid city.

Project to a local metric CRS, then take |dx| + |dy|. A rule of thumb that helps in
dense gridded street layouts and fails where the grid breaks down.
"""

from __future__ import annotations

from pyproj import Transformer

from src.distance.projected import WGS84, utm_epsg


def manhattan_distance_m(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    epsg: int | None = None,
) -> float:
    """L1 (grid) distance in metres after projecting to local UTM."""
    if epsg is None:
        epsg = utm_epsg((lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0)
    transformer = Transformer.from_crs(WGS84, f"EPSG:{epsg}", always_xy=True)
    x1, y1 = transformer.transform(lon1, lat1)
    x2, y2 = transformer.transform(lon2, lat2)
    return abs(x2 - x1) + abs(y2 - y1)
