# geo_distance_arena

**As the crow flies is not how the van drives.** A head-to-head comparison of every way to
measure the distance between two places, from the one-line straight-line formula to the
real shortest path along the roads, built entirely with free, keyless, Docker-free,
pip-installable Python (OSMnx, NetworkX, geopy, Nominatim).

The moment a dataset has latitude and longitude, someone computes distance, and the default
is almost always the straight line (the great-circle "as the crow flies" number) because it
is a one-line formula over columns you already have. That number then flows into decisions
that assume it means travel distance: which depot serves which store, whether a customer is
inside a delivery radius, which branch is "nearest", what a route will cost. But the crow
does not drive. This project measures the gap, honestly and for free, on a real city.

## The result, on real geography

Measured on the drivable road network of central Copenhagen (downloaded once from
OpenStreetMap, split by the Inner Harbour that only a few bridges cross):

| Question | Straight line says | The road says |
|---|---|---|
| How much longer is the road than the straight line? | nothing | 1.37x on average, up to 3.4x at the harbour |
| Is that bias a constant you can multiply away? | yes | no: a single multiplier still leaves 30 to 70 percent error at the barriers |
| Which branch is "nearest"? | one answer | a different branch for 10.8 percent of customers, concentrated at the water |
| Who is inside a 1.5 km catchment? | 32 customers in the circle | 57 inside the 4-minute drive-time area, a very different set |

The straight-line number is not just biased low, it is unreliably biased, and it is wrong
about which facility is nearest for exactly the customers the barrier inconveniences most.

## What is inside

- **`notebooks/`** six notebooks that build the argument step by step:
  1. `01_what_distance_means` the five notions side by side, and the degrees-as-metres bug
  2. `02_road_distance_from_osm` road distance and free travel time from OSMnx + NetworkX
  3. `03_the_detour_factor` the road/straight ratio, its fat tail, and why one multiplier fails
  4. `04_the_nearest_store_flips` nearest-branch flips and the three shapes of a catchment
  5. `05_scale_and_cost` the speed/accuracy trade-off and the hybrid prefilter
  6. `06_decision_framework` when to use which metric
- **`src/`** a small library: the distance methods, the OSM graph tooling, the business
  scenarios, and the evaluation harness.
- **`app/streamlit_app.py`** an interactive distance comparator and nearest-facility viewer.
- **`outputs/figures/`** every figure saved as PNG; **`outputs/data/`** every number saved
  as JSON, so the whole analysis is reproducible from files.

## The methods

| Method | What it is | Use it for |
|---|---|---|
| Geodesic | WGS84 ellipsoid, Karney's algorithm (geopy) | the straight-line ground truth |
| Haversine | great-circle on a sphere, vectorised | fast straight-line over many points |
| Projected Euclidean | local UTM then Euclidean (pyproj) | planar work over a small area |
| Manhattan | grid proxy | a rule of thumb in gridded cities |
| Road distance and time | OSMnx graph + NetworkX shortest path | delivery cost, catchments, nearest-facility |

Never compute Euclidean distance on raw latitude and longitude, or in the wrong UTM zone:
that produces numbers that are silently and badly wrong, and the error grows with latitude.
Notebook 01 reproduces and flags it.

## Quickstart

Runs in a 2-CPU / 8 GB GitHub Codespace. No GPU, no Docker, no routing server, no API key.

```bash
make setup      # install uv, sync dependencies, register the Jupyter kernel
make graph      # one-time, online: download and cache the Copenhagen road graphs
make test       # run the test suite (offline, on the committed graph)
make notebooks  # execute all six notebooks (offline, saves PNG + JSON)
make run        # launch the Streamlit app
make ci         # what CI runs: sync + lint + test, all offline
```

`make graph` is the only step that touches the network, and only to refresh the committed
graph caches. Everything else runs offline. Geocoding (Nominatim) and the scenario points
are cached too, and the scenario rebuilds itself from the committed graph if its cache is
missing.

## How it stays free and reproducible

- **Keyless.** OSM road graphs come from the keyless Overpass API via OSMnx; geocoding uses
  keyless Nominatim. No Google, Mapbox, or HERE.
- **Docker-free and server-free.** No routing engine (OSRM, Valhalla, GraphHopper) and no
  database (PostGIS, pgRouting). Everything is in-process Python, pip wheels only.
- **Offline after a one-time build.** The road graphs are frozen to GraphML and committed, so
  notebooks, tests, and CI run with no network.
- **Asserted.** The geodesic matches the geographiclib reference to the millimetre, road
  distance is never shorter than the straight line, Dijkstra equals A*, and the
  nearest-facility flip is reproduced on a planted case.

Live-traffic ETA and a self-hosted routing engine are named as future extensions, not
claimed here. The free speed-limited travel time is a much better estimate than distance and
honestly short of a live ETA.

## Related projects

Part of a series of hands-on "arena" comparisons by the same author. This one measures
distance on the Earth; its siblings measure distance and cost elsewhere.

- [distance_arena](https://github.com/Dima806/distance_arena) compares eight distance and
  similarity measures across kNN, clustering, and retrieval. It measures distance in a
  model's feature space; this project measures it on the map, and the lesson that the metric
  you pick changes the answer is the same.
- [curse_of_dimensionality_101](https://github.com/Dima806/curse_of_dimensionality_101) shows
  how distance loses meaning in high dimensions.
- [clustering_arena](https://github.com/Dima806/clustering_arena) compares clustering
  algorithms, every one of which depends on a distance.
- [retrieval_arena](https://github.com/Dima806/retrieval_arena) compares retrieval strategies
  that rank by distance in an embedding space.
- [optimization_101](https://github.com/Dima806/optimization_101) is a hands-on introduction
  to mathematical optimization with open solvers, the kind of facility-location and routing
  model that consumes the road-distance matrix this project builds.

More at [github.com/Dima806](https://github.com/Dima806).

## License

Apache-2.0.
