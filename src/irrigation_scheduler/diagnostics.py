"""Diagnostics and validation utilities."""

import pandas as pd


def calculate_mass_balance_error(
    results: pd.DataFrame,
) -> pd.Series:
    """Calculate daily root-zone water mass-balance error."""

    required_columns = [
        "initial_soil_storage",
        "precipitation",
        "irrigation_net",
        "actual_et",
        "drainage",
        "soil_storage",
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

    return (
        results["initial_soil_storage"]
        + results["precipitation"]
        + results["irrigation_net"]
        - results["actual_et"]
        - results["drainage"]
        - results["soil_storage"]
    )