"""Core data models for IrrigationScheduler.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Soil:
    """Soil water storage properties for the crop root zone.
    
    all water storage values are expressed in mm for the complete root zone.
    """
    
    field_capacity: float
    wilting_point: float
    initial_storage: float
    
    def __post_init__(self) -> None:
        if self.field_capacity <= 0:
            raise ValueError("Field capacity must be greater than zero.")
        
        if self.wilting_point < 0:
            raise ValueError("Wilting point must be greater than or equal to zero.")
        
        if self.field_capacity <= self.wilting_point:
            raise ValueError("Field capacity must be greater than wilting point.")
        
        if not self.wilting_point <= self.initial_storage <= self.field_capacity:
            raise ValueError("Initial storage must be between wilting point and field capacity.")
        
    @property
    def total_available_water(self) -> float:
        """Total available water (TAW) in the root zone."""
        return self.field_capacity - self.wilting_point
    

@dataclass
class Crop:
    """Crop properties required for the initial scheduling model.
    """
    
    kc_initial: float
    kc_mid: float
    kc_end: float
    
    initial_stage_days: int
    development_stage_days: int
    mid_stage_days: int
    late_stage_days: int
    
    def __post_init__(self) -> None:
        kc_values = (self.kc_initial, self.kc_mid, self.kc_end)
        
        if any(kc < 0 for kc in kc_values):
            raise ValueError("All crop coefficients must be greater than or equal to zero.")
        
        stage_lengths = (self.initial_stage_days, self.development_stage_days, self.mid_stage_days, self.late_stage_days)
        
        if any(days <= 0 for days in stage_lengths):
            raise ValueError("All stage lengths must be greater than zero.")
        
    @property
    def season_length(self) -> int:
        """Total length of the crop season in days."""
        return sum((self.initial_stage_days, self.development_stage_days, self.mid_stage_days, self.late_stage_days))
        
@dataclass(frozen=True)
class WeatherDay:
    """Daily wather inputs required by the model.
    """
    
    date: date
    eto: float
    precipitation: float
    
    def __post_init__(self) -> None:
        if self.eto < 0:
            raise ValueError("Reference evapotranspiration (ETo) must be greater than or equal to zero.")
        
        if self.precipitation < 0:
            raise ValueError("Precipitation must be greater than or equal to zero.")
        

@dataclass(frozen=True)
class IrrigationSystem:
    """Irrigation system characteristics.
    """
    
    efficiency: float = 1.0
    
    def __post_init__(self) -> None:
        if not 0 < self.efficiency <= 1:
            raise ValueError("Irrigation system efficiency must be between 0 and 1 (exclusive).")