"""Geo-Distance Arena -- interactive comparison of distance metrics.

Run with ``make run``. Everything is keyless and offline on cached data except the
optional live geocoding in the distance comparator (which caches every result).
"""

from __future__ import annotations

import streamlit as st

from src.distance.geodesic import geodesic_distance_m
from src.distance.haversine import haversine_m
from src.distance.manhattan import manhattan_distance_m
from src.distance.projected import naive_degree_scaled_m, projected_distance_m
from src.graph.build import build_synthetic_barrier_graph
from src.scenarios.nearest_facility import assign_nearest


def _distance_comparator() -> None:
    st.header("Distance comparator")
    st.caption("Every straight-line method on one pair of points, with the detour factor.")
    col1, col2 = st.columns(2)
    with col1:
        lat1 = st.number_input("Origin latitude", value=40.000, format="%.6f")
        lon1 = st.number_input("Origin longitude", value=-74.000, format="%.6f")
    with col2:
        lat2 = st.number_input("Destination latitude", value=40.007, format="%.6f")
        lon2 = st.number_input("Destination longitude", value=-74.003, format="%.6f")

    st.subheader("Straight-line distances (metres)")
    st.table(
        {
            "geodesic (truth)": [round(geodesic_distance_m(lat1, lon1, lat2, lon2), 2)],
            "haversine": [round(haversine_m(lat1, lon1, lat2, lon2), 2)],
            "projected": [round(projected_distance_m(lat1, lon1, lat2, lon2), 2)],
            "manhattan": [round(manhattan_distance_m(lat1, lon1, lat2, lon2), 2)],
            "naive degrees (BUG)": [round(naive_degree_scaled_m(lat1, lon1, lat2, lon2), 2)],
        }
    )


def _nearest_facility() -> None:
    st.header("Nearest facility")
    st.caption("On the planted barrier city: which branch is nearest by straight-line vs road.")
    graph = build_synthetic_barrier_graph()
    facilities = [(40.007, -74.004), (40.007, -74.000)]
    customers = [(40.007, -74.003), (40.004, -74.003), (40.001, -74.003)]
    assignments = assign_nearest(graph, facilities, customers)
    st.dataframe(assignments)
    st.metric("Flip rate", f"{assignments['flip'].mean():.0%}")


def main() -> None:
    st.set_page_config(page_title="Geo-Distance Arena", layout="wide")
    st.title("Geo-Distance Arena")
    st.write("As the crow flies is not how the van drives.")
    page = st.sidebar.radio("View", ["Distance comparator", "Nearest facility"])
    if page == "Distance comparator":
        _distance_comparator()
    else:
        _nearest_facility()


if __name__ == "__main__":
    main()
