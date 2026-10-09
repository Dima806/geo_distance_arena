# CLAUDE.md - geo_distance_arena

Guidance for working in this repository. Read this before writing code, notebooks, or docs.
The spec is [.llm/PRD_geo_distance_arena.md](.llm/PRD_geo_distance_arena.md); this file is the
operational summary of what actually exists. When they disagree, this file describes reality.

## 1. What this project is

A head-to-head arena comparing every way to measure distance between two places on Earth,
from the one-line straight-line formula to the real shortest path along the roads, built
entirely with free, keyless, Docker-free, pip-installable Python.

Thesis, defended with measured numbers (never asserted):

- Straight-line ("as the crow flies") distance underestimates road distance by about a third
  on average and by multiples at barriers (rivers, harbours, highways).
- The bias has large, spatially structured variance, so a single average multiplier does not
  fix it: the barrier cases stay wrong.
- The straight-line "nearest" facility is often not the road-nearest; assignments flip a
  double-digit percentage of the time, concentrated at barriers.
- Honest road distance, and even a free travel-time estimate from a speed-limited graph, cost
  nothing but CPU and a one-time download.

Audience: data scientists in logistics, delivery, retail siting, field service, and
marketplaces. This is a portfolio project, so clarity and correctness beat cleverness.

## 2. Current status

Built and working: the `src/` library, all six notebooks (executed, with saved outputs), the
Streamlit app, the test suite, the config, and the committed Copenhagen road graphs. `make ci`
passes (sync, lint, type-check, 12 tests), offline.

The real-world example is **central Copenhagen** (set in `config/settings.yaml` as a center
point plus a radius). Its Inner Harbour, crossed by only a few road bridges, drives the
barrier effect. To change the city, edit the `graph` block in the config and run `make graph`.

## 3. Hard constraints (non-negotiable; they are the project's premise)

- **Keyless.** OSM graphs via the keyless Overpass API (OSMnx); geocoding via keyless
  Nominatim. No Google, Mapbox, or HERE. No tokens or registration.
- **Docker-free and server-free.** No routing engine (OSRM, Valhalla, GraphHopper), no
  database (PostGIS, pgRouting). Everything is in-process Python.
- **pip-only.** Pure pip wheels, managed by `uv`. No system GDAL. Never `pip install` directly.
- **2-CPU / 8 GB, no GPU.** Keep one city graph and a few hundred points in memory.
- **Offline after a one-time build.** Only `make graph` (and `make geocode`) touch the network.
  The road graphs are frozen to GraphML and committed; notebooks, tests, and CI run offline.
- **Python 3.11+** (the venv is pinned to 3.12 for full geospatial wheel coverage).

Live-traffic ETA and self-hosted routing engines are future extensions, out of scope. Name
them as such; never claim this project gives production ETAs.

## 4. Stack

Core (all free/keyless/pip): `osmnx` (OSM graphs via Overpass), `networkx` (shortest path),
`geopy` + `geographiclib` (geodesic truth; Nominatim), `shapely` / `geopandas` / `pyproj`
(geometry and projection), `scikit-learn` BallTree (fast haversine nearest-neighbour),
`folium` (interactive maps in the app). Support: `numpy`, `scipy`, `pandas`, `matplotlib`,
`plotly`, `streamlit`, `pydantic`, `pyyaml`. Dev: `pytest`, `ruff`, `ty`, `jupyter`, `nbformat`.

## 5. Commands (Makefile)

Always go through the Makefile / `uv`; never call `python` or `pip` bare.

| Command | Purpose |
|---|---|
| `make setup` | install `uv`, `uv sync --all-extras`, register the Jupyter kernel |
| `make graph` | one-time online: download and cache the city road graphs (drive/walk/bike) |
| `make geocode` | one-time online: resolve and cache addresses (Nominatim, polite) |
| `make lint` | `ruff format` + `ruff check --fix` + `ty check src/` |
| `make test` / `make test-cov` | pytest, offline on the committed graph |
| `make notebooks` | execute all six notebooks offline; saves PNG and JSON |
| `make run` | Streamlit app |
| `make ci` | sync + lint + test (what CI runs, offline) |

Definition of done: `make lint` and `make test` pass, and any affected notebook still executes
under `make notebooks`.

## 6. Layout and module responsibilities

```
config/settings.yaml      City center/radius, travel speeds, Nominatim user-agent, seeds
src/config.py             Typed settings (pydantic) loaded from the YAML
src/io_utils.py           save_fig() -> outputs/figures/*.png, save_json() -> outputs/data/*.json
src/distance/
  geodesic.py             Ellipsoidal straight line (Karney) - the straight-line TRUTH
  haversine.py            Great-circle, vectorised (numpy)
  projected.py            Local-UTM Euclidean + the degrees-as-metres / wrong-zone BUG demos
  manhattan.py            Grid proxy
  road.py                 NetworkX shortest path on a graph: distance, travel time, A*; edge speeds
src/geocode/nominatim.py  Cache-first geocoder; allow_network=False forces offline
src/graph/
  build.py                build_synthetic_barrier_graph (tests), build_graph_from_point,
                          load_city_graph (loads cache, rebuilds online on miss), save_graphml
  snap.py                 SnapIndex (BallTree haversine) + snapping error
  matrix.py               Road matrix (Dijkstra per origin), straight-line matrix, BallTree prefilter
  isochrone.py            Reachable-within-T subgraph -> catchment polygon
src/scenarios/
  points.py               Deterministic depot/customers/facilities from graph nodes; cached JSON
  delivery.py             Depot -> customers: straight-line vs road
  catchment.py            Circle vs road-distance vs drive-time isochrone
  nearest_facility.py     assign_nearest (handles unreachable nodes as inf); flips
  cost_matrix.py          Cost estimation + the single-multiplier residual
src/evaluation/           error_vs_truth, detour_factor, ranking_flips, scale_cost, comparison
src/visualisation.py      folium maps + matplotlib (used by the app)
app/streamlit_app.py      Distance comparator + nearest-facility viewer
notebooks/01..06          Narrative; thin callers of src
data/graphs/*.graphml     Committed, frozen road graphs (offline thereafter)
data/geocoded/*.json      Geocode + scenario cache (GIT-IGNORED; rebuilt offline from the graph)
outputs/figures/*.png     Saved figures (deliverables)
outputs/data/*.json       Saved numbers (deliverables)
tests/                    Four offline test files (see section 8)
```

Keep logic in `src/`; notebooks and the app are thin callers. Notebooks render maps with
matplotlib / `osmnx.plot_graph` so every visual saves as a real PNG headlessly; folium stays
in the app, where interactivity helps. Every notebook saves its figures with `save_fig` and
its numbers with `save_json`.

## 7. Domain concepts and invariants

"Straight-line" is several distinct things: geodesic (ellipsoid, near-exact TRUTH), haversine
(sphere), projected Euclidean (local UTM), Manhattan (grid proxy).

Uphold and assert:

- Road distance (OSMnx graph + NetworkX) is never shorter than the straight line.
- Detour factor (road / straight) averages about 1.3 to 1.4 with a fat tail (2, 3, 4+) at
  barriers. Report it as a distribution, not one number.
- The variance is spatially structured, so a single multiplier leaves barrier cases wrong.
- Nearest-facility assignment flips a double-digit percentage of the time, at barriers.
- Distance is not time. Free travel time weights edges by speed limit
  (`src.distance.road.add_edge_speeds` / `add_edge_travel_times`). Live traffic needs a routing
  engine (out of scope).
- Road distance is asymmetric on one-ways; straight-line is symmetric. Drive/walk/bike differ.
- Scale: straight-line is vectorised and a BallTree is instant; road is a shortest-path search
  per pair. The practitioner's answer is the hybrid: straight-line prefilter, then road rank.

Never ship: Euclidean distance on raw degrees, or in the wrong UTM zone. Notebook 01 and
`test_projected_bug.py` reproduce and flag it.

## 8. Tests and reproducibility

`tests/` run offline. The road tests use a deterministic planted barrier graph
(`build_synthetic_barrier_graph`), so no city download is needed to test:

- `test_straightline.py` geodesic matches the geographiclib reference to the millimetre;
  haversine within a stated bound.
- `test_projected_bug.py` degrees-as-metres and wrong-UTM errors reproduced and flagged.
- `test_road.py` Dijkstra == A*; road >= straight-line for all pairs; cross-barrier detour large.
- `test_flips.py` a planted flip occurs and sits at the barrier.

The city graphs are committed (`data/graphs/*.graphml`). The scenario JSON and geocode cache
are git-ignored and rebuild themselves offline from the committed graph, so they need not be
committed to stay reproducible.

## 9. Conventions

- `uv` for deps, `ruff` for format and lint (line length 99; `E,F,W,I,UP,N,B,A,SIM,PTH`; E501
  ignored), `ty` for type-checking `src/`. Run `make lint` before calling anything done.
- Config, not constants: city, speeds, Nominatim user-agent, and seeds live in
  `config/settings.yaml`, loaded through `src/config.py`.
- Paths use `pathlib` (PTH is enforced).
- Politeness: Nominatim and Overpass are keyless fair-use, not bulk endpoints. Always use the
  custom user-agent, a rate limit, and the cache. Never bulk-geocode the public endpoint.
- Outputs: figures as PNG in `outputs/figures/`, numbers as JSON in `outputs/data/`, both via
  `src/io_utils.py`.
- Prose style for docs, READMEs, and articles: plain, concrete, practitioner-facing. Avoid
  em dashes and other known tells of AI-assisted writing; prefer commas, hyphens, parentheses,
  and short sentences.

## 10. Related projects (confirmed to exist)

This produces the real road-distance (and time) matrix that optimization models assume.

- [distance_arena](https://github.com/Dima806/distance_arena): feature-space distance and
  similarity (this project is the Earth-surface counterpart).
- [curse_of_dimensionality_101](https://github.com/Dima806/curse_of_dimensionality_101): how
  distance loses meaning in high dimensions.
- [clustering_arena](https://github.com/Dima806/clustering_arena) and
  [retrieval_arena](https://github.com/Dima806/retrieval_arena): methods that rank by distance.
- [optimization_101](https://github.com/Dima806/optimization_101): optimization with open
  solvers, the facility-location and routing models that consume a distance matrix.

(The PRD also references supply_chain_arena, routing_arena, and threshold_lab; link them only
after confirming the repositories exist.)
