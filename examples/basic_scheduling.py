"""Basic end-to-end irrigation scheduling example."""

from datetime import date, timedelta

from irrigation_scheduler.models import (
    Crop,
    IrrigationSystem,
    Soil,
    WeatherDay,
)
from irrigation_scheduler.simulation import IrrigationSimulation


def build_weather() -> list[WeatherDay]:
    """Build a small synthetic daily weather dataset."""

    eto_values = [
        4.2,
        4.5,
        4.8,
        5.0,
        5.2,
        5.4,
        5.1,
        4.9,
        5.3,
        5.5,
        5.7,
        5.4,
        5.2,
        5.0,
    ]

    precipitation_values = [
        0.0,
        0.0,
        2.0,
        0.0,
        0.0,
        0.0,
        8.0,
        0.0,
        0.0,
        0.0,
        0.0,
        4.0,
        0.0,
        0.0,
    ]

    start_date = date(2026, 4, 1)

    return [
        WeatherDay(
            date=start_date + timedelta(days=i),
            eto=eto,
            precipitation=rain,
        )
        for i, (eto, rain) in enumerate(
            zip(
                eto_values,
                precipitation_values,
            )
        )
    ]


def main() -> None:
    """Run the basic irrigation scheduling example."""

    soil = Soil(
        field_capacity=180.0,
        wilting_point=80.0,
        initial_storage=150.0,
    )

    crop = Crop(
        kc_initial=0.40,
        kc_mid=1.15,
        kc_end=0.80,
        initial_stage_days=3,
        development_stage_days=4,
        mid_stage_days=4,
        late_stage_days=3,
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

    weather = build_weather()

    results = simulation.run(weather)

    print("\nIrrigationScheduler — Basic Example")
    print("=" * 45)

    print(
        results[
            [
                "date",
                "eto",
                "kc",
                "etc",
                "precipitation",
                "irrigation_triggered",
                "irrigation_gross",
                "soil_storage",
                "depletion",
            ]
        ].to_string(index=False)
    )

    print("\nSummary")
    print("-" * 45)

    total_rainfall = results["precipitation"].sum()
    total_etc = results["etc"].sum()
    total_actual_et = results["actual_et"].sum()
    total_net_irrigation = results["irrigation_net"].sum()
    total_gross_irrigation = results["irrigation_gross"].sum()
    total_drainage = results["drainage"].sum()
    total_deficit = results["water_deficit"].sum()
    irrigation_events = results["irrigation_triggered"].sum()

    print(f"Simulation days       : {len(results)}")
    print(f"Total rainfall        : {total_rainfall:.2f} mm")
    print(f"Total ETc             : {total_etc:.2f} mm")
    print(f"Total actual ET       : {total_actual_et:.2f} mm")
    print(f"Net irrigation        : {total_net_irrigation:.2f} mm")
    print(f"Gross irrigation      : {total_gross_irrigation:.2f} mm")
    print(f"Drainage              : {total_drainage:.2f} mm")
    print(f"Water deficit         : {total_deficit:.2f} mm")
    print(f"Irrigation events     : {irrigation_events}")


if __name__ == "__main__":
    main()