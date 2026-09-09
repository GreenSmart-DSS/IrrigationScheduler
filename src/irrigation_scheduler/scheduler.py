"""Depletion-based irrigation scheduling logic."""

from dataclasses import dataclass

from .models import IrrigationSystem, Soil


@dataclass(frozen=True)
class IrrigationDecision:
    """Result of an irrigation scheduling decision."""
    
    triggered: bool
    depletion: float
    net_irrigation: float
    gross_irrigation: float
    

class IrrigationScheduler:
    """Depletion-based irrigation scheduler."""
    
    def __init__(self, soil: Soil, irrigation_system: IrrigationSystem, mad: float) -> None:
        
        if not 0 < mad < 1:
            raise ValueError("MAD must be between 0 and 1.")
        
        self.soil = soil
        self.irrigation_system = irrigation_system
        self.mad = mad
        
    @property
    def total_available_water(self) -> float:
        """Return total available water (TAW) in the root zone (mm)."""
        
        return self.soil.total_available_water
    
    @property
    def readily_available_water(self) -> float:
        """Return readily available water (RAW) in the root zone (mm)."""
        
        return self.mad * self.total_available_water
    
    def evaluate(self, storage: float) -> IrrigationDecision:
        """Evaluate whether irrigation is required."""
        
        if storage < self.soil.wilting_point:
            raise ValueError("Storage cannot be less than wilting point.")
        
        if storage > self.soil.field_capacity:
            raise ValueError("Storage cannot be greater than field capacity.")
        
        depletion = self.soil.field_capacity - storage
        
        triggered = depletion >= self.readily_available_water
        
        if not triggered:
            return IrrigationDecision(
                triggered=False,
                depletion=depletion,
                net_irrigation=0.0,
                gross_irrigation=0.0
            )
            
        net_irrigation = depletion
        gross_irrigation = net_irrigation / self.irrigation_system.efficiency
        
        return IrrigationDecision(
            triggered=True,
            depletion=depletion,
            net_irrigation=net_irrigation,
            gross_irrigation=gross_irrigation,
        )