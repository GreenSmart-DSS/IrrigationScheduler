import pytest

from irrigation_scheduler.models import Crop


@pytest.fixture
def crop():
    return Crop(
        kc_initial=0.40,
        kc_mid=1.15,
        kc_end=0.80,
        initial_stage_days=20,
        development_stage_days=30,
        mid_stage_days=40,
        late_stage_days=30,
    )


def test_kc_on_initial_stage(crop):
    assert crop.kc_on_day(1) == pytest.approx(0.40)
    assert crop.kc_on_day(20) == pytest.approx(0.40)


def test_kc_increases_during_development(crop):
    assert crop.kc_on_day(21) > 0.40
    assert crop.kc_on_day(35) > crop.kc_on_day(21)
    assert crop.kc_on_day(50) == pytest.approx(1.15)


def test_kc_remains_constant_during_mid_season(crop):
    assert crop.kc_on_day(51) == pytest.approx(1.15)
    assert crop.kc_on_day(70) == pytest.approx(1.15)
    assert crop.kc_on_day(90) == pytest.approx(1.15)


def test_kc_decreases_during_late_season(crop):
    assert crop.kc_on_day(91) < 1.15
    assert crop.kc_on_day(105) < crop.kc_on_day(91)
    assert crop.kc_on_day(120) == pytest.approx(0.80)


def test_kc_is_continuous_at_stage_boundaries(crop):
    assert crop.kc_on_day(20) == pytest.approx(0.40)
    assert crop.kc_on_day(50) == pytest.approx(1.15)
    assert crop.kc_on_day(90) == pytest.approx(1.15)
    assert crop.kc_on_day(120) == pytest.approx(0.80)


def test_kc_rejects_invalid_day(crop):
    with pytest.raises(ValueError):
        crop.kc_on_day(0)

    with pytest.raises(ValueError):
        crop.kc_on_day(121)