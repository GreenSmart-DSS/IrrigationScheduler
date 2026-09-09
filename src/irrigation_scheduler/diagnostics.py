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

def validate_physical_consistency(
    results: pd.DataFrame,
    wilting_point: float,
    field_capacity: float,
) -> list[str]:
    """Check basic physical consistency of simulation results."""

    required_columns = [
        "soil_storage",
        "actual_et",
        "etc",
        "irrigation_net",
        "irrigation_gross",
        "drainage",
        "water_deficit",
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

    errors = []

    if (results["soil_storage"] < wilting_point).any():
        errors.append(
            "soil_storage contains values below wilting_point."
        )

    if (results["soil_storage"] > field_capacity).any():
        errors.append(
            "soil_storage contains values above field_capacity."
        )

    if (results["actual_et"] > results["etc"]).any():
        errors.append(
            "actual_et contains values greater than etc."
        )

    if (results["irrigation_net"] < 0).any():
        errors.append(
            "irrigation_net contains negative values."
        )

    if (results["irrigation_gross"] < results["irrigation_net"]).any():
        errors.append(
            "irrigation_gross contains values below irrigation_net."
        )

    if (results["drainage"] < 0).any():
        errors.append(
            "drainage contains negative values."
        )

    if (results["water_deficit"] < 0).any():
        errors.append(
            "water_deficit contains negative values."
        )

    return errors