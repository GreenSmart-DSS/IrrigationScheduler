import pytest

from irrigation_scheduler.models import Soil
from irrigation_scheduler.water_balance import WaterBalance


@pytest.fixture
def soil():
    return Soil(
        field_capacity=180.0,
        wilting_point=80.0,
        initial_storage=150.0,
    )

@pytest.fixture
def water_balance(soil):
    return WaterBalance(soil)

def test_water_balance_without_inputs(water_balance):
    result = water_balance.step(
        storage=150.0,
        precipitation=0.0,
        irrigation=0.0,
        etc=5.0,
    )
    
    assert result.initial_storage == 150.0
    assert result.final_storage == 145.0
    assert result.actual_et == 5.0
    assert result.drainage == 0.0
    assert result.water_deficit == 0.0
    assert result.depletion == 35.0

def test_water_balance_with_precipitation(water_balance):
    result = water_balance.step(
        storage=150.0,
        precipitation=10.0,
        irrigation=0.0,
        etc=5.0
    )
    assert result.final_storage == 155.0
    assert result.actual_et == 5.0
    assert result.drainage == 0.0


def test_water_balance_with_irrigation(water_balance):
    result = water_balance.step(
        storage=150.0,
        precipitation=0.0,
        irrigation=20.0,
        etc=5.0,
    )

    assert result.final_storage == 165.0
    assert result.actual_et == 5.0
    assert result.drainage == 0.0


def test_excess_water_becomes_drainage(water_balance):
    result = water_balance.step(
        storage=170.0,
        precipitation=20.0,
        irrigation=0.0,
        etc=5.0,
    )

    assert result.drainage == 10.0
    assert result.final_storage == 175.0


def test_storage_cannot_fall_below_wilting_point(water_balance):
    result = water_balance.step(
        storage=85.0,
        precipitation=0.0,
        irrigation=0.0,
        etc=10.0,
    )

    assert result.final_storage == 80.0
    assert result.actual_et == 5.0
    assert result.water_deficit == 5.0
    assert result.depletion == 100.0


def test_zero_etc(water_balance):
    result = water_balance.step(
        storage=150.0,
        precipitation=0.0,
        irrigation=0.0,
        etc=0.0,
    )

    assert result.final_storage == 150.0
    assert result.actual_et == 0.0
    assert result.water_deficit == 0.0


def test_negative_precipitation_is_rejected(water_balance):
    with pytest.raises(ValueError):
        water_balance.step(
            storage=150.0,
            precipitation=-1.0,
            irrigation=0.0,
            etc=5.0,
        )


def test_negative_irrigation_is_rejected(water_balance):
    with pytest.raises(ValueError):
        water_balance.step(
            storage=150.0,
            precipitation=0.0,
            irrigation=-1.0,
            etc=5.0,
        )


def test_negative_etc_is_rejected(water_balance):
    with pytest.raises(ValueError):
        water_balance.step(
            storage=150.0,
            precipitation=0.0,
            irrigation=0.0,
            etc=-1.0,
        )


def test_storage_below_wilting_point_is_rejected(water_balance):
    with pytest.raises(ValueError):
        water_balance.step(
            storage=79.0,
            precipitation=0.0,
            irrigation=0.0,
            etc=5.0,
        )


def test_storage_above_field_capacity_is_rejected(water_balance):
    with pytest.raises(ValueError):
        water_balance.step(
            storage=181.0,
            precipitation=0.0,
            irrigation=0.0,
            etc=5.0,
        )