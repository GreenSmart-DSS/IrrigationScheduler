"""Visualization utilities for irrigation simulation results."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_soil_water_storage(
    results: pd.DataFrame,
    field_capacity: float,
    wilting_point: float,
) -> plt.Figure:  # type: ignore
    """Plot soil water storage with field capacity, wilting point,
    and irrigation events.
    """

    required_columns = [
        "date",
        "soil_storage",
        "irrigation_net",
    ]

    if not all(column in results.columns for column in required_columns):
        raise ValueError(
            "results must contain the columns: " + ", ".join(required_columns) + "."
        )

    if field_capacity <= 0:
        raise ValueError("field_capacity must be greater than 0.")

    if wilting_point < 0:
        raise ValueError("wilting_point cannot be negative.")

    if wilting_point >= field_capacity:
        raise ValueError("wilting_point must be less than field_capacity.")

    figure, axis = plt.subplots(
        figsize=(10, 5),
    )

    axis.plot(
        results["date"], results["soil_storage"], label="Soil water storage", marker="."
    )

    axis.axhline(field_capacity, linestyle="--", label="Field capacity", color="green")

    axis.axhline(wilting_point, linestyle="--", label="Wilting point", color="red")

    irrigation_events = results[results["irrigation_net"] > 0]

    if not irrigation_events.empty:
        axis.scatter(
            irrigation_events["date"],
            irrigation_events["soil_storage"],
            label="Irrigation events",
            zorder=3,
            color="green",
        )

    axis.set_xlabel("Date")
    axis.set_ylabel("Soil water storage (mm)")
    axis.set_title("Soil Water Storage")
    axis.legend(loc="lower right")
    figure.tight_layout()

    return figure


def plot_depletion(
    results: pd.DataFrame,
    readily_available_water: float,
) -> plt.Figure:  # type: ignore
    """Plot soil water depletion and the irrigation trigger threshold."""

    required_columns = [
        "date",
        "depletion",
        "precipitation",
        "irrigation_net",
        "actual_et",
        "drainage",
    ]

    if not all(column in results.columns for column in required_columns):
        raise ValueError(
            "results must contain the columns: " + ", ".join(required_columns) + "."
        )

    if readily_available_water <= 0:
        raise ValueError("readily_available_water must be greater than 0.")

    # Reconstruct depletion immediately before irrigation.
    #
    # The scheduler evaluates irrigation using soil storage
    # at the start of the day, before precipitation, irrigation,
    # and actual evapotranspiration are applied.
    pre_irrigation_depletion = (
        results["depletion"]
        + results["precipitation"]
        + results["irrigation_net"]
        - results["actual_et"]
        - results["drainage"]
    )

    figure, axis = plt.subplots(
        figsize=(10, 5),
    )

    axis.plot(
        results["date"],
        results["depletion"],
        label="Depletion",
        marker=".",
    )

    axis.axhline(
        readily_available_water,
        linestyle="--",
        label="RAW threshold",
        color="k",
    )

    irrigation_events = results[results["irrigation_net"] > 0]

    if not irrigation_events.empty:
        event_depletion = pre_irrigation_depletion.loc[irrigation_events.index]

        axis.scatter(
            irrigation_events["date"],
            event_depletion,
            label="Irrigation events",
            zorder=3,
            color="green",
        )

    axis.set_xlabel("Date")
    axis.set_ylabel("Soil water depletion (mm)")
    axis.set_title("Soil Water Depletion")
    axis.legend()
    figure.tight_layout()

    return figure


def plot_water_fluxes(
    results: pd.DataFrame,
) -> plt.Figure:  # type: ignore
    """Plot daily water inputs and losses."""

    required_columns = [
        "date",
        "precipitation",
        "irrigation_net",
        "actual_et",
        "drainage",
    ]

    if not all(column in results.columns for column in required_columns):
        raise ValueError(
            "results must contain the columns: " + ", ".join(required_columns) + "."
        )

    figure, axis_left = plt.subplots(
        figsize=(10, 5),
    )

    axis_right = axis_left.twinx()

    # Water inputs: bars on the right axis
    axis_right.bar(
        results["date"],
        results["precipitation"],
        width=0.8,
        label="Precipitation",
        color="blue",
        alpha=0.6,
    )

    axis_right.bar(
        results["date"],
        results["irrigation_net"],
        width=0.8,
        label="Net irrigation",
        color="green",
        alpha=0.6,
    )

    # Water losses: lines on the left axis
    axis_left.plot(
        results["date"],
        results["actual_et"],
        label="Actual ET",
        marker=".",
    )

    axis_left.plot(
        results["date"],
        results["drainage"],
        label="Drainage",
        color="red",
        marker=".",
    )

    axis_left.set_xlabel("Date")
    axis_left.set_ylabel("Water losses (mm/day)")
    axis_right.set_ylabel("Water inputs (mm/day)")

    axis_left.set_title("Daily Water Fluxes")

    # Combine legends from both axes
    lines_left, labels_left = axis_left.get_legend_handles_labels()

    lines_right, labels_right = axis_right.get_legend_handles_labels()

    axis_left.legend(
        lines_left + lines_right, labels_left + labels_right, loc="upper left"
    )

    figure.tight_layout()

    return figure


def plot_crop_water_demand(
    results: pd.DataFrame,
) -> plt.Figure:  # type: ignore
    """Plot ETo and ETc together with Kc on a secondary axis."""

    required_columns = [
        "date",
        "eto",
        "kc",
        "etc",
    ]

    if not all(column in results.columns for column in required_columns):
        raise ValueError(
            "results must contain the columns: " + ", ".join(required_columns) + "."
        )

    figure, axis = plt.subplots(
        figsize=(10, 5),
    )

    axis.plot(
        results["date"],
        results["eto"],
        label="ETo",
        marker=".",
    )

    axis.plot(results["date"], results["etc"], label="ETc", marker=".", color="green")

    axis.set_xlabel("Date")
    axis.set_ylabel("Evapotranspiration (mm/day)")

    kc_axis = axis.twinx()

    kc_axis.plot(results["date"], results["kc"], linestyle="--", label="Kc", color="k")

    kc_axis.set_ylabel("Crop coefficient (Kc)")

    axis.set_title("Crop Water Demand")

    lines_1, labels_1 = axis.get_legend_handles_labels()
    lines_2, labels_2 = kc_axis.get_legend_handles_labels()

    axis.legend(lines_1 + lines_2, labels_1 + labels_2, frameon=True, ncol=1)

    figure.tight_layout()

    return figure


def plot_cumulative_water_balance(
    results: pd.DataFrame,
) -> plt.Figure:  # type: ignore
    """Plot cumulative water inputs and losses."""

    required_columns = [
        "date",
        "precipitation",
        "irrigation_net",
        "actual_et",
        "drainage",
    ]

    if not all(column in results.columns for column in required_columns):
        raise ValueError(
            "results must contain the columns: " + ", ".join(required_columns) + "."
        )

    cumulative_precipitation = results["precipitation"].cumsum()

    cumulative_irrigation = results["irrigation_net"].cumsum()

    cumulative_et = results["actual_et"].cumsum()

    cumulative_drainage = results["drainage"].cumsum()

    figure, axis = plt.subplots(
        figsize=(10, 5),
    )

    axis.plot(
        results["date"],
        cumulative_precipitation,
        label="Cumulative precipitation",
        color="blue",
        marker=".",
    )

    axis.plot(
        results["date"],
        cumulative_irrigation,
        label="Cumulative net irrigation",
        marker=".",
        color="green",
    )

    axis.plot(results["date"], cumulative_et, label="Cumulative actual ET", marker=".")

    axis.plot(
        results["date"],
        cumulative_drainage,
        label="Cumulative drainage",
        color="red",
        marker=".",
    )

    axis.set_xlabel("Date")
    axis.set_ylabel("Cumulative water (mm)")
    axis.set_title("Cumulative Water Balance")
    axis.legend()
    figure.tight_layout()

    return figure
