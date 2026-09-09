"""Visualization utilities for irrigation simulation results."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_soil_water_storage(
    results: pd.DataFrame,
    field_capacity: float,
    wilting_point: float,
) -> plt.Figure:
    """Plot soil water storage with field capacity, wilting point,
    and irrigation events.
    """

    required_columns = [
        "date",
        "soil_storage",
        "irrigation_net",
    ]

    if not all(
        column in results.columns
        for column in required_columns
    ):
        raise ValueError(
            "results must contain the columns: "
            + ", ".join(required_columns)
            + "."
        )

    if field_capacity <= 0:
        raise ValueError(
            "field_capacity must be greater than 0."
        )

    if wilting_point < 0:
        raise ValueError(
            "wilting_point cannot be negative."
        )

    if wilting_point >= field_capacity:
        raise ValueError(
            "wilting_point must be less than field_capacity."
        )

    figure, axis = plt.subplots(
        figsize=(10, 5),
    )

    axis.plot(
        results["date"],
        results["soil_storage"],
        label="Soil water storage",
    )

    axis.axhline(
        field_capacity,
        linestyle="--",
        label="Field capacity",
    )

    axis.axhline(
        wilting_point,
        linestyle="--",
        label="Wilting point",
    )

    irrigation_events = results[
        results["irrigation_net"] > 0
    ]

    if not irrigation_events.empty:
        axis.scatter(
            irrigation_events["date"],
            irrigation_events["soil_storage"],
            label="Irrigation events",
            zorder=3,
        )

    axis.set_xlabel("Date")
    axis.set_ylabel("Soil water storage (mm)")
    axis.set_title("Soil Water Storage")
    axis.legend()
    figure.tight_layout()

    return figure