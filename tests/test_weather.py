"""Tests for synthetic weather data generation."""

from datetime import date

import pandas as pd
import pytest

from irrigation_scheduler.weather import generate_synthetic_weather


def test_generate_synthetic_weather_returns_dataframe() -> None:
    """Generator should return a pandas DataFrame."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    assert isinstance(result, pd.DataFrame)


def test_generated_weather_has_expected_columns() -> None:
    """Generated data should contain the required weather columns."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    assert list(result.columns) == [
        "date",
        "eto",
        "precipitation",
    ]


def test_generated_weather_has_requested_number_of_days() -> None:
    """Generator should produce exactly the requested number of days."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert len(result) == 120


def test_generated_weather_dates_are_consecutive() -> None:
    """Generated dates should be consecutive."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    expected_dates = pd.date_range(
        start="2026-01-01",
        periods=10,
        freq="D",
    )

    assert list(result["date"]) == list(expected_dates)


def test_generated_weather_values_are_nonnegative() -> None:
    """ETo and precipitation must never be negative."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert (result["eto"] >= 0).all()
    assert (result["precipitation"] >= 0).all()


def test_generated_weather_is_reproducible_with_same_seed() -> None:
    """The same seed should produce identical data."""

    result_1 = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    result_2 = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    pd.testing.assert_frame_equal(result_1, result_2)


def test_different_seeds_produce_different_weather() -> None:
    """Different seeds should produce different weather realizations."""

    result_1 = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    result_2 = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=12345,
    )

    assert not result_1.equals(result_2)


def test_invalid_days_are_rejected() -> None:
    """Number of days must be positive."""

    with pytest.raises(ValueError):
        generate_synthetic_weather(
            start_date=date(2026, 1, 1),
            days=0,
            seed=27183,
        )

    with pytest.raises(ValueError):
        generate_synthetic_weather(
            start_date=date(2026, 1, 1),
            days=-10,
            seed=27183,
        )


def test_default_seed_is_reproducible() -> None:
    """Calling the generator without a seed should use a deterministic default."""

    result_1 = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=30,
    )

    result_2 = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=30,
    )

    pd.testing.assert_frame_equal(result_1, result_2)
    
def test_eto_has_reasonable_synthetic_range() -> None:
    """Synthetic ETo should remain within a plausible range."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert result["eto"].min() >= 0.5
    assert result["eto"].max() <= 8.0


def test_eto_has_daily_variability() -> None:
    """Synthetic ETo should not be constant."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert result["eto"].nunique() > 1


def test_rainfall_occurs_on_multiple_days() -> None:
    """A long synthetic series should contain multiple rainfall events."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    rainy_days = (result["precipitation"] > 0).sum()

    assert rainy_days >= 5


def test_rainfall_is_not_present_every_day() -> None:
    """Rainfall should be intermittent rather than daily."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    rainy_days = (result["precipitation"] > 0).sum()

    assert rainy_days < 120


def test_dates_are_unique() -> None:
    """Every generated day should have a unique date."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert result["date"].is_unique

def test_eto_reflects_calendar_season() -> None:
    """Synthetic ETo should reflect the calendar season."""

    winter = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=30,
        seed=27183,
    )

    summer = generate_synthetic_weather(
        start_date=date(2026, 7, 1),
        days=30,
        seed=27183,
    )

    assert summer["eto"].mean() > winter["eto"].mean()
    
def test_start_date_is_preserved() -> None:
    """The first generated date should equal the requested start date."""

    result = generate_synthetic_weather(
        start_date=date(2026, 7, 15),
        days=10,
        seed=27183,
    )

    assert result["date"].iloc[0] == pd.Timestamp("2026-07-15")


def test_dates_are_sorted() -> None:
    """Generated dates should be in ascending order."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert result["date"].is_monotonic_increasing


def test_weather_columns_have_expected_numeric_types() -> None:
    """Weather variables should use numeric dtypes."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert pd.api.types.is_numeric_dtype(result["eto"])
    assert pd.api.types.is_numeric_dtype(result["precipitation"])


def test_weather_contains_no_missing_values() -> None:
    """Generated weather data should contain no missing values."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    assert not result.isna().any().any()


def test_longer_series_contains_multiple_rainfall_events() -> None:
    """A long synthetic series should contain several rainfall events."""

    result = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=365,
        seed=27183,
    )

    rainy_days = (result["precipitation"] > 0).sum()

    assert rainy_days >= 20


def test_different_start_dates_change_seasonal_eto() -> None:
    """Changing the calendar start date should change seasonal ETo."""

    january = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=30,
        seed=27183,
    )

    july = generate_synthetic_weather(
        start_date=date(2026, 7, 1),
        days=30,
        seed=27183,
    )

    assert not january["eto"].equals(july["eto"])
    
def test_save_weather_csv_creates_file(tmp_path) -> None:
    """Weather data should be saved as a CSV file."""

    from irrigation_scheduler.weather import save_weather_csv

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    output_path = tmp_path / "weather.csv"

    save_weather_csv(weather, output_path)

    assert output_path.exists()


def test_saved_weather_csv_can_be_read_back(tmp_path) -> None:
    """Saved CSV should preserve the weather data."""

    from irrigation_scheduler.weather import save_weather_csv

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    output_path = tmp_path / "weather.csv"

    save_weather_csv(weather, output_path)

    loaded = pd.read_csv(output_path, parse_dates=["date"])

    pd.testing.assert_frame_equal(
        loaded,
        weather,
        check_dtype=False,
    )


def test_save_weather_csv_rejects_missing_columns(tmp_path) -> None:
    """CSV export should reject invalid weather data."""

    from irrigation_scheduler.weather import save_weather_csv

    invalid_data = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "eto": [4.0, 4.5, 5.0],
        }
    )

    with pytest.raises(ValueError):
        save_weather_csv(
            invalid_data,
            tmp_path / "weather.csv",
        )

def test_load_weather_csv_returns_dataframe(tmp_path) -> None:
    """A saved weather CSV should be loadable as a DataFrame."""

    from irrigation_scheduler.weather import load_weather_csv

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    output_path = tmp_path / "weather.csv"
    weather.to_csv(output_path, index=False)

    result = load_weather_csv(output_path)

    assert isinstance(result, pd.DataFrame)


def test_load_weather_csv_has_expected_columns(tmp_path) -> None:
    """Loaded weather data should have the expected columns."""

    from irrigation_scheduler.weather import load_weather_csv

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    output_path = tmp_path / "weather.csv"
    weather.to_csv(output_path, index=False)

    result = load_weather_csv(output_path)

    assert list(result.columns) == [
        "date",
        "eto",
        "precipitation",
    ]


def test_load_weather_csv_parses_dates(tmp_path) -> None:
    """The date column should be parsed as datetime."""

    from irrigation_scheduler.weather import load_weather_csv

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    output_path = tmp_path / "weather.csv"
    weather.to_csv(output_path, index=False)

    result = load_weather_csv(output_path)

    assert pd.api.types.is_datetime64_any_dtype(
        result["date"]
    )


def test_load_weather_csv_preserves_values(tmp_path) -> None:
    """Loading a CSV should preserve weather values."""

    from irrigation_scheduler.weather import load_weather_csv

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=10,
        seed=27183,
    )

    output_path = tmp_path / "weather.csv"
    weather.to_csv(output_path, index=False)

    result = load_weather_csv(output_path)

    pd.testing.assert_frame_equal(
        result,
        weather,
        check_dtype=False,
    )


def test_load_weather_csv_rejects_missing_columns(tmp_path) -> None:
    """Loading invalid weather data should raise ValueError."""

    from irrigation_scheduler.weather import load_weather_csv

    invalid_data = pd.DataFrame(
        {
            "date": pd.date_range(
                "2026-01-01",
                periods=3,
            ),
            "eto": [4.0, 4.5, 5.0],
        }
    )

    output_path = tmp_path / "invalid.csv"
    invalid_data.to_csv(output_path, index=False)

    with pytest.raises(ValueError):
        load_weather_csv(output_path)