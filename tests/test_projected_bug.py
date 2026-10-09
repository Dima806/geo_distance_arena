"""The projected-Euclidean bugs are reproduced and flagged, so they never ship."""

from __future__ import annotations

from src.distance.geodesic import geodesic_distance_m
from src.distance.projected import (
    naive_degree_distance_m,
    naive_degree_scaled_m,
    projected_distance_m,
    utm_epsg,
    wrong_zone_distance_m,
)

PAIR = (40.0, -74.0, 40.01, -74.02)  # ~2 km near New York


def test_degrees_as_metres_is_meaningless() -> None:
    truth = geodesic_distance_m(*PAIR)
    naive = naive_degree_distance_m(*PAIR)
    assert truth > 1000.0  # the real distance is ~2 km
    assert naive < 1.0  # degrees are not metres
    assert truth / naive > 1000.0  # off by orders of magnitude


def test_single_constant_scaling_fails_at_high_latitude() -> None:
    # A degree of longitude at 60N is about half its length at the equator, so a single
    # metres-per-degree constant roughly doubles an east-west distance here.
    high_lat = (60.0, 10.0, 60.0, 11.0)
    truth = geodesic_distance_m(*high_lat)
    scaled = naive_degree_scaled_m(*high_lat)
    assert abs(scaled - truth) / truth > 0.3


def test_wrong_utm_zone_is_wrong() -> None:
    truth = geodesic_distance_m(*PAIR)
    lat1, lon1, lat2, lon2 = PAIR
    correct_epsg = utm_epsg((lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0)
    correct = projected_distance_m(*PAIR, epsg=correct_epsg)
    wrong = wrong_zone_distance_m(*PAIR, wrong_epsg=32601)  # UTM zone 1N, far from NYC

    correct_rel = abs(correct - truth) / truth
    wrong_rel = abs(wrong - truth) / truth
    assert correct_rel < 0.01  # correct zone is near-exact over a small area
    assert wrong_rel > 0.1  # wrong zone is badly wrong
    assert wrong_rel > 10.0 * correct_rel
