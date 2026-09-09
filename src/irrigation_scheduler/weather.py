"""Synthetic weather data generation."""

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_SEED = 27183


def generate_synthetic_weather(
    start_date: date,
    days: int,
    seed: int | None = DEFAULT_SEED,
) -> pd.DataFrame:
    """Generate a reproducible synthetic daily weather dataset.

    Parameters
    ----------
    start_date:
        First date of the generated weather series.
    days:
        Number of consecutive days to generate.
    seed:
        Random seed used to make the generated dataset reproducible.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing ``date``, ``eto``, and ``precipitation``.
    """

    if days <= 0:
        raise ValueError("days must be greater than 0.")

    rng = np.random.default_rng(seed)

    dates = pd.date_range(
        start=start_date,
        periods=days,
        freq="D",
    )

    day_of_year = dates.dayofyear.to_numpy()

    # Smooth seasonal variation in reference evapotranspiration based on calendar day.
    seasonal_signal = 1.5 * np.sin(
        2 * np.pi * (day_of_year - 80) / 365.0
    )

    # Day-to-day weather variability.
    eto_noise = rng.normal(
        loc=0.0,
        scale=0.45,
        size=days,
    )

    eto = 4.5 + seasonal_signal + eto_noise

    # ETo cannot be negative.
    eto = np.clip(eto, 0.5, None)

    # Generate intermittent rainfall events.
    rain_event = rng.random(days) < 0.18

    rainfall_amount = rng.gamma(
        shape=1.8,
        scale=5.0,
        size=days,
    )

    precipitation = np.where(
        rain_event,
        rainfall_amount,
        0.0,
    )

    return pd.DataFrame(
        {
            "date": dates,
            "eto": eto,
            "precipitation": precipitation,
        }
    )

def save_weather_csv(
    weather: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Save a weather dataset to a CSV file.

    Parameters
    ----------
    weather:
        Weather DataFrame containing ``date``, ``eto``, and
        ``precipitation`` columns.
    output_path:
        Destination path for the CSV file.
    """

    required_columns = [
        "date",
        "eto",
        "precipitation",
    ]

    if not all(
        column in weather.columns
        for column in required_columns
    ):
        raise ValueError(
            "weather must contain the columns: "
            "date, eto, precipitation."
        )

    weather[
        required_columns
    ].to_csv(
        output_path,
        index=False,
    )