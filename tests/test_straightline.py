"""Geodesic matches the geographiclib reference; haversine stays within a known bound."""

from __future__ import annotations

from geographiclib.geodesic import Geodesic

from src.distance.geodesic import geodesic_distance_m
from src.distance.haversine import haversine_m

PAIRS = [
    (40.0, -74.0, 40.01, -74.02),
    (51.5074, -0.1278, 48.8566, 2.3522),  # London -> Paris
    (34.0522, -118.2437, 40.7128, -74.0060),  # Los Angeles -> New York
]


def test_geodesic_matches_geographiclib_reference() -> None:
    for lat1, lon1, lat2, lon2 in PAIRS:
        reference = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)["s12"]
        computed = geodesic_distance_m(lat1, lon1, lat2, lon2)
        assert abs(computed - reference) < 1e-3  # within a millimetre


def test_haversine_within_bound_of_geodesic() -> None:
    for lat1, lon1, lat2, lon2 in PAIRS:
        truth = geodesic_distance_m(lat1, lon1, lat2, lon2)
        haversine = haversine_m(lat1, lon1, lat2, lon2)
        relative_error = abs(haversine - truth) / truth
        assert relative_error < 0.01  # sphere vs ellipsoid: well under 1%
