"""Nearest-facility ranking flips: how often, and how close to the barrier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.distance.haversine import haversine_m

if TYPE_CHECKING:
    import pandas as pd


def flip_rate(assignments: pd.DataFrame) -> float:
    """Fraction of customers whose nearest facility differs by metric."""
    return float(assignments["flip"].mean())


def distance_to_meridian_m(assignments: pd.DataFrame, barrier_lon: float) -> list[float]:
    """Approximate distance (metres) of each customer to a north-south barrier line.

    Used to show flips concentrate near the barrier.
    """
    return [
        haversine_m(lat, lon, lat, barrier_lon)
        for lat, lon in zip(assignments["lat"], assignments["lon"], strict=False)
    ]
