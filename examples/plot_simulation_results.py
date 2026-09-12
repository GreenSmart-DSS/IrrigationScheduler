"""Generate plots from the standard 120-day simulation."""

from pathlib import Path

import matplotlib.pyplot as plt

from irrigation_scheduler.models import (
    Crop,
    IrrigationSystem,
    Soil,
)
from irrigation_scheduler.simulation import IrrigationSimulation
from irrigation_scheduler.visualization import (
    plot_crop_water_demand,
    plot_cumulative_water_balance,
    plot_depletion,
    plot_soil_water_storage,
    plot_water_fluxes,
)
from irrigation_scheduler.weather import (
    load_weather_csv,
    weather_dataframe_to_days,
)


def main() -> None:
    """Run the standard simulation and save all visualizations."""

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

    output_directory = Path("data/figures")
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    figures = {
        "soil_water_storage": plot_soil_water_storage(
            results=results,
            field_capacity=soil.field_capacity,
            wilting_point=soil.wilting_point,
        ),
        "depletion": plot_depletion(
            results=results,
            readily_available_water=(
                simulation.scheduler.readily_available_water
            ),
        ),
        "water_fluxes": plot_water_fluxes(
            results=results,
        ),
        "crop_water_demand": plot_crop_water_demand(
            results=results,
        ),
        "cumulative_water_balance": (
            plot_cumulative_water_balance(
                results=results,
            )
        ),
    }

    for name, figure in figures.items():
        output_path = (
            output_directory / f"{name}.png"
        )

        figure.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

        plt.close(figure)

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()