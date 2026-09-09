import matplotlib.pyplot as plt
import pandas as pd
import pytest
from irrigation_scheduler.visualization import plot_soil_water_storage


def test_plot_soil_water_storage_returns_figure() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "soil_storage": [150.0, 145.0, 180.0],
            "irrigation_net": [0.0, 0.0, 35.0],
        }
    )

    figure = plot_soil_water_storage(
        results=results,
        field_capacity=180.0,
        wilting_point=80.0,
    )

    assert isinstance(figure, plt.Figure)

    plt.close(figure)


def test_plot_soil_water_storage_contains_expected_lines() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "soil_storage": [150.0, 145.0, 180.0],
            "irrigation_net": [0.0, 0.0, 35.0],
        }
    )

    figure = plot_soil_water_storage(
        results=results,
        field_capacity=180.0,
        wilting_point=80.0,
    )

    axis = figure.axes[0]

    assert len(axis.lines) >= 3

    plt.close(figure)


def test_plot_soil_water_storage_rejects_missing_columns() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "soil_storage": [150.0, 145.0, 180.0],
        }
    )

    with pytest.raises(ValueError):
        plot_soil_water_storage(
            results=results,
            field_capacity=180.0,
            wilting_point=80.0,
        )


def test_plot_soil_water_storage_rejects_invalid_soil_limits() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "soil_storage": [150.0, 145.0, 180.0],
            "irrigation_net": [0.0, 0.0, 35.0],
        }
    )

    with pytest.raises(ValueError):
        plot_soil_water_storage(
            results=results,
            field_capacity=80.0,
            wilting_point=180.0,
        )

def test_plot_soil_water_storage_with_120_day_simulation() -> None:
    from irrigation_scheduler.models import (
        Crop,
        IrrigationSystem,
        Soil,
    )
    from irrigation_scheduler.simulation import IrrigationSimulation
    from irrigation_scheduler.weather import (
        load_weather_csv,
        weather_dataframe_to_days,
    )

    weather_df = load_weather_csv(
        "data/synthetic_weather_120d.csv"
    )

    weather = weather_dataframe_to_days(
        weather_df
    )

    soil = Soil(
        field_capacity=180.0,
        wilting_point=80.0,
        initial_storage=150.0,
    )

    crop = Crop(
        kc_initial=0.40,
        kc_mid=1.15,
        kc_end=0.80,
        initial_stage_days=30,
        development_stage_days=30,
        mid_stage_days=30,
        late_stage_days=30,
    )

    irrigation_system = IrrigationSystem(
        efficiency=0.85,
    )

    simulation = IrrigationSimulation(
        soil=soil,
        crop=crop,
        irrigation_system=irrigation_system,
        mad=0.40,
    )

    results = simulation.run(weather)

    figure = plot_soil_water_storage(
        results=results,
        field_capacity=soil.field_capacity,
        wilting_point=soil.wilting_point,
    )

    assert isinstance(figure, plt.Figure)
    assert len(figure.axes) == 1

    axis = figure.axes[0]

    assert len(axis.lines) >= 3

    plt.close(figure)