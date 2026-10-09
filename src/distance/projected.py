"""Projected Euclidean distance, and the cautionary bugs around it.

Projecting to the correct local UTM zone and taking a plain Euclidean distance is
excellent over small areas. This module also reproduces the classic disasters, so the
reader can see the magnitude of the error and never ship them:

* ``naive_degree_distance_m`` -- Euclidean distance on raw lat/lon as if degrees were
  metres. Meaningless.
* ``naive_degree_scaled_m`` -- degrees scaled by a single constant, ignoring that a
  degree of longitude shrinks with latitude.
* ``wrong_zone_distance_m`` -- projecting into the wrong UTM zone.
"""

from __future__ import annotations

import math

from pyproj import Transformer

WGS84 = "EPSG:4326"
# Length of one degree of latitude near the equator (metres); a common naive constant.
METRES_PER_DEGREE = 111_319.49


def utm_epsg(lat: float, lon: float) -> int:
    """Return the EPSG code of the UTM zone containing ``(lat, lon)``."""
    zone = int((lon + 180.0) // 6.0) + 1
    return (32600 if lat >= 0 else 32700) + zone


def _transformer(epsg: int) -> Transformer:
    return Transformer.from_crs(WGS84, f"EPSG:{epsg}", always_xy=True)


def projected_distance_m(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    epsg: int | None = None,
) -> float:
    """Euclidean distance after projecting to a metric CRS (local UTM by default)."""
    if epsg is None:
        epsg = utm_epsg((lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0)
    transformer = _transformer(epsg)
    x1, y1 = transformer.transform(lon1, lat1)
    x2, y2 = transformer.transform(lon2, lat2)
    return math.hypot(x2 - x1, y2 - y1)


def naive_degree_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """BUG DEMO: Euclidean distance on raw degrees as if they were metres."""
    return math.hypot(lat2 - lat1, lon2 - lon1)


def naive_degree_scaled_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """BUG DEMO: degrees scaled by one constant, ignoring longitude shrink with latitude."""
    return math.hypot(lat2 - lat1, lon2 - lon1) * METRES_PER_DEGREE


def wrong_zone_distance_m(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    wrong_epsg: int,
) -> float:
    """BUG DEMO: projected distance using a deliberately wrong UTM zone."""
    return projected_distance_m(lat1, lon1, lat2, lon2, epsg=wrong_epsg)
