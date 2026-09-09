from datetime import date

import pytest

from irrigation_scheduler.models import Crop, IrrigationSystem, Soil, WeatherDay


def test_soil_creation():
    soil = Soil(field_capacity=180.0, wilting_point=80.0, initial_storage=150.0)
    
    assert soil.field_capacity == 180.0
    assert soil.wilting_point == 80.0
    assert soil.initial_storage == 150.0


def test_soil_total_available_water():
    soil = Soil(field_capacity=200.0, wilting_point=100.0, initial_storage=150.0)
    
    assert soil.total_available_water == 100.0
    

def test_soil_rejects_invalid_water_limits():
    with pytest.raises(ValueError):
        Soil(field_capacity=180.0, wilting_point=80.0, initial_storage=50.0)
        
        
def test_soil_rejects_storage_below_wilting_point():
    with pytest.raises(ValueError):
        Soil(field_capacity=180.0, wilting_point=80.0, initial_storage=70.0)
        

def test_soil_rejects_storage_above_field_capacity():
    with pytest.raises(ValueError):
        Soil(field_capacity=180.0, wilting_point=80.0, initial_storage=190.0)


def test_crop_creation():
    crop = Crop(
        kc_initial=0.3,
        kc_mid=1.2,
        kc_end=0.5,
        initial_stage_days=20,
        development_stage_days=30,
        mid_stage_days=40,
        late_stage_days=30
    )
    
    assert crop.kc_initial == 0.3
    assert crop.kc_mid == 1.2
    assert crop.kc_end == 0.5
    assert crop.initial_stage_days == 20
    assert crop.development_stage_days == 30
    assert crop.mid_stage_days == 40
    assert crop.late_stage_days == 30
    

def test_crop_season_length():
    crop = Crop(
        kc_initial=0.3,
        kc_mid=1.2,
        kc_end=0.5,
        initial_stage_days=20,
        development_stage_days=30,
        mid_stage_days=40,
        late_stage_days=30
    )
    
    assert crop.season_length == 120
    

def test_crop_rejects_negative_kc():
    with pytest.raises(ValueError):
        Crop(
            kc_initial=-0.1,
            kc_mid=1.2,
            kc_end=0.5,
            initial_stage_days=20,
            development_stage_days=30,
            mid_stage_days=40,
            late_stage_days=30
        )
        
def test_crop_rejects_invalid_stage_duration():
    with pytest.raises(ValueError):
        Crop(
            kc_initial=0.3,
            kc_mid=1.2,
            kc_end=0.5,
            initial_stage_days=20,
            development_stage_days=30,
            mid_stage_days=0,
            late_stage_days=30
        )
        

def test_weather_day_creation():
    weather_day = WeatherDay(
        date=date(2024, 6, 1),
        precipitation=5.0,
        eto=4.0
    )
    
    assert weather_day.date == date(2024, 6, 1)
    assert weather_day.precipitation == 5.0
    assert weather_day.eto == 4.0


def test_weather_rejects_negative_eto():
    with pytest.raises(ValueError):
        WeatherDay(
            date=date(2024, 6, 1),
            precipitation=5.0,
            eto=-1.0
        )

def test_weather_rejects_negative_precipitation():
    with pytest.raises(ValueError):
        WeatherDay(
            date=date(2024, 6, 1),
            precipitation=-5.0,
            eto=4.0
        )

def test_irrigation_system_creation():
    system = IrrigationSystem(efficiency=0.90)
    
    assert system.efficiency == 0.90


def test_irrigation_system_default_efficiency():
    system = IrrigationSystem()
    
    assert system.efficiency == 1.0


def test_irrigation_system_rejects_invalid_efficiency():
    with pytest.raises(ValueError):
        IrrigationSystem(efficiency=1.5)
        
    with pytest.raises(ValueError):
        IrrigationSystem(efficiency=0.0)
        
    with pytest.raises(ValueError):
        IrrigationSystem(efficiency=-0.1)
