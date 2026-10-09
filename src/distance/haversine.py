"""Haversine (great-circle) straight-line distance on a sphere.

Built from the classic formula, vectorised with numpy so it runs over whole columns at
once. Fast and cheap, with a small, measurable error versus the geodesic truth that the
arena quantifies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray

# Mean Earth radius (IUGG), the conventional value for great-circle distance.
EARTH_RADIUS_M = 6_371_008.8


def haversine_distance_m(
    lat1: ArrayLike,
    lon1: ArrayLike,
    lat2: ArrayLike,
    lon2: ArrayLike,
) -> NDArray[np.float64]:
    """Great-circle distance in metres. Accepts scalars or broadcastable arrays."""
    lat1r = np.radians(np.asarray(lat1, dtype=float))
    lon1r = np.radians(np.asarray(lon1, dtype=float))
    lat2r = np.radians(np.asarray(lat2, dtype=float))
    lon2r = np.radians(np.asarray(lon2, dtype=float))
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1r) * np.cos(lat2r) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Scalar convenience wrapper returning a plain ``float``."""
    return float(haversine_distance_m(lat1, lon1, lat2, lon2))
