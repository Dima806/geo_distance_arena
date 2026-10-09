"""Geodesic (ellipsoidal) straight-line distance: the near-exact ground truth.

Uses geopy's ``geodesic``, which implements Karney's geographiclib algorithm on the
WGS84 ellipsoid (accurate to the millimetre). Every other straight-line method in this
project is measured against this one.
"""

from __future__ import annotations

from geopy.distance import geodesic as _geopy_geodesic


def geodesic_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the geodesic (WGS84 ellipsoid) distance between two points, in metres."""
    return float(_geopy_geodesic((lat1, lon1), (lat2, lon2)).meters)
