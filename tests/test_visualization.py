import matplotlib.pyplot as plt
import pandas as pd
import pytest

from irrigation_scheduler.visualization import (
    plot_crop_water_demand,
    plot_cumulative_water_balance,
    plot_depletion,
    plot_soil_water_storage,
    plot_water_fluxes,
)


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

    weather_df = load_weather_csv("data/synthetic_weather_120d.csv")

    weather = weather_dataframe_to_days(weather_df)

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


def test_plot_depletion_returns_figure() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "depletion": [30.0, 40.0, 4.0],
            "precipitation": [0.0, 0.0, 0.0],
            "irrigation_net": [0.0, 0.0, 44.0],
            "actual_et": [4.0, 4.0, 4.0],
            "drainage": [0.0, 0.0, 0.0],
        }
    )

    figure = plot_depletion(
        results=results,
        readily_available_water=40.0,
    )

    assert isinstance(figure, plt.Figure)
    assert len(figure.axes) == 1

    plt.close(figure)


def test_plot_depletion_contains_expected_lines() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "depletion": [30.0, 40.0, 4.0],
            "precipitation": [0.0, 0.0, 0.0],
            "irrigation_net": [0.0, 0.0, 44.0],
            "actual_et": [4.0, 4.0, 4.0],
            "drainage": [0.0, 0.0, 0.0],
        }
    )

    figure = plot_depletion(
        results=results,
        readily_available_water=40.0,
    )

    axis = figure.axes[0]

    assert len(axis.lines) >= 2

    plt.close(figure)


def test_plot_depletion_rejects_missing_columns() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "depletion": [30.0, 40.0, 0.0],
        }
    )

    with pytest.raises(ValueError):
        plot_depletion(
            results=results,
            readily_available_water=40.0,
        )


def test_plot_depletion_rejects_invalid_raw() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "depletion": [30.0, 40.0, 0.0],
            "irrigation_net": [0.0, 0.0, 40.0],
        }
    )

    with pytest.raises(ValueError):
        plot_depletion(
            results=results,
            readily_available_water=0.0,
        )


def test_plot_water_fluxes_returns_figure() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "precipitation": [0.0, 5.0, 0.0],
            "irrigation_net": [20.0, 0.0, 25.0],
            "actual_et": [4.0, 4.5, 5.0],
            "drainage": [0.0, 0.0, 2.0],
        }
    )

    figure = plot_water_fluxes(results)

    assert isinstance(figure, plt.Figure)
    assert len(figure.axes) == 2

    plt.close(figure)


def test_plot_water_fluxes_contains_expected_series() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "precipitation": [0.0, 5.0, 0.0],
            "irrigation_net": [20.0, 0.0, 25.0],
            "actual_et": [4.0, 4.5, 5.0],
            "drainage": [0.0, 0.0, 2.0],
        }
    )

    figure = plot_water_fluxes(results)

    axis_left = figure.axes[0]
    axis_right = figure.axes[1]

    assert len(axis_left.lines) == 2
    assert len(axis_right.patches) == 6

    assert axis_left.get_ylabel() == "Water losses (mm/day)"
    assert axis_right.get_ylabel() == "Water inputs (mm/day)"

    plt.close(figure)


def test_plot_water_fluxes_rejects_missing_columns() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "precipitation": [0.0, 5.0, 0.0],
        }
    )

    with pytest.raises(ValueError):
        plot_water_fluxes(results)


def test_plot_crop_water_demand_returns_figure() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "eto": [3.0, 4.0, 5.0],
            "kc": [0.4, 0.8, 1.15],
            "etc": [1.2, 3.2, 5.75],
        }
    )

    figure = plot_crop_water_demand(results)

    assert isinstance(figure, plt.Figure)
    assert len(figure.axes) == 2

    plt.close(figure)


def test_plot_crop_water_demand_contains_expected_series() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "eto": [3.0, 4.0, 5.0],
            "kc": [0.4, 0.8, 1.15],
            "etc": [1.2, 3.2, 5.75],
        }
    )

    figure = plot_crop_water_demand(results)

    assert len(figure.axes[0].lines) >= 2
    assert len(figure.axes[1].lines) >= 1

    plt.close(figure)


def test_plot_crop_water_demand_rejects_missing_columns() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "eto": [3.0, 4.0, 5.0],
            "kc": [0.4, 0.8, 1.15],
        }
    )

    with pytest.raises(ValueError):
        plot_crop_water_demand(results)


def test_plot_cumulative_water_balance_returns_figure() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "precipitation": [0.0, 5.0, 0.0],
            "irrigation_net": [20.0, 0.0, 25.0],
            "actual_et": [4.0, 4.5, 5.0],
            "drainage": [0.0, 0.0, 2.0],
        }
    )

    figure = plot_cumulative_water_balance(results)

    assert isinstance(figure, plt.Figure)
    assert len(figure.axes) == 1

    plt.close(figure)


def test_plot_cumulative_water_balance_contains_expected_series() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "precipitation": [0.0, 5.0, 0.0],
            "irrigation_net": [20.0, 0.0, 25.0],
            "actual_et": [4.0, 4.5, 5.0],
            "drainage": [0.0, 0.0, 2.0],
        }
    )

    figure = plot_cumulative_water_balance(results)

    axis = figure.axes[0]

    assert len(axis.lines) >= 4

    plt.close(figure)


def test_plot_cumulative_water_balance_rejects_missing_columns() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "precipitation": [0.0, 5.0, 0.0],
            "irrigation_net": [20.0, 0.0, 25.0],
        }
    )

    with pytest.raises(ValueError):
        plot_cumulative_water_balance(results)


def test_all_visualizations_work_with_120_day_simulation() -> None:
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

    weather_df = load_weather_csv("data/synthetic_weather_120d.csv")

    weather = weather_dataframe_to_days(weather_df)

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

    raw = simulation.scheduler.readily_available_water

    figures = [
        plot_soil_water_storage(
            results=results,
            field_capacity=soil.field_capacity,
            wilting_point=soil.wilting_point,
        ),
        plot_depletion(
            results=results,
            readily_available_water=raw,
        ),
        plot_water_fluxes(
            results=results,
        ),
        plot_crop_water_demand(
            results=results,
        ),
        plot_cumulative_water_balance(
            results=results,
        ),
    ]

    assert len(figures) == 5

    for figure in figures:
        assert isinstance(figure, plt.Figure)
        assert len(figure.axes) >= 1
        plt.close(figure)


def test_plot_depletion_marks_pre_irrigation_depletion() -> None:
    results = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "depletion": [30.0, 40.0, 4.0],
            "precipitation": [0.0, 0.0, 0.0],
            "irrigation_net": [0.0, 0.0, 44.0],
            "actual_et": [4.0, 4.0, 4.0],
            "drainage": [0.0, 0.0, 0.0],
        }
    )

    figure = plot_depletion(
        results=results,
        readily_available_water=40.0,
    )

    axis = figure.axes[0]

    irrigation_scatter = axis.collections[0]

    offsets = irrigation_scatter.get_offsets()

    assert len(offsets) == 1
    assert offsets[0, 1] == pytest.approx(44.0)

    plt.close(figure)
