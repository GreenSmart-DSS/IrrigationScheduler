"""Generate the standard synthetic weather dataset."""

from datetime import date
from pathlib import Path

from irrigation_scheduler.weather import (
    generate_synthetic_weather,
    save_weather_csv,
)


def main() -> None:
    """Generate and save a reproducible 120-day weather dataset."""

    weather = generate_synthetic_weather(
        start_date=date(2026, 1, 1),
        days=120,
        seed=27183,
    )

    output_path = Path("data/synthetic_weather_120d.csv")

    save_weather_csv(
        weather=weather,
        output_path=output_path,
    )

    print(f"Saved {len(weather)} days to: {output_path}")
    print(f"Date range: {weather['date'].min().date()} → {weather['date'].max().date()}")
    print(f"Total ETo: {weather['eto'].sum():.2f} mm")
    print(f"Total precipitation: {weather['precipitation'].sum():.2f} mm")
    print(f"Rainy days: {(weather['precipitation'] > 0).sum()}")


if __name__ == "__main__":
    main()