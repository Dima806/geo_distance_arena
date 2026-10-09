"""Save notebook artifacts consistently: figures as PNG, results as JSON.

Every notebook writes its visuals to ``outputs/figures/`` and its textual/numerical
results to ``outputs/data/`` through these helpers, so the whole analysis is reproducible
from files rather than from notebook scrollback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from src.config import PROJECT_ROOT

if TYPE_CHECKING:
    from matplotlib.figure import Figure

FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
DATA_DIR = PROJECT_ROOT / "outputs" / "data"


def _json_default(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    msg = f"not JSON serialisable: {type(value)!r}"
    raise TypeError(msg)


def save_fig(fig: Figure, name: str, dpi: int = 150) -> Path:
    """Save a matplotlib figure as PNG under ``outputs/figures/`` and return its path."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / (name if name.endswith(".png") else f"{name}.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path


def save_json(obj: Any, name: str) -> Path:
    """Save a JSON-serialisable object under ``outputs/data/`` and return its path."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / (name if name.endswith(".json") else f"{name}.json")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=_json_default))
    return path
