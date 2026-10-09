"""Typed project configuration loaded from ``config/settings.yaml``.

Cities, travel-speed assumptions, the Nominatim user-agent, and seeds live in YAML so
modules and notebooks never hard-code them.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"


class GeocodeSettings(BaseModel):
    """Nominatim geocoding: polite rate-limit and on-disk cache (keyless)."""

    user_agent: str
    min_delay_seconds: float = 1.1
    cache_dir: Path = Path("data/geocoded")


class CitySettings(BaseModel):
    """A single OSM area to download and cache, as a center point plus a radius."""

    name: str
    center_lat: float
    center_lon: float
    dist_m: float = 2000.0


class GraphSettings(BaseModel):
    """Where cached road graphs live and which places/modes to build."""

    cache_dir: Path = Path("data/graphs")
    cities: list[CitySettings] = []
    network_types: list[str] = ["drive"]


class SpeedSettings(BaseModel):
    """Speed assumptions (km/h) used to turn road distance into travel time."""

    default_kph: float = 50.0
    by_highway: dict[str, float] = {}


class Settings(BaseModel):
    """Top-level project settings."""

    seed: int = 42
    geocode: GeocodeSettings
    graph: GraphSettings
    speeds: SpeedSettings


def load_settings(path: Path | None = None) -> Settings:
    """Load and validate settings from ``path`` (defaults to ``config/settings.yaml``)."""
    settings_path = path or DEFAULT_SETTINGS_PATH
    data = yaml.safe_load(settings_path.read_text())
    return Settings.model_validate(data)


@lru_cache
def get_settings() -> Settings:
    """Return cached project settings."""
    return load_settings()
