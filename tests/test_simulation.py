from datetime import date, timedelta

import pandas as pd
import pytest

from irrigation_scheduler.models import (
    Crop,
    IrrigationSystem,
    Soil,
    WeatherDay,
)
from irrigation_scheduler.simulation import IrrigationSimulation


def make_soil(initial_storage=80.0):
    return Soil(
        field_capacity=100.0,
        wilting_point=40.0,
        initial_storage=initial_storage,
    )


def make_crop():
    return Crop(
        kc_initial=1.0,
        kc_mid=1.0,
        kc_end=1.0,
        initial_stage_days=1,
        development_stage_days=1,
        mid_stage_days=1,
        late_stage_days=1,
    )


def make_weather(n_days=3, eto=5.0, precipitation=0.0):
    start = date(2026, 1, 1)

    return [
        WeatherDay(
            date=start + timedelta(days=i),
            eto=eto,
            precipitation=precipitation,
        )
        for i in range(n_days)
    ]


def make_simulation(
    initial_storage=80.0,
    efficiency=1.0,
    mad=0.5,
):
    soil = make_soil(initial_storage=initial_storage)

    crop = make_crop()

    irrigation_system = IrrigationSystem(
        efficiency=efficiency
    )

    return IrrigationSimulation(
        soil=soil,
        crop=crop,
        irrigation_system=irrigation_system,
        mad=mad,
    )


def test_simulation_returns_dataframe():
    simulation = make_simulation()

    result = simulation.run(
        make_weather()
    )

    assert isinstance(result, pd.DataFrame)


def test_simulation_has_expected_columns():
    simulation = make_simulation()

    result = simulation.run(
        make_weather()
    )

    expected_columns = [
        "date",
        "day_of_season",
        "eto",
        "kc",
        "etc",
        "precipitation",
        "irrigation_triggered",
        "irrigation_net",
        "irrigation_gross",
        "actual_et",
        "water_deficit",
        "drainage",
        "soil_storage",
        "depletion",
    ]

    assert list(result.columns) == expected_columns


def test_simulation_number_of_rows_matches_weather():
    simulation = make_simulation()

    weather = make_weather(n_days=3)

    result = simulation.run(weather)

    assert len(result) == 3


def test_simulation_calculates_etc():
    simulation = make_simulation()

    weather = make_weather(
        n_days=1,
        eto=6.0,
    )

    result = simulation.run(weather)

    assert result.loc[0, "kc"] == pytest.approx(1.0)
    assert result.loc[0, "etc"] == pytest.approx(6.0)


def test_simulation_updates_soil_storage():
    simulation = make_simulation(
        initial_storage=80.0,
        mad=0.9,
    )

    weather = make_weather(
        n_days=1,
        eto=5.0,
    )

    result = simulation.run(weather)

    assert result.loc[0, "soil_storage"] == pytest.approx(75.0)


def test_simulation_triggers_irrigation_when_raw_is_reached():
    simulation = make_simulation(
        initial_storage=80.0,
        mad=0.5,
    )

    weather = make_weather(
        n_days=3,
        eto=5.0,
    )

    result = simulation.run(weather)

    assert not result.loc[0, "irrigation_triggered"]
    assert not result.loc[1, "irrigation_triggered"]
    assert bool(result.loc[2, "irrigation_triggered"])


def test_simulation_records_net_and_gross_irrigation():
    simulation = make_simulation(
        initial_storage=80.0,
        efficiency=0.5,
        mad=0.5,
    )

    weather = make_weather(
        n_days=2,
        eto=5.0,
    )

    result = simulation.run(weather)

    # At the beginning of day 2:
    # FC = 100
    # storage = 75
    # depletion = 25
    # RAW = 0.5 * (100 - 40) = 30
    #
    # Therefore irrigation should not yet be triggered.
    assert not result.loc[1, "irrigation_triggered"]

    # Day 3 should trigger irrigation.
    result = simulation.run(
        make_weather(n_days=3, eto=5.0)
    )

    assert bool(result.loc[2, "irrigation_triggered"])
    assert result.loc[2, "irrigation_net"] == pytest.approx(30.0)
    assert result.loc[2, "irrigation_gross"] == pytest.approx(60.0)


def test_net_irrigation_is_used_in_water_balance():
    simulation = make_simulation(
        initial_storage=80.0,
        efficiency=0.5,
        mad=0.5,
    )

    weather = make_weather(
        n_days=3,
        eto=5.0,
    )

    result = simulation.run(weather)

    # Start of day 3:
    # storage = 70 mm
    # depletion = 30 mm
    # net irrigation = 30 mm
    # ETc = 5 mm
    #
    # Final storage = 70 + 30 - 5 = 95 mm
    assert result.loc[2, "soil_storage"] == pytest.approx(95.0)


def test_rainfall_can_produce_drainage():
    simulation = make_simulation(
        initial_storage=95.0,
        mad=0.9,
    )

    weather = make_weather(
        n_days=1,
        eto=0.0,
        precipitation=10.0,
    )

    result = simulation.run(weather)

    assert result.loc[0, "drainage"] == pytest.approx(5.0)
    assert result.loc[0, "soil_storage"] == pytest.approx(100.0)


def test_simulation_tracks_depletion():
    simulation = make_simulation(
        initial_storage=80.0,
        mad=0.9,
    )

    weather = make_weather(
        n_days=1,
        eto=5.0,
    )

    result = simulation.run(weather)

    assert result.loc[0, "depletion"] == pytest.approx(25.0)


def test_simulation_rejects_empty_weather():
    simulation = make_simulation()

    with pytest.raises(ValueError):
        simulation.run([])


def test_simulation_rejects_weather_longer_than_crop_season():
    simulation = make_simulation()

    weather = make_weather(
        n_days=5,
    )

    with pytest.raises(ValueError):
        simulation.run(weather)


def test_simulation_uses_day_of_season():
    simulation = make_simulation()

    weather = make_weather(
        n_days=4,
    )

    result = simulation.run(weather)

    assert result["day_of_season"].tolist() == [1, 2, 3, 4]


def test_simulation_preserves_weather_dates():
    simulation = make_simulation()

    weather = make_weather(
        n_days=3,
    )

    result = simulation.run(weather)

    assert result["date"].tolist() == [
        item.date for item in weather
    ]