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