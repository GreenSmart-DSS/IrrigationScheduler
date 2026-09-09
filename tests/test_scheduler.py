import pytest

from irrigation_scheduler.models import IrrigationSystem, Soil
from irrigation_scheduler.scheduler import IrrigationScheduler


@pytest.fixture
def soil():
    return Soil(
        field_capacity=180.0,
        wilting_point=80.0,
        initial_storage=150.0,
    )


@pytest.fixture
def irrigation_system():
    return IrrigationSystem(efficiency=0.80)


@pytest.fixture
def scheduler(soil, irrigation_system):
    return IrrigationScheduler(
        soil=soil,
        irrigation_system=irrigation_system,
        mad=0.50,
    )


def test_total_available_water(scheduler):
    assert scheduler.total_available_water == pytest.approx(100.0)


def test_readily_available_water(scheduler):
    assert scheduler.readily_available_water == pytest.approx(50.0)


def test_no_irrigation_before_trigger(scheduler):
    decision = scheduler.evaluate(storage=140.0)

    assert decision.triggered is False
    assert decision.depletion == pytest.approx(40.0)
    assert decision.net_irrigation == pytest.approx(0.0)
    assert decision.gross_irrigation == pytest.approx(0.0)


def test_irrigation_trigger(scheduler):
    decision = scheduler.evaluate(storage=125.0)

    assert decision.triggered is True
    assert decision.depletion == pytest.approx(55.0)
    assert decision.net_irrigation == pytest.approx(55.0)
    assert decision.gross_irrigation == pytest.approx(68.75)


def test_trigger_at_exact_raw_threshold(scheduler):
    decision = scheduler.evaluate(storage=130.0)

    assert decision.depletion == pytest.approx(50.0)
    assert decision.triggered is True
    assert decision.net_irrigation == pytest.approx(50.0)


def test_no_irrigation_when_storage_is_at_field_capacity(scheduler):
    decision = scheduler.evaluate(storage=180.0)

    assert decision.triggered is False
    assert decision.depletion == pytest.approx(0.0)
    assert decision.net_irrigation == pytest.approx(0.0)
    assert decision.gross_irrigation == pytest.approx(0.0)


def test_storage_below_wilting_point_is_rejected(scheduler):
    with pytest.raises(ValueError):
        scheduler.evaluate(storage=79.0)


def test_storage_above_field_capacity_is_rejected(scheduler):
    with pytest.raises(ValueError):
        scheduler.evaluate(storage=181.0)


def test_invalid_mad_is_rejected(soil, irrigation_system):
    with pytest.raises(ValueError):
        IrrigationScheduler(
            soil=soil,
            irrigation_system=irrigation_system,
            mad=0.0,
        )

    with pytest.raises(ValueError):
        IrrigationScheduler(
            soil=soil,
            irrigation_system=irrigation_system,
            mad=1.0,
        )

    with pytest.raises(ValueError):
        IrrigationScheduler(
            soil=soil,
            irrigation_system=irrigation_system,
            mad=-0.2,
        )


def test_full_depletion_requires_full_net_refill(soil):
    irrigation_system = IrrigationSystem(efficiency=0.50)

    scheduler = IrrigationScheduler(
        soil=soil,
        irrigation_system=irrigation_system,
        mad=0.50,
    )

    decision = scheduler.evaluate(storage=80.0)

    assert decision.triggered is True
    assert decision.net_irrigation == pytest.approx(100.0)
    assert decision.gross_irrigation == pytest.approx(200.0)