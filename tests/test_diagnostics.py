import pandas as pd
import pytest

from irrigation_scheduler.diagnostics import calculate_mass_balance_error


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