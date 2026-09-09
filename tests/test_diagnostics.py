import pandas as pd
import pytest

from irrigation_scheduler.diagnostics import (
    calculate_mass_balance_error,
    validate_physical_consistency,
)
from irrigation_scheduler.models import Crop, IrrigationSystem, Soil
from irrigation_scheduler.simulation import IrrigationSimulation
from irrigation_scheduler.weather import load_weather_csv, weather_dataframe_to_days


def test_calculate_mass_balance_error() -> None:
    results = pd.DataFrame(
        {
            "initial_soil_storage": [150.0],
            "precipitation": [10.0],
            "irrigation_net": [20.0],
            "actual_et": [8.0],
            "drainage": [2.0],
            "soil_storage": [170.0],
        }
    )

    error = calculate_mass_balance_error(results)

    assert error.iloc[0] == 0.0


def test_calculate_mass_balance_error_detects_nonzero_error() -> None:
    results = pd.DataFrame(
        {
            "initial_soil_storage": [150.0],
            "precipitation": [10.0],
            "irrigation_net": [20.0],
            "actual_et": [8.0],
            "drainage": [2.0],
            "soil_storage": [169.0],
        }
    )

    error = calculate_mass_balance_error(results)

    assert error.iloc[0] == 1.0


def test_calculate_mass_balance_error_rejects_missing_columns() -> None:
    results = pd.DataFrame(
        {
            "initial_soil_storage": [150.0],
            "precipitation": [10.0],
            "irrigation_net": [20.0],
            "actual_et": [8.0],
            "drainage": [2.0],
        }
    )

    with pytest.raises(ValueError):
        calculate_mass_balance_error(results)
        
def test_validate_physical_consistency() -> None:
    results = pd.DataFrame(
        {
            "soil_storage": [150.0],
            "actual_et": [4.0],
            "etc": [5.0],
            "irrigation_net": [10.0],
            "irrigation_gross": [12.0],
            "drainage": [0.0],
            "water_deficit": [0.0],
        }
    )

    from irrigation_scheduler.diagnostics import validate_physical_consistency

    errors = validate_physical_consistency(
        results,
        wilting_point=80.0,
        field_capacity=180.0,
    )

    assert errors == []

def test_validate_physical_consistency_detects_physical_errors() -> None:
    results = pd.DataFrame(
        {
            "soil_storage": [70.0],
            "actual_et": [6.0],
            "etc": [5.0],
            "irrigation_net": [-1.0],
            "irrigation_gross": [-2.0],
            "drainage": [-0.5],
            "water_deficit": [-1.0],
        }
    )

    from irrigation_scheduler.diagnostics import validate_physical_consistency

    errors = validate_physical_consistency(
        results,
        wilting_point=80.0,
        field_capacity=180.0,
    )

    assert len(errors) == 6
    assert "soil_storage contains values below wilting_point." in errors
    assert "actual_et contains values greater than etc." in errors
    assert "irrigation_net contains negative values." in errors
    assert "irrigation_gross contains values below irrigation_net." in errors
    assert "drainage contains negative values." in errors
    assert "water_deficit contains negative values." in errors

def test_validate_physical_consistency_detects_storage_above_field_capacity() -> None:
    results = pd.DataFrame(
        {
            "soil_storage": [190.0],
            "actual_et": [4.0],
            "etc": [5.0],
            "irrigation_net": [0.0],
            "irrigation_gross": [0.0],
            "drainage": [0.0],
            "water_deficit": [0.0],
        }
    )

    from irrigation_scheduler.diagnostics import validate_physical_consistency

    errors = validate_physical_consistency(
        results,
        wilting_point=80.0,
        field_capacity=180.0,
    )

    assert "soil_storage contains values above field_capacity." in errors

def test_validate_physical_consistency_handles_multiple_days() -> None:
    results = pd.DataFrame(
        {
            "soil_storage": [150.0, 145.0, 160.0],
            "actual_et": [4.0, 5.0, 4.5],
            "etc": [5.0, 5.0, 5.0],
            "irrigation_net": [0.0, 0.0, 10.0],
            "irrigation_gross": [0.0, 0.0, 12.0],
            "drainage": [0.0, 0.0, 0.0],
            "water_deficit": [1.0, 0.0, 0.5],
        }
    )

    from irrigation_scheduler.diagnostics import validate_physical_consistency

    errors = validate_physical_consistency(
        results,
        wilting_point=80.0,
        field_capacity=180.0,
    )

    assert errors == []

def test_120_day_simulation_passes_diagnostics() -> None:
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

    mass_balance_error = calculate_mass_balance_error(
        results
    )

    physical_errors = validate_physical_consistency(
        results,
        wilting_point=soil.wilting_point,
        field_capacity=soil.field_capacity,
    )

    assert len(results) == 120
    assert mass_balance_error.abs().max() < 1e-10
    assert physical_errors == []