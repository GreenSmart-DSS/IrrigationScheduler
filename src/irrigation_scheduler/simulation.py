"""Daily irrigation smulation engine."""

import pandas as pd

from .et import calculate_etc
from .models import Crop, IrrigationSystem, Soil, WeatherDay
from .scheduler import IrrigationScheduler
from .water_balance import WaterBalance


class IrrigationSimulation:
    """Orchestrates daily root-zone water balance and depletion-based irrigation scheduling."""
    
    def __init__(self, soil: Soil, crop: Crop, irrigation_system: IrrigationSystem, mad: float) -> None:
        
        self.soil = soil
        self.crop = crop
        
        self.water_balance = WaterBalance(soil)
        
        self.scheduler = IrrigationScheduler(
            soil=soil,
            irrigation_system=irrigation_system,
            mad=mad
        )
    
    def run(self, weather: list[WeatherDay]) -> pd.DataFrame:
        """Run the daily irrigation simulation."""
        
        if not weather:
            raise ValueError("Weather data cannot be empty.")
        
        if len(weather) > self.crop.season_length:
            raise ValueError("Weather data cannot exceed crop season length.")
        
        storage = self.soil.initial_storage
        
        records = []
        
        for day_of_season, weather_day in enumerate(weather, start=1):
            
            initial_soil_storage = storage
            
            # 1. Crop coefficient
            kc = self.crop.kc_on_day(day_of_season)
            
            # 2. Crop evapotranspiration
            etc = calculate_etc(eto=weather_day.eto, kc=kc)
            
            # 3. Determine irrigation requirement
            irrigation_decision = self.scheduler.evaluate(storage)
            
            # 4. Apply the NET irrigation to the root zone. Gross irrigation represents the amount applied. by the irrigation system and is reported separately.
            irrigation_net = irrigation_decision.net_irrigation
            irrigation_gross = irrigation_decision.gross_irrigation
            
            # 5. Perform daily water balance
            balance = self.water_balance.step(
                storage=storage,
                precipitation=weather_day.precipitation,
                irrigation=irrigation_net,
                etc=etc
            )
            
            # 6. Update storage for the next day
            storage = balance.final_storage
            
            # 7. Store daily outputs
            records.append(
                {
                    "date": weather_day.date,
                    "day_of_season": day_of_season,
                    "eto": weather_day.eto,
                    "kc": kc,
                    "etc": balance.etc,
                    "precipitation": balance.precipitation,
                    "irrigation_triggered": irrigation_decision.triggered,
                    "irrigation_net": irrigation_net,
                    "irrigation_gross": irrigation_gross,
                    "actual_et": balance.actual_et,
                    "water_deficit": balance.water_deficit,
                    "drainage": balance.drainage,
                    "initial_soil_storage": initial_soil_storage,
                    "soil_storage": balance.final_storage,
                    "depletion": balance.depletion,
                }
            )
        return pd.DataFrame(records)