"""Keyless geocoding via Nominatim, with a polite rate limit and an on-disk cache.

Nominatim is keyless fair-use, not a bulk endpoint. This wrapper caches every result to
JSON so an address is geocoded once and everything afterwards runs offline, and it
rate-limits live calls with a custom user agent. Pass ``allow_network=False`` to assert a
lookup is served purely from cache (as tests and CI require).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Callable


class Geocoder:
    """Address -> (lat, lon) with a committed on-disk cache."""

    def __init__(
        self,
        user_agent: str | None = None,
        cache_dir: Path | str | None = None,
        min_delay_seconds: float | None = None,
    ) -> None:
        settings = get_settings()
        self.user_agent = user_agent or settings.geocode.user_agent
        self.cache_dir = (
            Path(cache_dir) if cache_dir is not None else Path(settings.geocode.cache_dir)
        )
        self.min_delay_seconds = (
            min_delay_seconds
            if min_delay_seconds is not None
            else settings.geocode.min_delay_seconds
        )
        self.cache_path = self.cache_dir / "geocode_cache.json"
        self._cache: dict[str, list[float]] = self._load_cache()
        self._geocode_fn: Callable[[str], Any] | None = None

    def _load_cache(self) -> dict[str, list[float]]:
        if self.cache_path.exists():
            return json.loads(self.cache_path.read_text())
        return {}

    def _save_cache(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self._cache, indent=2, sort_keys=True))

    def _ensure_backend(self) -> None:
        if self._geocode_fn is None:
            from geopy.extra.rate_limiter import RateLimiter
            from geopy.geocoders import Nominatim

            nominatim = Nominatim(user_agent=self.user_agent)
            self._geocode_fn = RateLimiter(
                nominatim.geocode, min_delay_seconds=self.min_delay_seconds
            )

    def geocode(self, address: str, *, allow_network: bool = True) -> tuple[float, float]:
        """Return ``(lat, lon)`` for ``address``, from cache or (if allowed) Nominatim."""
        if address in self._cache:
            lat, lon = self._cache[address]
            return lat, lon
        if not allow_network:
            msg = f"{address!r} not in geocode cache and network access is disabled"
            raise KeyError(msg)
        self._ensure_backend()
        assert self._geocode_fn is not None
        location = self._geocode_fn(address)
        if location is None:
            msg = f"Nominatim could not geocode: {address!r}"
            raise ValueError(msg)
        lat = float(location.latitude)
        lon = float(location.longitude)
        self._cache[address] = [lat, lon]
        self._save_cache()
        return lat, lon


def main() -> None:
    """``make geocode`` entry point: resolve and cache a few example addresses."""
    geocoder = Geocoder()
    examples = [
        "Carnegie Mellon University, Pittsburgh",
        "University of Pittsburgh, Pittsburgh",
        "PNC Park, Pittsburgh",
    ]
    for address in examples:
        try:
            lat, lon = geocoder.geocode(address)
        except (ValueError, KeyError) as exc:
            print(f"skip {address!r}: {exc}")
        else:
            print(f"{address!r} -> ({lat:.5f}, {lon:.5f})")


if __name__ == "__main__":
    main()
