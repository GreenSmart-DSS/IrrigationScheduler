"""Daily root-zone water balance and depletion-based irrigation scheduling."""

from dataclasses import dataclass

from .models import Soil


@dataclass(frozen=True)
class WaterBalanceResult:
    """Results of one daily root-zone water balance calculation.
    """
    
    initial_storage: float
    precipitation: float
    irrigation: float
    etc: float
    actual_et: float
    drainage: float
    final_storage: float
    depletion: float
    water_deficit: float


class WaterBalance:
    """Daily root-zone water balance engine.
    """
    
    def __init__(self, soil: Soil) -> None:
        self.soil = soil
        
    def step(
        self,
        storage: float,
        precipitation: float,
        irrigation: float,
        etc: float,
    ) -> WaterBalanceResult:
        """Perform one daily root-zone water balance calculation.
        """
        
        if storage < self.soil.wilting_point:
            raise ValueError("Storage cannot be less than wilting point.")
        
        if storage > self.soil.field_capacity:
            raise ValueError("Storage cannot be greater than field capacity.")
        
        if precipitation < 0:
            raise ValueError("Precipitation cannot be negative.")
        
        if irrigation < 0:
            raise ValueError("Irrigation cannot be negative.")
        
        if etc < 0:
            raise ValueError("ETc cannot be negative.")
        
        initial_storage = storage
        
        # Add incoming water.
        storage += precipitation + irrigation
        
        # water above field capacity becomes drainage.
        drainage = max(0.0, storage - self.soil.field_capacity)
        storage = min(storage, self.soil.field_capacity)
        
        # Available water above wilting point.
        available_water = storage - self.soil.wilting_point
        
        # Actual ET cannot exceed available soil water.
        actual_et = min(etc, available_water)
        water_deficit = etc - actual_et
        storage -= actual_et
        
        # Numerical safety.
        storage = max(storage, self.soil.wilting_point)
        depletion = self.soil.field_capacity - storage
        
        return WaterBalanceResult(
            initial_storage=initial_storage,
            precipitation=precipitation,
            irrigation=irrigation,
            etc=etc,
            actual_et=actual_et,
            drainage=drainage,
            final_storage=storage,
            depletion=depletion,
            water_deficit=water_deficit
        )